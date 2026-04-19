import { useEffect, useState } from "react";
import { api, ReferralSummary } from "../api";
import { useI18n } from "../i18n";

function formatUSD(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export function ReferralsPage() {
  const { t } = useI18n();
  const [data, setData] = useState<ReferralSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    api.myReferrals().then(setData).catch((e) => setError(String(e)));
  }, []);

  async function copy(text: string, key: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(key);
      setTimeout(() => setCopied(null), 1500);
    } catch {
      /* ignore */
    }
  }

  if (error) return <div className="text-fire text-sm">{error}</div>;
  if (!data) return <div className="text-muted">{t("common.loading")}</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl">{t("ref.title")}</h1>
        <p className="text-sm text-muted">{t("ref.subtitle")}</p>
      </div>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted">{t("ref.your_code")}</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="font-display text-4xl tracking-[0.15em]">{data.code}</div>
              <button
                className="btn-ghost text-xs"
                onClick={() => copy(data.code, "code")}
              >
                {copied === "code" ? t("ref.copied") : t("ref.copy")}
              </button>
            </div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted">{t("ref.share_url")}</div>
            <div className="flex items-center gap-2 mt-1">
              <input
                className="input flex-1 text-xs"
                value={data.share_url}
                readOnly
              />
              <button
                className="btn-ghost text-xs"
                onClick={() => copy(data.share_url, "url")}
              >
                {copied === "url" ? t("ref.copied") : t("ref.copy")}
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted">{t("ref.tier_plan")}</div>
            <div className="text-sm mt-1">
              {t("ref.monthly_fee")}: <b>${data.monthly_fee_usd.toFixed(2)}</b>
            </div>
          </div>
        </div>
        <div className="grid sm:grid-cols-3 gap-3 mt-4">
          {data.tier_percents.map((pct, i) => {
            const count =
              i === 0 ? data.downline_tier_counts.tier_1 :
              i === 1 ? data.downline_tier_counts.tier_2 :
              data.downline_tier_counts.tier_3;
            const label = [t("ref.tier_1_label"), t("ref.tier_2_label"), t("ref.tier_3_label")][i];
            const earnPerSub = data.monthly_fee_usd * (pct / 100);
            return (
              <div key={i} className="rounded-xl border border-ink/10 p-4">
                <div className="text-xs text-muted">{label}</div>
                <div className="font-display text-3xl mt-1">{pct}%</div>
                <div className="text-xs text-muted mt-1">
                  = ${earnPerSub.toFixed(2)} / {t("ref.members")}
                </div>
                <div className="mt-2 text-sm">
                  <span className="chip element-wood">{count} {t("ref.members")}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="grid sm:grid-cols-2 gap-4">
        <div className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted">{t("ref.pending")}</div>
          <div className="font-display text-4xl mt-1">{formatUSD(data.pending_cents)}</div>
          <div className="text-xs text-muted mt-1">{data.pending_count} × commission</div>
        </div>
        <div className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted">{t("ref.paid")}</div>
          <div className="font-display text-4xl mt-1">{formatUSD(data.paid_cents)}</div>
          <div className="text-xs text-muted mt-1">{data.paid_count} × commission</div>
        </div>
      </section>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-3">
          {t("ref.direct_referrals")} ({data.direct_referrals.length})
        </div>
        {data.direct_referrals.length === 0 ? (
          <div className="text-sm text-muted">{t("ref.no_referrals")}</div>
        ) : (
          <ul className="divide-y divide-ink/10">
            {data.direct_referrals.map((u) => (
              <li key={u.id} className="py-2 flex items-center justify-between">
                <div>
                  <div className="text-sm">{u.display_name || u.email}</div>
                  <div className="text-xs text-muted">{new Date(u.created_at).toLocaleDateString()}</div>
                </div>
                {u.is_premium
                  ? <span className="chip element-wood">{t("ref.paid_status")}</span>
                  : <span className="chip element-metal">{t("ref.unpaid_status")}</span>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
