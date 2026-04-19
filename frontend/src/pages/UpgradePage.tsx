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
  "billing.feature_referrals",
];

export function UpgradePage() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [config, setConfig] = useState<BillingConfig | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [params] = useSearchParams();

  useEffect(() => {
    api.billingConfig().then(setConfig).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    const u = params.get("upgraded");
    if (u === "1") setNotice(t("billing.upgraded_success"));
    if (u === "0") setNotice(t("billing.upgraded_cancel"));
  }, [params, t]);

  async function subscribe() {
    setBusy(true);
    setError(null);
    try {
      const { url } = await api.billingCheckout();
      window.location.assign(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setBusy(false);
    }
  }

  async function openPortal() {
    setBusy(true);
    setError(null);
    try {
      const { url } = await api.billingPortal();
      window.location.assign(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setBusy(false);
    }
  }

  const isPremium = user?.is_premium ?? false;

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="font-display text-3xl">{t("billing.title")}</h1>
        <p className="text-sm text-muted mt-1">{t("billing.subtitle")}</p>
      </div>

      {notice && (
        <div className="rounded-xl border border-wood/40 bg-wood-soft p-3 text-sm">
          {notice}
        </div>
      )}
      {error && <div className="text-fire text-sm">{error}</div>}

      <section className="relative rounded-2xl border border-earth/40 bg-gradient-to-br from-parchment via-white to-earth-soft p-6 sm:p-8 shadow-sm">
        <div className="absolute -top-3 right-4 chip bg-earth text-white shadow-sm">PREMIUM</div>
        <div className="flex items-baseline gap-2">
          <div className="font-display text-5xl">${config?.price_usd?.toFixed(2) ?? "19.00"}</div>
          <div className="text-sm text-muted">/ {t("billing.price_label")}</div>
        </div>

        <ul className="mt-5 space-y-2 text-sm">
          {FEATURE_KEYS.map((k) => (
            <li key={k} className="flex items-start gap-2">
              <span className="text-wood mt-0.5">✓</span>
              <span>{t(k)}</span>
            </li>
          ))}
        </ul>

        <div className="mt-6">
          {isPremium ? (
            <div className="space-y-3">
              <div className="rounded-lg border border-wood/40 bg-wood-soft/60 p-3 text-sm">
                {t("billing.current_premium")}
              </div>
              {user?.stripe_customer_id && (
                <button
                  disabled={busy}
                  onClick={openPortal}
                  className="btn-primary w-full"
                >
                  {busy ? t("billing.opening") : t("billing.manage")}
                </button>
              )}
            </div>
          ) : config && !config.enabled ? (
            <div className="rounded-lg border border-earth/40 bg-earth-soft p-3 text-sm">
              {t("billing.unconfigured")}
            </div>
          ) : (
            <button
              disabled={busy || !config}
              onClick={subscribe}
              className="btn-primary w-full text-base py-3"
            >
              {busy ? t("billing.subscribing") : t("billing.subscribe")}
            </button>
          )}
        </div>
      </section>
    </div>
  );
}
