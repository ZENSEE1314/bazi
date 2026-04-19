import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Business } from "../api";
import { useAuth } from "../auth";
import { useI18n } from "../i18n";

const DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] as const;

function toDTLocal(iso: string): string {
  // Treat the server value as local/naive — do NOT shift by browser timezone.
  const clean = iso.replace(/(\.\d+)?Z$/, "").replace(/[+-]\d{2}:?\d{2}$/, "");
  return clean.length >= 16 ? clean.slice(0, 16) : clean;
}

function fromDTLocal(v: string): string {
  return v.length === 16 ? `${v}:00` : v;
}

export function BusinessesPage() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Business | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      setBusinesses(await api.listBusinesses());
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { refresh(); }, []);

  async function onDelete(id: number) {
    if (!confirm(t("profiles.delete_confirm"))) return;
    await api.deleteBusiness(id);
    refresh();
  }

  const atLimit = !user?.is_premium && businesses.length >= 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl">{t("biz.title")}</h1>
          <div className="text-sm text-muted">
            {businesses.length}{user?.is_premium ? "" : ` / 1`}
            {atLimit ? ` · ${t("biz.limit_hit")}` : ""}
          </div>
        </div>
        <button
          onClick={() => { setEditing(null); setShowForm((v) => !v); }}
          disabled={atLimit}
          className="btn-primary disabled:opacity-50"
        >
          {showForm && !editing ? t("common.cancel") : t("biz.new")}
        </button>
      </div>

      {showForm && !editing && (
        <BusinessForm mode="create" onDone={() => { setShowForm(false); refresh(); }} onCancel={() => setShowForm(false)} />
      )}
      {editing && (
        <BusinessForm key={editing.id} mode="edit" initial={editing} onDone={() => { setEditing(null); refresh(); }} onCancel={() => setEditing(null)} />
      )}

      {loading ? (
        <div className="text-muted">{t("common.loading")}</div>
      ) : businesses.length === 0 ? (
        <div className="rounded-xl border border-dashed border-ink/20 p-6 text-center text-muted">
          {t("biz.empty")}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-3">
          {businesses.map((b) => (
            <div key={b.id} className="rounded-xl border border-ink/10 bg-white p-4 flex flex-col">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <Link to={`/businesses/${b.id}`} className="font-display text-lg hover:underline">
                    {b.name}
                  </Link>
                  {b.chinese_name && <span className="ml-2 font-display text-muted">{b.chinese_name}</span>}
                  {b.is_main && <span className="ml-2 chip element-fire">{t("profiles.main")}</span>}
                </div>
                <div className="flex gap-2 text-xs">
                  <button onClick={() => { setShowForm(false); setEditing(b); }} className="text-muted hover:text-ink underline-offset-2 hover:underline">
                    {t("biz.edit")}
                  </button>
                  <button onClick={() => onDelete(b.id)} className="text-muted hover:text-fire">
                    {t("biz.delete")}
                  </button>
                </div>
              </div>
              <div className="text-xs text-muted mt-1">
                {t("biz.opened_on")}: {new Date(b.open_datetime).toLocaleString()}
              </div>
              {b.location && <div className="text-xs text-muted mt-0.5">{b.location}</div>}
              {b.industry && <div className="text-xs text-muted mt-0.5">{b.industry}</div>}
              <Link to={`/businesses/${b.id}`} className="btn-ghost text-xs mt-3 self-start">
                {t("biz.view")}
              </Link>
            </div>
          ))}
        </div>
      )}

      {error && <div className="text-fire text-sm">{error}</div>}
    </div>
  );
}

type FormProps = {
  mode: "create" | "edit";
  initial?: Business;
  onDone: () => void;
  onCancel: () => void;
};

function BusinessForm({ mode, initial, onDone, onCancel }: FormProps) {
  const { t } = useI18n();
  const [name, setName] = useState(initial?.name ?? "");
  const [chineseName, setChineseName] = useState(initial?.chinese_name ?? "");
  const [openDt, setOpenDt] = useState(initial ? toDTLocal(initial.open_datetime) : "");
  const [location, setLocation] = useState(initial?.location ?? "");
  const [facing, setFacing] = useState(initial?.facing_direction ?? "");
  const [industry, setIndustry] = useState(initial?.industry ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [isMain, setIsMain] = useState(initial?.is_main ?? false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const payload = {
        name,
        chinese_name: chineseName || null,
        open_datetime: fromDTLocal(openDt),
        location: location || null,
        facing_direction: facing || null,
        industry: industry || null,
        notes: notes || null,
        is_main: isMain,
      };
      if (mode === "edit" && initial) {
        await api.updateBusiness(initial.id, payload);
      } else {
        await api.createBusiness(payload);
      }
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="rounded-xl border border-ink/10 bg-white p-4 space-y-3">
      <div className="grid sm:grid-cols-2 gap-3">
        <label className="block">
          <span className="text-xs text-muted">{t("biz.name")}</span>
          <input className="input mt-1" value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("biz.chinese_name")}</span>
          <input className="input mt-1 font-display text-lg" value={chineseName} onChange={(e) => setChineseName(e.target.value)} maxLength={16} />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("biz.open_dt")}</span>
          <input type="datetime-local" className="input mt-1" value={openDt} onChange={(e) => setOpenDt(e.target.value)} required />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("biz.location")}</span>
          <input className="input mt-1" value={location} onChange={(e) => setLocation(e.target.value)} />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("biz.facing")}</span>
          <select className="input mt-1" value={facing} onChange={(e) => setFacing(e.target.value)}>
            <option value="">—</option>
            {DIRECTIONS.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("biz.industry")}</span>
          <input className="input mt-1" value={industry} onChange={(e) => setIndustry(e.target.value)} placeholder={t("biz.industry_ph")} />
        </label>
        <label className="flex items-center gap-2 text-sm mt-6">
          <input type="checkbox" checked={isMain} onChange={(e) => setIsMain(e.target.checked)} />
          {t("biz.set_main")}
        </label>
      </div>
      <label className="block">
        <span className="text-xs text-muted">{t("profiles.notes")}</span>
        <textarea className="input mt-1" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>
      {error && <div className="text-xs text-fire">{error}</div>}
      <div className="flex gap-2">
        <button type="submit" disabled={busy} className="btn-primary">
          {busy ? t("common.saving") : mode === "edit" ? t("profiles.save_changes") : t("profiles.save")}
        </button>
        <button type="button" onClick={onCancel} className="btn-ghost">{t("common.cancel")}</button>
      </div>
    </form>
  );
}
