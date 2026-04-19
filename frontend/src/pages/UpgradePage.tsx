import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, BillingConfig } from "../api";
import { useAuth } from "../auth";
import { useI18n } from "../i18n";

const FEATURE_KEYS = [
  "billing.feature_profiles",
  "billing.feature_calendar",
  "billing.feature_numerology",
  "billing.feature_name",
  "billing.feature_fengshui",
  "billing.feature_compat",
  "billing.feature_chat",
  "billing.feature_face_palm",
  "billing.feature_referrals",
];

export function UpgradePage() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [config, setConfig] = useState<BillingConfig | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [creditQty, setCreditQty] = useState(1);
  const [slotQty, setSlotQty] = useState(1);
  const [params] = useSearchParams();

  useEffect(() => {
    api.billingConfig().then(setConfig).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    const u = params.get("purchased") ?? params.get("upgraded");
    if (u === "1") setNotice(t("billing.upgraded_success"));
    if (u === "0") setNotice(t("billing.upgraded_cancel"));
  }, [params, t]);

  async function go(
    key: string,
    fn: () => Promise<{ url: string }>,
  ) {
    setBusy(key);
    setError(null);
    try {
      const { url } = await fn();
      window.location.assign(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setBusy(null);
    }
  }

  const isPremium = user?.is_premium ?? false;
  const credits = user?.feature_credits ?? 0;
  const slots = user?.extra_profile_slots ?? 0;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="font-display text-3xl">{t("billing.title")}</h1>
        <p className="text-sm text-muted mt-1">{t("billing.subtitle")}</p>
      </div>

      {(credits > 0 || slots > 0 || isPremium) && (
        <div className="rounded-xl border border-wood/40 bg-wood-soft/60 p-4 text-sm flex gap-6 flex-wrap">
          {isPremium && (
            <div>
              <span className="chip bg-earth text-white mr-2">{t("common.premium")}</span>
              {t("billing.current_premium")}
            </div>
          )}
          {credits > 0 && (
            <div>
              <b>{credits}</b> {t("billing.credits_on_hand")}
            </div>
          )}
          {slots > 0 && (
            <div>
              <b>{slots}</b> {t("billing.slots_on_hand")}
            </div>
          )}
        </div>
      )}

      {notice && (
        <div className="rounded-xl border border-wood/40 bg-wood-soft p-3 text-sm">
          {notice}
        </div>
      )}
      {error && <div className="text-fire text-sm">{error}</div>}
      {config && !config.enabled && (
        <div className="rounded-lg border border-earth/40 bg-earth-soft p-3 text-sm">
          {t("billing.unconfigured")}
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-4">
        {/* Unlimited monthly */}
        <section className="relative rounded-2xl border-2 border-earth/50 bg-gradient-to-br from-parchment via-white to-earth-soft p-6 shadow-sm flex flex-col">
          <div className="absolute -top-3 right-4 chip bg-earth text-white shadow-sm">
            {t("billing.best_value")}
          </div>
          <div className="text-xs uppercase tracking-wider text-muted">
            {t("billing.plan_monthly")}
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <div className="font-display text-4xl">
              ${config?.monthly?.price_usd?.toFixed(0) ?? "88"}
            </div>
            <div className="text-sm text-muted">/ {t("billing.per_month")}</div>
          </div>
          <p className="text-xs text-muted mt-1">{t("billing.plan_monthly_sub")}</p>
          <ul className="mt-4 space-y-1.5 text-xs flex-1">
            {FEATURE_KEYS.map((k) => (
              <li key={k} className="flex items-start gap-2">
                <span className="text-wood mt-0.5">✓</span>
                <span>{t(k)}</span>
              </li>
            ))}
          </ul>
          <div className="mt-5">
            {isPremium ? (
              user?.stripe_customer_id ? (
                <button
                  disabled={!!busy}
                  onClick={() => go("portal", () => api.billingPortal())}
                  className="btn-primary w-full"
                >
                  {busy === "portal" ? t("billing.opening") : t("billing.manage")}
                </button>
              ) : (
                <div className="text-xs text-muted">{t("billing.current_premium")}</div>
              )
            ) : (
              <button
                disabled={!!busy || !config?.monthly?.available}
                onClick={() => go("sub", () => api.billingCheckout())}
                className="btn-primary w-full"
              >
                {busy === "sub" ? t("billing.subscribing") : t("billing.subscribe")}
              </button>
            )}
          </div>
        </section>

        {/* Per-use credit */}
        <section className="rounded-2xl border border-ink/15 bg-white p-6 flex flex-col">
          <div className="text-xs uppercase tracking-wider text-muted">
            {t("billing.plan_credit")}
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <div className="font-display text-4xl">
              ${config?.credit?.price_usd?.toFixed(0) ?? "8"}
            </div>
            <div className="text-sm text-muted">/ {t("billing.per_use")}</div>
          </div>
          <p className="text-xs text-muted mt-1">{t("billing.plan_credit_sub")}</p>
          <ul className="mt-4 space-y-1.5 text-xs flex-1">
            <li className="flex items-start gap-2"><span className="text-wood mt-0.5">✓</span><span>{t("billing.credit_f1")}</span></li>
            <li className="flex items-start gap-2"><span className="text-wood mt-0.5">✓</span><span>{t("billing.credit_f2")}</span></li>
            <li className="flex items-start gap-2"><span className="text-wood mt-0.5">✓</span><span>{t("billing.credit_f3")}</span></li>
          </ul>
          <div className="mt-5 space-y-2">
            <label className="block">
              <span className="text-xs text-muted">{t("billing.quantity")}</span>
              <input
                type="number"
                min={1}
                max={20}
                className="input mt-1"
                value={creditQty}
                onChange={(e) => setCreditQty(Math.max(1, Math.min(20, Number(e.target.value) || 1)))}
              />
            </label>
            <button
              disabled={!!busy || !config?.credit?.available}
              onClick={() => go("credit", () => api.billingBuyCredit(creditQty))}
              className="btn-primary w-full"
            >
              {busy === "credit"
                ? t("billing.redirecting")
                : t("billing.buy_credits_for").replace(
                    "{amount}",
                    `$${((config?.credit?.price_cents ?? 800) * creditQty / 100).toFixed(2)}`,
                  )}
            </button>
          </div>
        </section>

        {/* Profile slot */}
        <section className="rounded-2xl border border-ink/15 bg-white p-6 flex flex-col">
          <div className="text-xs uppercase tracking-wider text-muted">
            {t("billing.plan_slot")}
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <div className="font-display text-4xl">
              ${config?.profile_slot?.price_usd?.toFixed(0) ?? "16"}
            </div>
            <div className="text-sm text-muted">/ {t("billing.per_slot")}</div>
          </div>
          <p className="text-xs text-muted mt-1">{t("billing.plan_slot_sub")}</p>
          <ul className="mt-4 space-y-1.5 text-xs flex-1">
            <li className="flex items-start gap-2"><span className="text-wood mt-0.5">✓</span><span>{t("billing.slot_f1")}</span></li>
            <li className="flex items-start gap-2"><span className="text-wood mt-0.5">✓</span><span>{t("billing.slot_f2")}</span></li>
            <li className="flex items-start gap-2"><span className="text-wood mt-0.5">✓</span><span>{t("billing.slot_f3")}</span></li>
          </ul>
          <div className="mt-5 space-y-2">
            <label className="block">
              <span className="text-xs text-muted">{t("billing.quantity")}</span>
              <input
                type="number"
                min={1}
                max={10}
                className="input mt-1"
                value={slotQty}
                onChange={(e) => setSlotQty(Math.max(1, Math.min(10, Number(e.target.value) || 1)))}
              />
            </label>
            <button
              disabled={!!busy || !config?.profile_slot?.available}
              onClick={() => go("slot", () => api.billingBuyProfileSlot(slotQty))}
              className="btn-primary w-full"
            >
              {busy === "slot"
                ? t("billing.redirecting")
                : t("billing.buy_slots_for").replace(
                    "{amount}",
                    `$${((config?.profile_slot?.price_cents ?? 1600) * slotQty / 100).toFixed(2)}`,
                  )}
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
