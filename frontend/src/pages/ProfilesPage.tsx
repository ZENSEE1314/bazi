import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Profile } from "../api";
import { useAuth } from "../auth";

const FREE_LIMIT = 3;

export function ProfilesPage() {
  const { user } = useAuth();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
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

  useEffect(() => {
    refresh();
  }, []);

  async function onDelete(id: number) {
    if (!confirm("Delete this profile? This cannot be undone.")) return;
    await api.deleteProfile(id);
    refresh();
  }

  const atLimit = !user?.is_premium && profiles.length >= FREE_LIMIT;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl">Profiles Vault</h1>
          <div className="text-sm text-muted">
            {profiles.length}{user?.is_premium ? "" : ` / ${FREE_LIMIT}`} profiles
            {!user?.is_premium && atLimit && " · free tier full"}
          </div>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          disabled={atLimit}
          className="btn-primary disabled:opacity-50"
          title={atLimit ? "Free tier full. Upgrade for unlimited." : ""}
        >
          {showForm ? "Cancel" : "+ New profile"}
        </button>
      </div>

      {atLimit && (
        <div className="rounded-xl border border-earth/40 bg-earth-soft p-4 text-sm">
          You've hit the <b>{FREE_LIMIT}-profile free limit</b>. Upgrade to Premium for unlimited
          profiles, yearly reports, and advanced lucky-number averaging.
        </div>
      )}

      {showForm && <CreateForm onCreated={() => { setShowForm(false); refresh(); }} />}

      {loading ? (
        <div className="text-muted">Loading…</div>
      ) : profiles.length === 0 ? (
        <div className="rounded-xl border border-dashed border-ink/20 p-6 text-center text-muted">
          No profiles yet. Create one above.
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
                  {p.is_main && <span className="ml-2 chip element-fire">MAIN</span>}
                </div>
                <button onClick={() => onDelete(p.id)} className="text-xs text-muted hover:text-fire">
                  delete
                </button>
              </div>
              <div className="text-xs text-muted mt-1">
                {new Date(p.birth_datetime).toLocaleString()}
              </div>
              {p.relationship_label && (
                <div className="text-xs text-muted mt-0.5">{p.relationship_label}</div>
              )}
              <Link to={`/profiles/${p.id}`} className="btn-ghost text-xs mt-3 self-start">
                View chart →
              </Link>
            </div>
          ))}
        </div>
      )}

      {error && <div className="text-fire text-sm">{error}</div>}
    </div>
  );
}

function CreateForm({ onCreated }: { onCreated: () => void }) {
  const [name, setName] = useState("");
  const [birth, setBirth] = useState("");
  const [label, setLabel] = useState("");
  const [location, setLocation] = useState("");
  const [gender, setGender] = useState("");
  const [isMain, setIsMain] = useState(false);
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.createProfile({
        name,
        birth_datetime: new Date(birth).toISOString(),
        relationship_label: label || null,
        birth_location: location || null,
        gender: gender || null,
        is_main: isMain,
        notes: notes || null,
      });
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="rounded-xl border border-ink/10 bg-white p-4 space-y-3">
      <div className="grid sm:grid-cols-2 gap-3">
        <label className="block">
          <span className="text-xs text-muted">Name</span>
          <input className="input mt-1" value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label className="block">
          <span className="text-xs text-muted">Birth date & time</span>
          <input type="datetime-local" className="input mt-1" value={birth} onChange={(e) => setBirth(e.target.value)} required />
        </label>
        <label className="block">
          <span className="text-xs text-muted">Relationship (self, spouse…)</span>
          <input className="input mt-1" value={label} onChange={(e) => setLabel(e.target.value)} />
        </label>
        <label className="block">
          <span className="text-xs text-muted">Birth location</span>
          <input className="input mt-1" value={location} onChange={(e) => setLocation(e.target.value)} />
        </label>
        <label className="block">
          <span className="text-xs text-muted">Gender (optional)</span>
          <select className="input mt-1" value={gender} onChange={(e) => setGender(e.target.value)}>
            <option value="">—</option>
            <option value="female">female</option>
            <option value="male">male</option>
            <option value="other">other</option>
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm mt-6">
          <input type="checkbox" checked={isMain} onChange={(e) => setIsMain(e.target.checked)} />
          Set as main profile
        </label>
      </div>
      <label className="block">
        <span className="text-xs text-muted">Notes</span>
        <textarea className="input mt-1" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>
      {error && <div className="text-xs text-fire">{error}</div>}
      <button type="submit" disabled={busy} className="btn-primary">
        {busy ? "Saving…" : "Save profile"}
      </button>
    </form>
  );
}
