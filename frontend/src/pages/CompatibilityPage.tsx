import { FormEvent, useEffect, useState } from "react";
import { api, Compatibility, Profile } from "../api";
import { ElementBar, ScoreRing } from "../components/PillarCard";

export function CompatibilityPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [a, setA] = useState<number | "">("");
  const [b, setB] = useState<number | "">("");
  const [result, setResult] = useState<Compatibility | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.listProfiles().then(setProfiles).catch((e) => setError(String(e)));
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (a === "" || b === "" || a === b) {
      setError("Pick two different profiles.");
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.compatibility(Number(a), Number(b)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl">Relationship Compatibility</h1>
        <p className="text-sm text-muted">
          Pick two saved profiles. We compare their Day Masters and Five-Elements blend.
        </p>
      </div>

      {profiles.length < 2 ? (
        <div className="rounded-xl border border-dashed border-ink/20 p-6 text-center text-muted">
          Add at least two profiles in the Vault to run a compatibility reading.
        </div>
      ) : (
        <form onSubmit={onSubmit} className="rounded-2xl border border-ink/10 bg-white p-5 grid sm:grid-cols-[1fr_auto_1fr_auto] gap-3 items-end">
          <label className="block">
            <span className="text-xs text-muted">Person A</span>
            <select className="input mt-1" value={a} onChange={(e) => setA(e.target.value === "" ? "" : Number(e.target.value))} required>
              <option value="">Select…</option>
              {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </label>
          <div className="text-center font-display text-muted hidden sm:block">×</div>
          <label className="block">
            <span className="text-xs text-muted">Person B</span>
            <select className="input mt-1" value={b} onChange={(e) => setB(e.target.value === "" ? "" : Number(e.target.value))} required>
              <option value="">Select…</option>
              {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </label>
          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? "Reading…" : "Compare"}
          </button>
        </form>
      )}

      {error && <div className="text-fire text-sm">{error}</div>}

      {result && (
        <section className="rounded-2xl border border-ink/10 bg-white p-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <div className="text-xs uppercase tracking-wider text-muted">Synastry</div>
              <p className="font-display text-xl mt-1">{result.summary}</p>
            </div>
            <ScoreRing score={result.score} label="Match" />
          </div>

          {result.harmony.length > 0 && (
            <div className="mt-4">
              <div className="text-xs uppercase tracking-wider text-wood mb-1">Harmony</div>
              <ul className="list-disc pl-5 text-sm space-y-0.5">
                {result.harmony.map((h, i) => <li key={i}>{h}</li>)}
              </ul>
            </div>
          )}
          {result.tension.length > 0 && (
            <div className="mt-4">
              <div className="text-xs uppercase tracking-wider text-fire mb-1">Tension</div>
              <ul className="list-disc pl-5 text-sm space-y-0.5">
                {result.tension.map((t, i) => <li key={i}>{t}</li>)}
              </ul>
            </div>
          )}

          <div className="mt-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-1">Combined Five-Element blend</div>
            <ElementBar elements={result.element_blend} />
          </div>
        </section>
      )}
    </div>
  );
}
