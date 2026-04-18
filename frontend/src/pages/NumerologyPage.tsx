import { FormEvent, useState } from "react";
import { api, DeepNumerology } from "../api";
import { ElementBar, ScoreRing } from "../components/PillarCard";

const TYPES = [
  { id: "phone", label: "Phone Number", placeholder: "+60 12-888-8888", hint: "Everyday contact — wealth & safety matter." },
  { id: "bank",  label: "Bank Account", placeholder: "1234567890", hint: "Long-term vessel — favor stable/balanced numbers." },
  { id: "car",   label: "Car Plate",    placeholder: "WAB 8888",   hint: "Mobility & travel — movement safety matters." },
  { id: "id",    label: "ID / IC Number", placeholder: "880514-14-1234", hint: "Identity-level — life-path and overall score matter most." },
  { id: "credit",label: "Credit Card",  placeholder: "4012 3456 7890 1234", hint: "Spending instrument — wealth axis is key." },
];

const typeNarrative: Record<string, (n: DeepNumerology) => string> = {
  phone: (n) => n.scores.wealth >= 75 ? "Phone energy leans wealth/opportunity — good for sales, negotiation, closing." : "Phone energy is steady rather than wealth-magnetic; fine for personal use.",
  bank:  (n) => n.scores.safety >= 75 ? "Strong safety profile — account accumulates and protects." : "Account is workable but lacks strong safety lock; diversify savings across multiple instruments.",
  car:   (n) => n.scores.safety >= 70 ? "Plate scores high on safety — favorable for daily driving and travel." : "Consider complementing with protective charms if safety is low; be extra careful on long trips.",
  id:    (n) => `Identity number aligns with Life Path ${n.life_path}. The ID carries you through official systems; the Life Path theme is the lens bureaucrats and institutions will filter you through.`,
  credit:(n) => n.scores.wealth >= 75 ? "Wealth-attracting plastic — good for active spending on growth assets." : "Neutral-to-cautious for wealth; keep for necessities, channel growth spending through a different instrument.",
};

export function NumerologyPage() {
  const [type, setType] = useState("phone");
  const [number, setNumber] = useState("");
  const [result, setResult] = useState<DeepNumerology | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const activeType = TYPES.find((t) => t.id === type)!;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.numerologyDeep(number));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl">Number Check</h1>
        <p className="text-sm text-muted">
          Score any number — phone, bank account, car plate, ID, credit card.
          Deep mode runs a Life-Path number and Ba-Zhai pair-by-pair analysis.
        </p>
      </div>

      <div className="rounded-2xl border border-ink/10 bg-white p-5 space-y-3">
        <div className="flex flex-wrap gap-2">
          {TYPES.map((t) => (
            <button
              key={t.id}
              onClick={() => { setType(t.id); setResult(null); setNumber(""); }}
              className={`px-3 py-1.5 rounded-lg text-sm transition ${
                type === t.id ? "bg-ink text-parchment" : "bg-ink/5 text-ink hover:bg-ink/10"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="text-xs text-muted">{activeType.hint}</div>
        <form onSubmit={onSubmit} className="flex gap-2 flex-wrap">
          <input
            className="input flex-1 min-w-[240px]"
            placeholder={activeType.placeholder}
            value={number}
            onChange={(e) => setNumber(e.target.value)}
            required
          />
          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? "Scoring…" : "Score"}
          </button>
        </form>
      </div>

      {error && <div className="text-fire text-sm">{error}</div>}

      {result && (
        <>
          <section className="rounded-2xl border border-ink/10 bg-white p-6">
            <div className="grid sm:grid-cols-4 gap-4 items-center justify-items-center">
              <ScoreRing score={result.scores.wealth} label="Wealth" />
              <ScoreRing score={result.scores.safety} label="Safety" />
              <ScoreRing score={result.scores.health} label="Health" />
              <ScoreRing score={result.scores.overall} label="Overall" />
            </div>
            <p className="mt-5 text-sm">{typeNarrative[type]?.(result)}</p>
          </section>

          <section className="grid md:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-muted mb-1">Life Path</div>
              <div className="font-display text-5xl">{result.life_path}</div>
              <p className="mt-2 text-sm">{result.life_path_theme}</p>
            </div>
            <div className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-muted mb-1">
                Element Profile — dominant: <b>{result.scores.dominant_element}</b>
              </div>
              <ElementBar elements={result.scores.element_counts} />
            </div>
          </section>

          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs uppercase tracking-wider text-muted">
                Pair-by-Pair (Ba Zhai system)
              </div>
              <div className="text-xs">
                <span className="chip element-wood mr-1">✓ {result.auspicious_pair_count} auspicious</span>
                <span className="chip element-fire">✗ {result.inauspicious_pair_count} inauspicious</span>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs uppercase text-muted">
                    <th className="text-left py-1">Pair</th>
                    <th className="text-left py-1">Quality</th>
                    <th className="text-left py-1">Category</th>
                    <th className="text-left py-1">Theme</th>
                  </tr>
                </thead>
                <tbody>
                  {result.pairs.map((p, i) => (
                    <tr key={i} className="border-t border-ink/5">
                      <td className="py-1.5 font-display text-lg">{p.a}-{p.b}</td>
                      <td>
                        {p.auspicious
                          ? <span className="chip element-wood">✓</span>
                          : <span className="chip element-fire">✗</span>}
                      </td>
                      <td>{p.category_cn} {p.category_en}</td>
                      <td className="text-muted">{p.theme}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
