"""Stripe billing: checkout, customer portal, and webhook handling.

Required env vars:
    STRIPE_SECRET_KEY        sk_test_... or sk_live_...
    STRIPE_PUBLISHABLE_KEY   pk_test_... or pk_live_... (exposed to frontend)
    STRIPE_WEBHOOK_SECRET    whsec_...  (signs events)
    STRIPE_PRICE_ID          price_...  (the $19/mo recurring Price)

Optional:
    STRIPE_SUCCESS_PATH      default '/referrals?upgraded=1'
    STRIPE_CANCEL_PATH       default '/referrals?upgraded=0'
    PUBLIC_BASE_URL          base URL used to build return URLs
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import get_current_user
from ..models import SubscriptionPayment, User
from ..referral import MONTHLY_FEE_CENTS, record_payment_and_commissions

router = APIRouter(prefix="/api/billing", tags=["billing"])


def _settings():
    return get_settings()


def _stripe_enabled() -> bool:
    s = _settings()
    return bool(s.stripe_secret_key and s.stripe_price_id)


def _init_stripe() -> None:
    s = _settings()
    if not s.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY and STRIPE_PRICE_ID.",
        )
    stripe.api_key = s.stripe_secret_key


def _public_base(request: Request) -> str:
    s = _settings()
    if s.public_base_url:
        return s.public_base_url.rstrip("/")
    # Fall back to the request's own origin.
    return f"{request.url.scheme}://{request.url.netloc}"


@router.get("/config")
def billing_config() -> dict:
    """What the frontend needs to render the Upgrade page."""
    s = _settings()
    return {
        "enabled": _stripe_enabled(),
        "publishable_key": s.stripe_publishable_key or None,
        "price_cents": MONTHLY_FEE_CENTS,
        "price_usd": MONTHLY_FEE_CENTS / 100,
        "price_id": s.stripe_price_id or None,
        "interval": "month",
    }


@router.post("/checkout")
def create_checkout_session(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Create a Stripe Checkout session for the current user and return its URL."""
    _init_stripe()
    s = _settings()

    # Reuse existing Stripe customer if we have one, otherwise create one.
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.display_name or None,
            metadata={"app_user_id": str(user.id), "referral_code": user.referral_code or ""},
        )
        user.stripe_customer_id = customer["id"]
        db.commit()
        db.refresh(user)

    base = _public_base(request)
    success_url = f"{base}{s.stripe_success_path}&session={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base}{s.stripe_cancel_path}"

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=user.stripe_customer_id,
        line_items=[{"price": s.stripe_price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        allow_promotion_codes=True,
        client_reference_id=str(user.id),
        subscription_data={
            "metadata": {"app_user_id": str(user.id)},
        },
        metadata={"app_user_id": str(user.id)},
    )
    return {"url": session["url"], "id": session["id"]}


@router.post("/portal")
def create_portal_session(
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Stripe-hosted customer portal for managing / cancelling their subscription."""
    _init_stripe()
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer on file.")
    base = _public_base(request)
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{base}/referrals",
    )
    return {"url": session["url"]}


# --- Webhook -------------------------------------------------------------

def _find_user_by_customer(db: Session, customer_id: str) -> User | None:
    return db.query(User).filter(User.stripe_customer_id == customer_id).first()


def _period_from_invoice(invoice: dict[str, Any]) -> str:
    """YYYY-MM from invoice.period_end (epoch seconds)."""
    ts = invoice.get("period_end") or invoice.get("status_transitions", {}).get("finalized_at")
    if not ts:
        ts = datetime.utcnow().timestamp()
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m")


def _handle_invoice_paid(db: Session, invoice: dict[str, Any]) -> None:
    customer_id = invoice.get("customer")
    if not customer_id:
        return
    user = _find_user_by_customer(db, customer_id)
    if user is None:
        return

    amount = invoice.get("amount_paid") or invoice.get("amount_due") or MONTHLY_FEE_CENTS
    period = _period_from_invoice(invoice)
    invoice_id = invoice.get("id") or ""

    # Idempotency: if we've already stored this invoice, do nothing.
    existing = (
        db.query(SubscriptionPayment)
        .filter(SubscriptionPayment.stripe_invoice_id == invoice_id)
        .first()
    )
    if existing is None and invoice_id:
        payment = record_payment_and_commissions(
            db, user, period_month=period, amount_cents=amount, note="stripe:invoice.paid"
        )
        payment.stripe_invoice_id = invoice_id
    user.is_premium = True
    sub_id = invoice.get("subscription")
    if sub_id:
        user.stripe_subscription_id = sub_id
    db.commit()


def _handle_subscription_deleted(db: Session, subscription: dict[str, Any]) -> None:
    customer_id = subscription.get("customer")
    if not customer_id:
        return
    user = _find_user_by_customer(db, customer_id)
    if user is None:
        return
    user.is_premium = False
    db.commit()


def _handle_checkout_completed(db: Session, session_obj: dict[str, Any]) -> None:
    """When Checkout completes, remember the subscription id on the user."""
    customer_id = session_obj.get("customer")
    subscription_id = session_obj.get("subscription")
    user_id_raw = session_obj.get("client_reference_id") or (session_obj.get("metadata") or {}).get("app_user_id")
    if not customer_id:
        return
    user = _find_user_by_customer(db, customer_id)
    if user is None and user_id_raw:
        try:
            user = db.get(User, int(user_id_raw))
        except (TypeError, ValueError):
            user = None
        if user is not None:
            user.stripe_customer_id = customer_id
    if user is None:
        return
    if subscription_id:
        user.stripe_subscription_id = subscription_id
    db.commit()


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    stripe_signature: str = Header(default=None, alias="Stripe-Signature"),
) -> dict:
    """Stripe webhook receiver. Signature-verified with STRIPE_WEBHOOK_SECRET."""
    s = _settings()
    if not s.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured.")
    stripe.api_key = s.stripe_secret_key

    payload = await request.body()

    if s.stripe_webhook_secret:
        try:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=stripe_signature, secret=s.stripe_webhook_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError) as exc:
            raise HTTPException(status_code=400, detail=f"Invalid webhook: {exc}")
    else:
        # Unsigned path — allowed only for local testing; log & parse directly.
        event = json.loads(payload.decode("utf-8"))

    event_type = event.get("type") or event["type"]
    data_object = (event.get("data") or {}).get("object") or {}

    if event_type == "invoice.paid":
        _handle_invoice_paid(db, data_object)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(db, data_object)
    elif event_type == "checkout.session.completed":
        _handle_checkout_completed(db, data_object)

    return {"received": True, "type": event_type}
