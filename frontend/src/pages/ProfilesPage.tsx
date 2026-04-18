import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Profile } from "../api";
import { useAuth } from "../auth";
import { useI18n } from "../i18n";

const FREE_LIMIT = 3;

function toDatetimeLocal(iso: string): string {
  // Convert ISO to the YYYY-MM-DDTHH:MM shape <input type="datetime-local"> wants.
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function ProfilesPage() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      setProfiles(await api.listProfiles());
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { refresh(); }, []);

  async function onDelete(id: number) {
    if (!confirm(t("profiles.delete_confirm"))) return;
    await api.deleteProfile(id);
    refresh();
  }

  const atLimit = !user?.is_premium && profiles.length >= FREE_LIMIT;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl">{t("profiles.title")}</h1>
          <div className="text-sm text-muted">
            {profiles.length}{user?.is_premium ? "" : ` / ${FREE_LIMIT}`}
            {!user?.is_premium && atLimit && ` · ${t("profiles.limit_reached")}`}
          </div>
        </div>
        <button
          onClick={() => { setEditing(null); setShowForm((v) => !v); }}
          disabled={atLimit}
          className="btn-primary disabled:opacity-50"
        >
          {showForm && !editing ? t("common.cancel") : t("profiles.new")}
        </button>
      </div>

      {atLimit && (
        <div className="rounded-xl border border-earth/40 bg-earth-soft p-4 text-sm">
          {t("profiles.limit_hint", { limit: FREE_LIMIT })}
        </div>
      )}

      {(showForm && !editing) && (
        <ProfileForm
          mode="create"
          onDone={() => { setShowForm(false); refresh(); }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {editing && (
        <ProfileForm
          mode="edit"
          initial={editing}
          onDone={() => { setEditing(null); refresh(); }}
          onCancel={() => setEditing(null)}
        />
      )}

      {loading ? (
        <div className="text-muted">{t("common.loading")}</div>
      ) : profiles.length === 0 ? (
        <div className="rounded-xl border border-dashed border-ink/20 p-6 text-center text-muted">
          {t("profiles.empty")}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {profiles.map((p) => (
            <div key={p.id} className="rounded-xl border border-ink/10 bg-white p-4 flex flex-col">
              <div className="flex items-start justify-between">
                <div>
                  <Link to={`/profiles/${p.id}`} className="font-display text-lg hover:underline">
                    {p.name}
                  </Link>
                  {p.chinese_name && (
                    <span className="ml-2 font-display text-muted">{p.chinese_name}</span>
                  )}
                  {p.is_main && <span className="ml-2 chip element-fire">{t("profiles.main")}</span>}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => { setShowForm(false); setEditing(p); }}
                    className="text-xs text-muted hover:text-ink underline-offset-2 hover:underline"
                  >
                    {t("profiles.edit")}
                  </button>
                  <button
                    onClick={() => onDelete(p.id)}
                    className="text-xs text-muted hover:text-fire"
                  >
                    {t("profiles.delete")}
                  </button>
                </div>
              </div>
              <div className="text-xs text-muted mt-1">
                {new Date(p.birth_datetime).toLocaleString()}
              </div>
              {p.relationship_label && (
                <div className="text-xs text-muted mt-0.5">{p.relationship_label}</div>
              )}
              <Link to={`/profiles/${p.id}`} className="btn-ghost text-xs mt-3 self-start">
                {t("profiles.view_chart")}
              </Link>
            </div>
          ))}
        </div>
      )}

      {error && <div className="text-fire text-sm">{error}</div>}
    </div>
  );
}

// --- Form: create / edit -------------------------------------------------

type ProfileFormProps = {
  mode: "create" | "edit";
  initial?: Profile;
  onDone: () => void;
  onCancel: () => void;
};

function ProfileForm({ mode, initial, onDone, onCancel }: ProfileFormProps) {
  const { t } = useI18n();

  const [name, setName] = useState(initial?.name ?? "");
  const [chineseName, setChineseName] = useState(initial?.chinese_name ?? "");
  const [birth, setBirth] = useState(
    initial ? toDatetimeLocal(initial.birth_datetime) : "",
  );
  const [label, setLabel] = useState(initial?.relationship_label ?? "");
  const [location, setLocation] = useState(initial?.birth_location ?? "");
  const [gender, setGender] = useState(initial?.gender ?? "");
  const [isMain, setIsMain] = useState(initial?.is_main ?? false);
  const [notes, setNotes] = useState(initial?.notes ?? "");
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
        birth_datetime: new Date(birth).toISOString(),
        relationship_label: label || null,
        birth_location: location || null,
        gender: gender || null,
        is_main: isMain,
        notes: notes || null,
      };
      if (mode === "edit" && initial) {
        await api.updateProfile(initial.id, payload);
      } else {
        await api.createProfile(payload);
      }
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="rounded-xl border border-ink/10 bg-white p-4 space-y-3">
      {mode === "edit" && (
        <div className="text-xs uppercase tracking-wider text-muted">
          {t("profiles.edit_title")}
        </div>
      )}
      <div className="grid sm:grid-cols-2 gap-3">
        <label className="block">
          <span className="text-xs text-muted">{t("profiles.name")}</span>
          <input className="input mt-1" value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("profiles.chinese_name")}</span>
          <input
            className="input mt-1 font-display text-lg"
            value={chineseName}
            onChange={(e) => setChineseName(e.target.value)}
            placeholder={t("profiles.chinese_name_placeholder")}
            maxLength={16}
          />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("profiles.birth_dt")}</span>
          <input type="datetime-local" className="input mt-1" value={birth} onChange={(e) => setBirth(e.target.value)} required />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("profiles.relationship")}</span>
          <input className="input mt-1" value={label} onChange={(e) => setLabel(e.target.value)} />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("profiles.location")}</span>
          <input className="input mt-1" value={location} onChange={(e) => setLocation(e.target.value)} />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("profiles.gender")}</span>
          <select className="input mt-1" value={gender} onChange={(e) => setGender(e.target.value)}>
            <option value="">—</option>
            <option value="female">{t("profiles.gender_female")}</option>
            <option value="male">{t("profiles.gender_male")}</option>
            <option value="other">{t("profiles.gender_other")}</option>
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm mt-6">
          <input type="checkbox" checked={isMain} onChange={(e) => setIsMain(e.target.checked)} />
          {t("profiles.set_main")}
        </label>
      </div>
      <label className="block">
        <span className="text-xs text-muted">{t("profiles.notes")}</span>
        <textarea className="input mt-1" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>
      {error && <div className="text-xs text-fire">{error}</div>}
      <div className="flex gap-2">
        <button type="submit" disabled={busy} className="btn-primary">
          {busy
            ? t("common.saving")
            : mode === "edit"
              ? t("profiles.save_changes")
              : t("profiles.save")}
        </button>
        <button type="button" onClick={onCancel} className="btn-ghost">
          {t("common.cancel")}
        </button>
      </div>
    </form>
  );
}
