import { FormEvent, useEffect, useState } from "react";
import { api, DeepNumerology, Profile } from "../api";
import { ElementBar, ScoreRing } from "../components/PillarCard";
import { useI18n } from "../i18n";

const TYPE_IDS = ["phone", "bank", "car", "id", "credit"] as const;

const typePlaceholder: Record<string, string> = {
  phone: "+60 12-888-8888",
  bank: "1234567890",
  car: "WAB 8888",
  id: "880514-14-1234",
  credit: "4012 3456 7890 1234",
};

function typeNarrative(type: string, n: DeepNumerology): string {
  if (type === "phone")
    return n.scores.wealth >= 75
      ? "Phone energy leans wealth/opportunity — good for sales, negotiation, closing."
      : "Phone energy is steady rather than wealth-magnetic; fine for personal use.";
  if (type === "bank")
    return n.scores.safety >= 75
      ? "Strong safety profile — account accumulates and protects."
      : "Account is workable but lacks strong safety lock; diversify savings across multiple instruments.";
  if (type === "car")
    return n.scores.safety >= 70
      ? "Plate scores high on safety — favorable for daily driving and travel."
      : "Consider complementing with protective charms if safety is low; be extra careful on long trips.";
  if (type === "id")
    return `Identity number aligns with Life Path ${n.life_path}. This number filters how institutions see you.`;
  if (type === "credit")
    return n.scores.wealth >= 75
      ? "Wealth-attracting plastic — good for active spending on growth assets."
      : "Neutral-to-cautious for wealth; keep for necessities.";
  return "";
}

export function NumerologyPage() {
  const { t, lang } = useI18n();
  const [type, setType] = useState<string>("phone");
  const [number, setNumber] = useState("");
  const [profileId, setProfileId] = useState<number | "">("");
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [result, setResult] = useState<DeepNumerology | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.listProfiles().then(setProfiles).catch(() => {});
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(
        await api.numerologyDeep(
          number,
          profileId === "" ? undefined : Number(profileId),
          lang,
        ),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl">{t("numerology.title")}</h1>
        <p className="text-sm text-muted">{t("numerology.subtitle")}</p>
      </div>

      <div className="rounded-2xl border border-ink/10 bg-white p-5 space-y-3">
        <div className="flex flex-wrap gap-2">
          {TYPE_IDS.map((id) => (
            <button
              key={id}
              onClick={() => { setType(id); setResult(null); setNumber(""); }}
              className={`px-3 py-1.5 rounded-lg text-sm transition ${
                type === id ? "bg-ink text-parchment" : "bg-ink/5 text-ink hover:bg-ink/10"
              }`}
            >
              {t(`numerology.type_${id}`)}
            </button>
          ))}
        </div>

        <label className="block">
          <span className="text-xs text-muted">{t("numerology.link_profile")}</span>
          <select
            className="input mt-1"
            value={profileId}
            onChange={(e) => setProfileId(e.target.value === "" ? "" : Number(e.target.value))}
          >
            <option value="">{t("numerology.select_profile")}</option>
            {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>

        <form onSubmit={onSubmit} className="flex gap-2 flex-wrap">
          <input
            className="input flex-1 min-w-[240px]"
            placeholder={typePlaceholder[type]}
            value={number}
            onChange={(e) => setNumber(e.target.value)}
            required
          />
          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? t("numerology.scoring") : t("numerology.score")}
          </button>
        </form>
      </div>

      {error && <div className="text-fire text-sm">{error}</div>}

      {result && (
        <>
          <section className="rounded-2xl border border-ink/10 bg-white p-6">
            <div className="grid sm:grid-cols-4 gap-4 items-center justify-items-center">
              <ScoreRing score={result.scores.wealth} label={t("numerology.wealth")} />
              <ScoreRing score={result.scores.safety} label={t("numerology.safety")} />
              <ScoreRing score={result.scores.health} label={t("numerology.health")} />
              <ScoreRing score={result.scores.overall} label={t("numerology.overall")} />
            </div>
            <p className="mt-5 text-sm">{typeNarrative(type, result)}</p>
          </section>

          {result.profile_name && (
            <section className="rounded-2xl border border-wood/40 bg-wood-soft p-5">
              <div className="text-xs uppercase tracking-wider text-wood mb-1">
                {t("numerology.personalized")} · {result.profile_name}
              </div>
              <p className="text-sm mb-3">{result.personalized_note}</p>
              <div className="flex flex-wrap gap-3 text-sm">
                <div>
                  <div className="text-xs text-muted">{t("numerology.preferred_digits")}</div>
                  <div className="flex gap-1 mt-1">
                    {result.preferred_digits.map((d) => (
                      <span key={d} className="font-display text-xl px-2 rounded bg-white">{d}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted">{t("numerology.avoid_digits")}</div>
                  <div className="flex gap-1 mt-1">
                    {result.digits_to_avoid.length === 0 ? (
                      <span className="text-xs text-muted">—</span>
                    ) : result.digits_to_avoid.map((d) => (
                      <span key={d} className="font-display text-xl px-2 rounded bg-fire-soft text-fire">{d}</span>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          )}

          {result.suggestion && (result.suggestion.issues.length > 0 || result.suggestion.suggestions.length > 0) && (
            <section className="rounded-2xl border border-ink/10 bg-white p-5">
              {result.suggestion.issues.length > 0 && (
                <div className="mb-3">
                  <div className="text-xs uppercase tracking-wider text-fire mb-1">{t("numerology.issues")}</div>
                  <ul className="list-disc pl-5 text-sm space-y-1">
                    {result.suggestion.issues.map((i, idx) => <li key={idx}>{i}</li>)}
                  </ul>
                </div>
              )}
              {result.suggestion.suggestions.length > 0 && (
                <div>
                  <div className="text-xs uppercase tracking-wider text-wood mb-1">{t("numerology.suggestions")}</div>
                  <ul className="text-sm space-y-1">
                    {result.suggestion.suggestions.map((s, idx) => (
                      <li key={idx} className="font-mono bg-parchment rounded px-2 py-1 border border-ink/5">{s}</li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}

          <section className="grid md:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("numerology.life_path")}</div>
              <div className="font-display text-5xl">{result.life_path}</div>
              <p className="mt-2 text-sm">{result.life_path_theme}</p>
            </div>
            <div className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-muted mb-1">
                {t("numerology.element_profile")} — {t("numerology.dominant")}: <b>{result.scores.dominant_element}</b>
              </div>
              <ElementBar elements={result.scores.element_counts} />
            </div>
          </section>

          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs uppercase tracking-wider text-muted">
                {t("numerology.pair_analysis")}
              </div>
              <div className="text-xs">
                <span className="chip element-wood mr-1">✓ {result.auspicious_pair_count} {t("numerology.auspicious")}</span>
                <span className="chip element-fire">✗ {result.inauspicious_pair_count} {t("numerology.inauspicious")}</span>
              </div>
            </div>
            <div className="space-y-2">
              {result.pairs.map((p, i) => (
                <div key={i} className={`rounded-xl border p-3 ${p.auspicious ? "border-wood/20 bg-wood-soft/30" : "border-fire/20 bg-fire-soft/30"}`}>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-display text-xl">{p.a}-{p.b}</span>
                    {p.auspicious
                      ? <span className="chip element-wood">✓</span>
                      : <span className="chip element-fire">✗</span>}
                    <span className="text-sm"><b>{p.category_cn}</b> {p.category_en}</span>
                    <span className="text-muted text-xs">— {p.theme}</span>
                  </div>
                  <div className="text-xs mt-2 text-muted">
                    <span className="uppercase tracking-wider mr-1">{t("numerology.why")}:</span>
                    {p.explanation}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
