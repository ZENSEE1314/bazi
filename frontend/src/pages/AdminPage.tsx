import { useEffect, useState } from "react";
import { AdminUser, api, Commission } from "../api";
import { useI18n } from "../i18n";

function fmtUSD(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString();
}

export function AdminPage() {
  const { t } = useI18n();
  const [tab, setTab] = useState<"users" | "commissions">("users");

  return (
    <div className="space-y-4">
      <div>
        <h1 className="font-display text-2xl">{t("admin.title")}</h1>
      </div>
      <div className="flex gap-2">
        <button
          className={`px-3 py-1.5 rounded-lg text-sm ${tab === "users" ? "bg-ink text-parchment" : "bg-ink/5 hover:bg-ink/10"}`}
          onClick={() => setTab("users")}
        >
          {t("admin.users_tab")}
        </button>
        <button
          className={`px-3 py-1.5 rounded-lg text-sm ${tab === "commissions" ? "bg-ink text-parchment" : "bg-ink/5 hover:bg-ink/10"}`}
          onClick={() => setTab("commissions")}
        >
          {t("admin.commissions_tab")}
        </button>
      </div>

      {tab === "users" ? <UsersTab /> : <CommissionsTab />}
    </div>
  );
}

function UsersTab() {
  const { t } = useI18n();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh(search?: string) {
    setLoading(true);
    try {
      setUsers(await api.adminListUsers(search || undefined));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { refresh(); }, []);

  async function doAction(fn: () => Promise<any>) {
    try {
      await fn();
      refresh(q);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2 flex-wrap">
        <input
          className="input flex-1 min-w-[260px]"
          placeholder={t("admin.search")}
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button onClick={() => refresh(q)} className="btn-primary">
          {t("admin.search").replace("…", "")}
        </button>
      </div>

      {error && <div className="text-fire text-sm">{error}</div>}
      {loading ? (
        <div className="text-muted">{t("common.loading")}</div>
      ) : (
        <div className="rounded-2xl border border-ink/10 bg-white overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs uppercase text-muted border-b border-ink/10">
                <th className="text-left p-3">{t("admin.email")}</th>
                <th className="text-left p-3">{t("admin.status")}</th>
                <th className="text-left p-3">{t("admin.ref_code")}</th>
                <th className="text-left p-3">{t("admin.joined")}</th>
                <th className="text-left p-3">{t("admin.earnings")}</th>
                <th className="text-left p-3">{t("admin.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-ink/5 align-top">
                  <td className="p-3">
                    <div className="font-medium">{u.email}</div>
                    {u.display_name && <div className="text-xs text-muted">{u.display_name}</div>}
                    <div className="text-[10px] text-muted">#{u.id}</div>
                  </td>
                  <td className="p-3 space-y-1">
                    {u.is_premium
                      ? <span className="chip element-wood">{t("admin.paid_label")}</span>
                      : <span className="chip element-metal">{t("admin.unpaid_label")}</span>}
                    {!u.is_active && <span className="chip element-fire ml-1">{t("admin.banned_label")}</span>}
                    {u.is_admin && <span className="chip element-earth ml-1">{t("admin.admin_label")}</span>}
                  </td>
                  <td className="p-3 font-mono text-xs">{u.referral_code || "—"}</td>
                  <td className="p-3 text-xs text-muted">{fmtDate(u.created_at)}</td>
                  <td className="p-3 text-xs">
                    <div><span className="text-muted">{t("ref.pending")}:</span> {fmtUSD(u.total_pending_cents)}</div>
                    <div><span className="text-muted">{t("ref.paid")}:</span> {fmtUSD(u.total_paid_cents)}</div>
                  </td>
                  <td className="p-3">
                    <div className="flex flex-wrap gap-1">
                      {u.is_premium ? (
                        <button
                          className="btn-ghost text-xs"
                          onClick={() => doAction(() => api.adminUnsetPremium(u.id))}
                        >
                          {t("admin.make_unpaid")}
                        </button>
                      ) : (
                        <button
                          className="btn-primary text-xs py-1"
                          onClick={() => {
                            if (!confirm(t("admin.confirm_mark_paid"))) return;
                            doAction(() => api.adminSetPremium(u.id));
                          }}
                        >
                          {t("admin.make_paid")}
                        </button>
                      )}
                      {u.is_active ? (
                        <button
                          className="btn-ghost text-xs text-fire"
                          onClick={() => {
                            if (!confirm(t("admin.confirm_ban"))) return;
                            doAction(() => api.adminBan(u.id));
                          }}
                        >
                          {t("admin.ban")}
                        </button>
                      ) : (
                        <button
                          className="btn-ghost text-xs text-wood"
                          onClick={() => doAction(() => api.adminUnban(u.id))}
                        >
                          {t("admin.unban")}
                        </button>
                      )}
                      {u.is_admin ? (
                        <button
                          className="btn-ghost text-xs"
                          onClick={() => doAction(() => api.adminUnmakeAdmin(u.id))}
                        >
                          {t("admin.revoke_admin")}
                        </button>
                      ) : (
                        <button
                          className="btn-ghost text-xs"
                          onClick={() => doAction(() => api.adminMakeAdmin(u.id))}
                        >
                          {t("admin.make_admin")}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function CommissionsTab() {
  const { t } = useI18n();
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [filter, setFilter] = useState<"all" | "pending" | "paid">("pending");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      setCommissions(await api.adminListCommissions({
        status: filter === "all" ? undefined : filter,
      }));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { refresh(); }, [filter]);

  async function markPaid(id: number) {
    try {
      await api.adminMarkCommissionPaid(id);
      refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }
  async function payAll() {
    if (!confirm(t("admin.pay_all_confirm"))) return;
    try {
      await api.adminPayAllPending();
      refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  const totalPending = commissions
    .filter((c) => c.status === "pending")
    .reduce((s, c) => s + c.amount_cents, 0);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex gap-1">
          {(["all", "pending", "paid"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm ${filter === f ? "bg-ink text-parchment" : "bg-ink/5 hover:bg-ink/10"}`}
            >
              {t(`admin.filter_${f}`)}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted">
            {t("ref.pending")}: <b>{fmtUSD(totalPending)}</b>
          </span>
          <button onClick={payAll} className="btn-primary text-xs">
            {t("admin.pay_all")}
          </button>
        </div>
      </div>

      {error && <div className="text-fire text-sm">{error}</div>}
      {loading ? (
        <div className="text-muted">{t("common.loading")}</div>
      ) : (
        <div className="rounded-2xl border border-ink/10 bg-white overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs uppercase text-muted border-b border-ink/10">
                <th className="text-left p-3">{t("admin.period")}</th>
                <th className="text-left p-3">{t("admin.tier_col")}</th>
                <th className="text-left p-3">{t("admin.earner")}</th>
                <th className="text-left p-3">{t("admin.payer")}</th>
                <th className="text-left p-3">{t("admin.amount")}</th>
                <th className="text-left p-3">{t("admin.status")}</th>
                <th className="text-left p-3">{t("admin.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {commissions.map((c) => (
                <tr key={c.id} className="border-b border-ink/5">
                  <td className="p-3 font-mono text-xs">{c.period_month}</td>
                  <td className="p-3">
                    <span className="chip element-earth">T{c.tier}</span>
                  </td>
                  <td className="p-3 text-xs">#{c.earner_user_id}</td>
                  <td className="p-3 text-xs">#{c.payer_user_id}</td>
                  <td className="p-3 font-medium">{fmtUSD(c.amount_cents)}</td>
                  <td className="p-3">
                    {c.status === "paid"
                      ? <span className="chip element-wood">{t("ref.paid")}</span>
                      : <span className="chip element-metal">{t("ref.pending")}</span>}
                  </td>
                  <td className="p-3">
                    {c.status === "pending" && (
                      <button
                        onClick={() => markPaid(c.id)}
                        className="btn-ghost text-xs"
                      >
                        {t("admin.mark_paid_action")}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
