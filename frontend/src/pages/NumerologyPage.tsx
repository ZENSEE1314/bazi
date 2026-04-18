import { FormEvent, useState } from "react";
import { api, Numerology } from "../api";
import { ElementBar, ScoreRing } from "../components/PillarCard";

export function NumerologyPage() {
  const [number, setNumber] = useState("");
  const [result, setResult] = useState<Numerology | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.numerology(number));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl">Quick Check</h1>
        <p className="text-sm text-muted">
          Score a phone number, bank account, car plate or ID on Wealth, Safety, and Health.
        </p>
      </div>

      <form onSubmit={onSubmit} className="rounded-2xl border border-ink/10 bg-white p-5 flex gap-2 flex-wrap">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="+1 555 888 8888"
          value={number}
          onChange={(e) => setNumber(e.target.value)}
          required
        />
        <button type="submit" disabled={busy} className="btn-primary">
          {busy ? "Scoring…" : "Score"}
        </button>
      </form>

      {error && <div className="text-fire text-sm">{error}</div>}

      {result && (
        <section className="rounded-2xl border border-ink/10 bg-white p-6">
          <div className="grid sm:grid-cols-4 gap-4 items-center justify-items-center">
            <ScoreRing score={result.wealth} label="Wealth" />
            <ScoreRing score={result.safety} label="Safety" />
            <ScoreRing score={result.health} label="Health" />
            <ScoreRing score={result.overall} label="Overall" />
          </div>
          <div className="mt-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-1">
              Element profile — dominant: <b>{result.dominant_element}</b>
            </div>
            <ElementBar elements={result.element_counts} />
          </div>
        </section>
      )}
    </div>
  );
}
