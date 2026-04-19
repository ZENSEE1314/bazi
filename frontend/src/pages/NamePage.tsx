import { FormEvent, useState } from "react";
import { api, ChineseNameReading } from "../api";
import { HistorySidebar } from "../components/HistorySidebar";
import { useI18n } from "../i18n";

const elementClass: Record<string, string> = {
  wood: "element-wood",
  fire: "element-fire",
  earth: "element-earth",
  metal: "element-metal",
  water: "element-water",
};

function useGridLabels(t: (k: string) => string): Record<string, { cn: string; gloss: string }> {
  return {
    heaven: { cn: "天格", gloss: "Ancestral influence / first 1/3 of life" },
    person: { cn: "人格", gloss: "Core self / personality" },
    earth:  { cn: "地格", gloss: "Subordinate / mid-life fortune" },
    total:  { cn: "总格", gloss: "Lifetime fate" },
    outer:  { cn: "外格", gloss: "Social life / external encounters" },
  };
}

function qualityClass(q: string) {
  if (q === "auspicious") return "element-wood";
  if (q === "inauspicious") return "element-fire";
  return "element-earth";
}

export function NamePage() {
  const { t } = useI18n();
  const GRID_LABELS = useGridLabels(t);
  const [name, setName] = useState("");
  const [surnameLen, setSurnameLen] = useState<number | "">("");
  const [result, setResult] = useState<ChineseNameReading | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [historyKey, setHistoryKey] = useState(0);
  const [openHistoryId, setOpenHistoryId] = useState<number | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.chineseName(name, surnameLen === "" ? undefined : Number(surnameLen)));
      setOpenHistoryId(null);
      setHistoryKey((k) => k + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  async function openHistory(id: number) {
    setError(null);
    try {
      const item = await api.getHistory<ChineseNameReading>(id);
      setResult(item.payload);
      setName(item.label);
      setOpenHistoryId(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  }

  return (
    <div className="grid lg:grid-cols-[1fr_240px] gap-4">
      <div className="space-y-6 min-w-0">
      <div>
        <h1 className="font-display text-2xl">{t("name.title")}</h1>
        <p className="text-sm text-muted">{t("name.subtitle")}</p>
      </div>

      <form onSubmit={onSubmit} className="rounded-2xl border border-ink/10 bg-white p-5 flex gap-2 items-end flex-wrap">
        <label className="block flex-1 min-w-[240px]">
          <span className="text-xs text-muted">{t("name.enter")}</span>
          <input className="input mt-1" value={name} onChange={(e) => setName(e.target.value)} placeholder="王小明" required />
        </label>
        <label className="block">
          <span className="text-xs text-muted">{t("name.surname_length")}</span>
          <select className="input mt-1" value={surnameLen} onChange={(e) => setSurnameLen(e.target.value === "" ? "" : Number(e.target.value))}>
            <option value="">{t("name.auto")}</option>
            <option value="1">{t("name.one_char")}</option>
            <option value="2">{t("name.two_chars")}</option>
          </select>
        </label>
        <button type="submit" disabled={busy} className="btn-primary">
          {busy ? t("name.reading") : t("name.analyse")}
        </button>
      </form>

      {error && <div className="text-fire text-sm">{error}</div>}

      {result && (
        <>
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="flex items-center gap-4 flex-wrap">
              <div className="font-display text-5xl">{result.name}</div>
              <div>
                <div className="text-xs text-muted">surname / given</div>
                <div className="font-display text-lg">{result.surname} · {result.given}</div>
              </div>
              <div className="ml-auto flex flex-wrap gap-2">
                <span className="chip element-wood">✓ {result.auspicious_grids}</span>
                <span className="chip element-earth">~ {result.mixed_grids}</span>
                <span className="chip element-fire">✗ {result.inauspicious_grids}</span>
              </div>
            </div>
            <p className="mt-3 text-sm">{result.summary}</p>

            <div className="mt-4">
              <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("name.character_strokes")}</div>
              <div className="flex flex-wrap gap-2">
                {result.character_strokes.map((c, i) => (
                  <div key={i} className="px-3 py-2 rounded-lg border border-ink/10 bg-parchment min-w-[120px]">
                    <div className="flex items-baseline gap-2">
                      <span className="font-display text-2xl">{c.char}</span>
                      <span className="text-xs text-muted">{c.strokes} {t("name.strokes")}</span>
                    </div>
                    {c.meaning && (
                      <div className="text-[11px] text-muted mt-1 italic">{c.meaning}</div>
                    )}
                  </div>
                ))}
              </div>
              <div className="text-xs text-muted mt-2">
                {t("name.totals")}: {result.surname_strokes} + {result.given_strokes} = <b>{result.total_strokes}</b>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-3">{t("name.five_grids")}</div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs uppercase text-muted">
                    <th className="text-left py-1">{t("name.grid")}</th>
                    <th className="text-left py-1">{t("name.grid_number")}</th>
                    <th className="text-left py-1">{t("name.grid_meaning")}</th>
                    <th className="text-left py-1">{t("name.grid_quality")}</th>
                    <th className="text-left py-1">{t("name.grid_theme")}</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(result.grids).map(([key, g]) => {
                    const label = GRID_LABELS[key];
                    return (
                      <tr key={key} className="border-t border-ink/5">
                        <td className="py-1.5">
                          <b>{label.cn}</b> <span className="text-muted capitalize text-xs">({key})</span>
                          <div className="text-xs text-muted">{label.gloss}</div>
                        </td>
                        <td className="font-display text-xl">{g.number}</td>
                        <td>{g.en}</td>
                        <td><span className={`chip ${qualityClass(g.quality)}`}>{g.quality}</span></td>
                        <td className="text-muted">{g.theme}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* Three Talents */}
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
              <div className="text-xs uppercase tracking-wider text-muted">
                {t("name.three_talents")}
              </div>
              <span className={`chip ${
                result.three_talents.level === "great" ? "element-wood" :
                result.three_talents.level === "good" ? "element-wood" :
                result.three_talents.level === "bad" ? "element-fire" :
                "element-earth"
              }`}>
                {result.three_talents.label_cn} {result.three_talents.label_en}
              </span>
            </div>
            <div className="flex items-center gap-2 justify-center text-sm mb-3">
              <div className="text-center">
                <div className="text-xs text-muted">{t("name.heaven")}</div>
                <span className={`chip ${elementClass[result.three_talents.heaven_element]} text-base px-3 py-1`}>
                  {result.three_talents.heaven_element}
                </span>
              </div>
              <div className="text-muted">→</div>
              <div className="text-center">
                <div className="text-xs text-muted">{t("name.person")}</div>
                <span className={`chip ${elementClass[result.three_talents.person_element]} text-base px-3 py-1`}>
                  {result.three_talents.person_element}
                </span>
              </div>
              <div className="text-muted">→</div>
              <div className="text-center">
                <div className="text-xs text-muted">{t("name.earth")}</div>
                <span className={`chip ${elementClass[result.three_talents.earth_element]} text-base px-3 py-1`}>
                  {result.three_talents.earth_element}
                </span>
              </div>
            </div>
            <p className="text-sm text-muted">{result.three_talents.note}</p>
          </section>

          {/* Life stages */}
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-3">{t("name.life_stages")}</div>
            <div className="space-y-2">
              {result.life_stages.map((s, i) => (
                <div key={i} className="flex gap-3 items-start rounded-xl border border-ink/5 p-3 bg-parchment/50">
                  <div className="shrink-0 text-center w-24">
                    <div className="text-xs text-muted">{s.age_label_en}</div>
                    <div className="text-xs text-muted">{s.age_label_zh}</div>
                    <div className="font-display text-2xl mt-1">{s.number}</div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <b className="text-sm">{s.role}</b>
                      <span className={`chip ${qualityClass(s.quality)}`}>{s.quality}</span>
                    </div>
                    <p className="text-sm mt-1">{s.note}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Aspect scores */}
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-3">{t("name.aspects")}</div>
            <div className="grid grid-cols-5 gap-2 text-center">
              {(["career", "wealth", "health", "marriage", "social"] as const).map((k) => {
                const v = result.aspect_scores[k];
                const chipCls = v >= 80 ? "element-wood" : v >= 45 ? "element-earth" : "element-fire";
                return (
                  <div key={k} className="rounded-xl border border-ink/5 p-3">
                    <div className="text-[10px] uppercase tracking-wider text-muted">{t(`name.aspect_${k}`)}</div>
                    <div className="font-display text-2xl mt-1">{v}</div>
                    <span className={`chip ${chipCls} mt-1 text-[10px]`}>{v >= 80 ? "strong" : v >= 45 ? "mixed" : "weak"}</span>
                  </div>
                );
              })}
            </div>
            {result.aspect_notes.length > 0 && (
              <ul className="list-disc pl-5 mt-4 text-sm space-y-1">
                {result.aspect_notes.map((n, i) => <li key={i}>{n}</li>)}
              </ul>
            )}
          </section>

          {/* Yin Yang */}
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("name.yin_yang")}</div>
            <div className="flex items-center gap-3 text-sm mb-2">
              <div className="flex-1">
                <div className="text-xs text-muted">{t("name.odd")}</div>
                <div className="font-display text-2xl">{result.yin_yang.odd_count}</div>
              </div>
              <div className="flex-1">
                <div className="text-xs text-muted">{t("name.even")}</div>
                <div className="font-display text-2xl">{result.yin_yang.even_count}</div>
              </div>
            </div>
            <p className="text-sm">{result.yin_yang.verdict}</p>
          </section>

          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-2">
              {t("name.element_profile")} — {t("numerology.dominant")}: <b>{result.dominant_element}</b>
            </div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(result.element_profile).map(([el, count]) => (
                <span key={el} className={`chip ${elementClass[el]}`}>{el}: {count}</span>
              ))}
            </div>
          </section>
        </>
      )}
      </div>
      <div className="order-first lg:order-none">
        <HistorySidebar
          kind="name"
          refreshKey={historyKey}
          currentId={openHistoryId}
          onOpen={openHistory}
        />
      </div>
    </div>
  );
}
