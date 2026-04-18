import { FormEvent, useEffect, useState } from "react";
import { api, DeepCompatibility, Profile } from "../api";
import { ElementBar, ScoreRing } from "../components/PillarCard";

const elementClass: Record<string, string> = {
  wood: "element-wood",
  fire: "element-fire",
  earth: "element-earth",
  metal: "element-metal",
  water: "element-water",
};

const areaLabels: Record<string, string> = {
  romance: "Romance",
  communication: "Communication",
  finance: "Finance",
  family: "Family",
  long_term: "Long-term",
};

export function CompatibilityPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [a, setA] = useState<number | "">("");
  const [b, setB] = useState<number | "">("");
  const [result, setResult] = useState<DeepCompatibility | null>(null);
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
      setResult(await api.compatibilityDeep(Number(a), Number(b)));
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
          Deep synastry: Day Master interaction, spouse-star check, Useful-God exchange,
          branch-by-branch harmonies and clashes, and area scores across five life domains.
        </p>
      </div>

      {profiles.length < 2 ? (
        <div className="rounded-xl border border-dashed border-ink/20 p-6 text-center text-muted">
          Add at least two profiles in the Vault to run a compatibility reading.
        </div>
      ) : (
        <form
          onSubmit={onSubmit}
          className="rounded-2xl border border-ink/10 bg-white p-5 grid sm:grid-cols-[1fr_auto_1fr_auto] gap-3 items-end"
        >
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
        <>
          {/* Headline */}
          <section className="rounded-2xl border border-ink/10 bg-white p-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <div className="text-xs uppercase tracking-wider text-muted">Synastry</div>
                <div className="font-display text-2xl mt-1">
                  {result.profile_a} <span className="text-muted">×</span> {result.profile_b}
                </div>
                <p className="text-sm mt-2">{result.verdict}</p>
              </div>
              <ScoreRing score={result.total_score} label="Match" />
            </div>
          </section>

          {/* Area scores */}
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-3">Area Scores</div>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 justify-items-center">
              {Object.entries(result.area_scores).map(([key, score]) => (
                <ScoreRing key={key} score={score} label={areaLabels[key] || key} />
              ))}
            </div>
          </section>

          {/* Day Master relation */}
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-2">Day Master Interaction</div>
            <div className="flex items-center gap-3 mb-2">
              <span className={`chip ${elementClass[result.day_master_relation.a_element]}`}>
                A · {result.day_master_relation.a_element}
              </span>
              <span className="text-muted">↔</span>
              <span className={`chip ${elementClass[result.day_master_relation.b_element]}`}>
                B · {result.day_master_relation.b_element}
              </span>
              <span className="text-xs text-muted">({result.day_master_relation.kind.replace(/_/g, " ")})</span>
            </div>
            <p className="text-sm">{result.day_master_relation.note}</p>
          </section>

          {/* Spouse star + Useful God */}
          <section className="grid md:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-muted mb-2">Spouse Star Check</div>
              {(["a_checks_b", "b_checks_a"] as const).map((side) => {
                const s = result.spouse_star_check[side];
                const label = side === "a_checks_b"
                  ? `${result.profile_a} → ${result.profile_b}`
                  : `${result.profile_b} → ${result.profile_a}`;
                return (
                  <div key={side} className="mb-3 last:mb-0">
                    <div className="text-xs font-semibold">{label}</div>
                    {s.applicable ? (
                      <>
                        <div className="text-sm mt-1">
                          Looking for{" "}
                          <span className={`chip ${elementClass[s.expected_element!]}`}>
                            {s.expected_element}
                          </span>{" "}
                          <span className="text-muted text-xs">({s.role})</span>; partner is{" "}
                          <span className={`chip ${elementClass[s.partner_dm_element!]}`}>
                            {s.partner_dm_element}
                          </span>.
                          {s.partner_plays_spouse_star
                            ? <span className="ml-2 chip element-wood">✓ matches</span>
                            : <span className="ml-2 chip element-metal">— other channel</span>}
                        </div>
                        <p className="text-xs text-muted mt-1">{s.note}</p>
                      </>
                    ) : (
                      <p className="text-xs text-muted mt-1">{s.note}</p>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-muted mb-2">Useful God Exchange</div>
              <p className="text-sm mb-3">
                A needs <span className={`chip ${elementClass[result.useful_god_exchange.a_useful_god]}`}>{result.useful_god_exchange.a_useful_god}</span>
                ; B supplies <b>{result.useful_god_exchange.b_useful_percent_in_a.toFixed(1)}%</b>{" "}
                {result.useful_god_exchange.a_gets_what_a_needs
                  ? <span className="chip element-wood">✓ enough</span>
                  : <span className="chip element-metal">— low</span>}
              </p>
              <p className="text-sm">
                B needs <span className={`chip ${elementClass[result.useful_god_exchange.b_useful_god]}`}>{result.useful_god_exchange.b_useful_god}</span>
                ; A supplies <b>{result.useful_god_exchange.a_useful_percent_in_b.toFixed(1)}%</b>{" "}
                {result.useful_god_exchange.b_gets_what_b_needs
                  ? <span className="chip element-wood">✓ enough</span>
                  : <span className="chip element-metal">— low</span>}
              </p>
              <p className="text-xs text-muted mt-2">{result.useful_god_exchange.note}</p>
            </div>
          </section>

          {/* Branch interactions */}
          {result.branch_interactions.length > 0 && (
            <section className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-muted mb-3">Branch Interactions</div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-muted text-xs uppercase">
                      <th className="text-left py-1">Kind</th>
                      <th className="text-left py-1">A pillar</th>
                      <th className="text-left py-1">B pillar</th>
                      <th className="text-left py-1">Branches</th>
                      <th className="text-left py-1">→</th>
                      <th className="text-left py-1">Note</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.branch_interactions.map((it, i) => (
                      <tr key={i} className="border-t border-ink/5">
                        <td className="py-1.5">
                          {it.kind === "clash" && <span className="chip element-fire">Clash 六冲</span>}
                          {it.kind === "six_combination" && <span className="chip element-wood">Combo 六合</span>}
                          {it.kind === "three_harmony_partial" && <span className="chip element-earth">3-Harmony 三合</span>}
                        </td>
                        <td>{it.a_label}</td>
                        <td>{it.b_label}</td>
                        <td className="font-display text-lg">{it.a_branch} {it.b_branch}</td>
                        <td>
                          {it.transforms_to && (
                            <span className={`chip ${elementClass[it.transforms_to]}`}>{it.transforms_to}</span>
                          )}
                        </td>
                        <td className="text-xs text-muted">{it.note}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {/* Harmony / Tension */}
          <section className="grid md:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-wood mb-2">Harmony</div>
              {result.harmony.length > 0 ? (
                <ul className="list-disc pl-5 text-sm space-y-1">
                  {result.harmony.map((h, i) => <li key={i}>{h}</li>)}
                </ul>
              ) : <div className="text-sm text-muted">None notable.</div>}
            </div>
            <div className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-fire mb-2">Tension</div>
              {result.tension.length > 0 ? (
                <ul className="list-disc pl-5 text-sm space-y-1">
                  {result.tension.map((t, i) => <li key={i}>{t}</li>)}
                </ul>
              ) : <div className="text-sm text-muted">None notable.</div>}
            </div>
          </section>

          {/* Complementarity + shared weakness */}
          {(result.complementary_strengths.length > 0 || result.shared_weakness.length > 0) && (
            <section className="rounded-2xl border border-ink/10 bg-white p-5">
              {result.complementary_strengths.length > 0 && (
                <div>
                  <div className="text-xs uppercase tracking-wider text-muted mb-1">Complementary strengths</div>
                  <ul className="list-disc pl-5 text-sm space-y-1">
                    {result.complementary_strengths.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}
              {result.shared_weakness.length > 0 && (
                <div className="mt-3">
                  <div className="text-xs uppercase tracking-wider text-muted mb-1">Shared weak element(s)</div>
                  <div className="flex flex-wrap gap-1.5">
                    {result.shared_weakness.map((e) => (
                      <span key={e} className={`chip ${elementClass[e]}`}>{e}</span>
                    ))}
                  </div>
                  <p className="text-xs text-muted mt-2">
                    Neither chart emphasizes these — consciously cultivate together.
                  </p>
                </div>
              )}
            </section>
          )}

          {/* Element blend */}
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-2">Combined Five-Elements Blend</div>
            <ElementBar elements={result.element_blend} />
          </section>
        </>
      )}
    </div>
  );
}
