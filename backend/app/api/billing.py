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
        # Unlimited monthly plan
        "monthly": {
            "price_cents": s.monthly_unlimited_cents,
            "price_usd": s.monthly_unlimited_cents / 100,
            "price_id": s.stripe_price_id or None,
            "available": bool(s.stripe_price_id),
        },
        # One-off feature credit
        "credit": {
            "price_cents": s.feature_credit_cents,
            "price_usd": s.feature_credit_cents / 100,
            "price_id": s.stripe_price_id_credit or None,
            "available": bool(s.stripe_price_id_credit),
        },
        # One-off extra profile slot
        "profile_slot": {
            "price_cents": s.profile_slot_cents,
            "price_usd": s.profile_slot_cents / 100,
            "price_id": s.stripe_price_id_profile_slot or None,
            "available": bool(s.stripe_price_id_profile_slot),
        },
        # Legacy shape kept for any existing frontend still reading it:
        "price_cents": s.monthly_unlimited_cents,
        "price_usd": s.monthly_unlimited_cents / 100,
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


def _ensure_stripe_customer(db: Session, user: User) -> str:
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(
        email=user.email,
        name=user.display_name or None,
        metadata={
            "app_user_id": str(user.id),
            "referral_code": user.referral_code or "",
        },
    )
    user.stripe_customer_id = customer["id"]
    db.commit()
    db.refresh(user)
    return user.stripe_customer_id


def _one_shot_checkout(
    request: Request,
    db: Session,
    user: User,
    price_id: str,
    quantity: int,
    purchase_type: str,
) -> dict:
    """Create a one-time Stripe Checkout session that grants credits/slots
    to ``user`` on successful webhook receipt."""
    _init_stripe()
    s = _settings()
    customer = _ensure_stripe_customer(db, user)
    base = _public_base(request)
    success_url = f"{base}{s.stripe_success_path}&session={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base}{s.stripe_cancel_path}"
    session = stripe.checkout.Session.create(
        mode="payment",
        customer=customer,
        line_items=[{"price": price_id, "quantity": quantity}],
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=str(user.id),
        metadata={
            "app_user_id": str(user.id),
            "purchase_type": purchase_type,
            "quantity": str(quantity),
        },
        payment_intent_data={
            "metadata": {
                "app_user_id": str(user.id),
                "purchase_type": purchase_type,
                "quantity": str(quantity),
            },
        },
    )
    return {"url": session["url"], "id": session["id"]}


@router.post("/checkout/credit")
def checkout_credit(
    request: Request,
    quantity: int = 1,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Buy N feature credits at $8 each. 1 credit = 1 additional feature use."""
    s = _settings()
    if not s.stripe_price_id_credit:
        raise HTTPException(
            status_code=503,
            detail="Per-use credit purchases are not configured.",
        )
    if quantity < 1 or quantity > 20:
        raise HTTPException(status_code=400, detail="Quantity must be between 1 and 20.")
    return _one_shot_checkout(
        request, db, user,
        price_id=s.stripe_price_id_credit,
        quantity=quantity,
        purchase_type="feature_credit",
    )


@router.post("/checkout/profile_slot")
def checkout_profile_slot(
    request: Request,
    quantity: int = 1,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Buy N extra profile slots at $16 each. Each slot raises the permanent
    profile cap by 1."""
    s = _settings()
    if not s.stripe_price_id_profile_slot:
        raise HTTPException(
            status_code=503,
            detail="Profile-slot purchases are not configured.",
        )
    if quantity < 1 or quantity > 10:
        raise HTTPException(status_code=400, detail="Quantity must be between 1 and 10.")
    return _one_shot_checkout(
        request, db, user,
        price_id=s.stripe_price_id_profile_slot,
        quantity=quantity,
        purchase_type="profile_slot",
    )


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
    """When Checkout completes, remember the subscription id OR grant credits
    / slots depending on the purchase type carried in session metadata."""
    customer_id = session_obj.get("customer")
    subscription_id = session_obj.get("subscription")
    metadata = session_obj.get("metadata") or {}
    user_id_raw = session_obj.get("client_reference_id") or metadata.get("app_user_id")

    user: User | None = None
    if customer_id:
        user = _find_user_by_customer(db, customer_id)
    if user is None and user_id_raw:
        try:
            user = db.get(User, int(user_id_raw))
        except (TypeError, ValueError):
            user = None
        if user is not None and customer_id:
            user.stripe_customer_id = customer_id
    if user is None:
        return

    mode = session_obj.get("mode")
    purchase_type = metadata.get("purchase_type")
    amount_paid = session_obj.get("amount_total") or session_obj.get("amount_subtotal") or 0

    if mode == "subscription":
        if subscription_id:
            user.stripe_subscription_id = subscription_id
    elif mode == "payment" and purchase_type in ("feature_credit", "profile_slot"):
        qty_raw = metadata.get("quantity") or "1"
        try:
            qty = max(1, int(qty_raw))
        except ValueError:
            qty = 1
        if purchase_type == "feature_credit":
            user.feature_credits = (user.feature_credits or 0) + qty
        elif purchase_type == "profile_slot":
            user.extra_profile_slots = (user.extra_profile_slots or 0) + qty

        # Pay referral commissions on the one-off too.
        if amount_paid and user.id:
            period = datetime.now(tz=timezone.utc).strftime("%Y-%m")
            try:
                record_payment_and_commissions(
                    db, user, period_month=period,
                    amount_cents=int(amount_paid),
                    note=f"stripe:{purchase_type}:{qty}",
                )
            except Exception:
                pass
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
