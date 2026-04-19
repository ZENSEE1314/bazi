import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Daily, DeepBaZi, Profile } from "../api";
import { ElementBar, ScoreRing } from "../components/PillarCard";
import { useI18n } from "../i18n";

const elementClass: Record<string, string> = {
  wood: "element-wood",
  fire: "element-fire",
  earth: "element-earth",
  metal: "element-metal",
  water: "element-water",
};

const starLabels: Record<string, { cn: string; en: string }> = {
  nobleman:      { cn: "天乙贵人", en: "Nobleman" },
  peach_blossom: { cn: "桃花",     en: "Peach Blossom" },
  academic:      { cn: "文昌",     en: "Intelligence" },
  sky_horse:     { cn: "驿马",     en: "Sky Horse" },
};

function formatBirth(iso: string, locale: string): string {
  try {
    return new Date(iso).toLocaleString(locale, {
      year:   "numeric",
      month:  "long",
      day:    "numeric",
      hour:   "2-digit",
      minute: "2-digit",
    });
  } catch {
    return new Date(iso).toLocaleString();
  }
}

function ageFromBirth(iso: string): number {
  const b = new Date(iso);
  const now = new Date();
  let age = now.getFullYear() - b.getFullYear();
  const m = now.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < b.getDate())) age -= 1;
  return age;
}

export function DashboardPage() {
  const { t, lang } = useI18n();
  const [profile, setProfile] = useState<Profile | null | undefined>(undefined);
  const [deep, setDeep] = useState<DeepBaZi | null>(null);
  const [daily, setDaily] = useState<Daily | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listProfiles()
      .then((profiles) => {
        const main = profiles.find((p) => p.is_main) ?? profiles[0] ?? null;
        setProfile(main);
        if (main) {
          Promise.all([api.deep(main.id, lang), api.daily(main.id)])
            .then(([d, dl]) => { setDeep(d); setDaily(dl); })
            .catch((e) => setError(String(e)));
        }
      })
      .catch((e) => { setError(String(e)); setProfile(null); });
  }, [lang]);

  if (profile === undefined) {
    return <div className="text-muted">{t("common.loading")}</div>;
  }

  if (profile === null) {
    return (
      <div className="rounded-2xl border border-dashed border-ink/20 p-8 text-center">
        <div className="font-display text-3xl">{t("dash.welcome")}</div>
        <p className="mt-2 text-muted">{t("dash.welcome_empty")}</p>
        <Link to="/profiles" className="btn-primary mt-4">{t("dash.add_profile")}</Link>
      </div>
    );
  }

  const age = ageFromBirth(profile.birth_datetime);
  const currentLuckPillar = deep?.luck_pillars.find(
    (lp) => age >= lp.start_age && age < lp.end_age,
  );

  return (
    <div className="space-y-6">
      {/* --- Profile identity card ------------------------------------- */}
      <section className="rounded-2xl border border-earth/30 bg-gradient-to-br from-parchment via-white to-earth-soft/40 p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="min-w-0">
            <div className="text-xs text-muted uppercase tracking-wider">
              {t("dash.main_profile")}
              {profile.relationship_label && ` · ${profile.relationship_label}`}
            </div>
            <h1 className="font-display text-3xl mt-1 flex items-baseline flex-wrap gap-3">
              <span>{profile.name}</span>
              {profile.chinese_name && (
                <span className="text-muted text-2xl">{profile.chinese_name}</span>
              )}
            </h1>
            <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-sm">
              <InfoRow label={t("dash.born")} value={formatBirth(profile.birth_datetime, lang)} />
              {profile.birth_location && (
                <InfoRow label={t("dash.location")} value={profile.birth_location} />
              )}
              {profile.gender && (
                <InfoRow label={t("dash.gender")} value={profile.gender} />
              )}
              <InfoRow label={t("dash.age")} value={`${age}`} />
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <Link to={`/profiles/${profile.id}`} className="btn-primary text-sm">
              {t("dash.open_full")}
            </Link>
            <Link to="/chat" className="btn-ghost text-sm">
              {t("dash.ask_reader")}
            </Link>
          </div>
        </div>

        {deep && (
          <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3">
            <QuickStat
              label={t("dash.day_master")}
              main={`${deep.day_master.stem}`}
              sub={`${deep.day_master.element} · ${deep.day_master.strength_level}`}
              tone={deep.day_master.element}
            />
            <QuickStat
              label={t("dash.zodiac")}
              main={deep.zodiac}
              sub={deep.chart_string}
            />
            <QuickStat
              label={t("dash.useful_god")}
              main={deep.day_master.useful_god}
              sub={t("dash.useful_god_sub")}
              tone={deep.day_master.useful_god}
            />
            <QuickStat
              label={t("dash.avoid_god")}
              main={deep.day_master.avoid_god}
              sub={t("dash.avoid_god_sub")}
              tone={deep.day_master.avoid_god}
            />
          </div>
        )}
      </section>

      {/* --- Four Pillars with hidden stems ---------------------------- */}
      {deep && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-3">
            {t("detail.four_pillars")} · {deep.chart_string}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {deep.pillars.map((p) => (
              <div key={p.label} className="rounded-xl border border-ink/10 bg-parchment/40 p-3">
                <div className="text-[10px] uppercase tracking-wider text-muted">{p.label}</div>
                <div className="font-display text-3xl mt-1">{p.stem}{p.branch}</div>
                <div className="text-xs text-muted">{p.pinyin}</div>
                <div className="mt-2 flex flex-wrap gap-1">
                  <span className={`chip text-[10px] ${elementClass[p.stem_element]}`}>{p.stem_element}</span>
                  <span className={`chip text-[10px] ${elementClass[p.branch_element]}`}>{p.branch_element}</span>
                </div>
                {p.stem_ten_god_en ? (
                  <div className="mt-2 text-[11px] text-muted">
                    {p.stem_ten_god_cn} · {p.stem_ten_god_en}
                  </div>
                ) : (
                  <div className="mt-2 text-[11px] font-medium">{t("detail.day_master_word")}</div>
                )}
                <div className="mt-1 text-[11px] text-muted italic">
                  {p.nayin_cn} ({p.nayin_en})
                </div>
                {p.hidden_stems.length > 0 && (
                  <div className="mt-2 text-[10px] text-muted border-t border-ink/5 pt-1.5">
                    <div className="font-semibold text-[10px]">{t("detail.hidden")}</div>
                    {p.hidden_stems.map((h, i) => (
                      <div key={i} className="truncate">
                        {h.stem}·{h.element} {h.ten_god_en}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* --- Element balance + Day Master verdict ---------------------- */}
      {deep && (
        <section className="grid md:grid-cols-2 gap-4">
          <div className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-3">
              {t("detail.five_elements_raw")}
            </div>
            <ElementBar elements={deep.elements} />
            <div className="mt-3 text-xs text-muted">
              {t("dash.dominant")}: <b className="text-ink">{deep.dominant_element}</b> ·
              {" "}{t("dash.weakest")}: <b className="text-ink">{deep.weakest_element}</b>
            </div>
            <div className="mt-4 text-xs uppercase tracking-wider text-muted mb-2">
              {t("detail.five_factors")}
            </div>
            <div className="space-y-1">
              {deep.five_factors.map((f) => (
                <div key={f.key} className="flex items-center gap-2 text-xs">
                  <span className={`chip ${elementClass[f.element]} text-[10px]`}>{f.element}</span>
                  <span className="w-20 truncate">{f.label}</span>
                  <div className="flex-1 h-2 bg-ink/5 rounded-full overflow-hidden">
                    <div
                      className={elementClass[f.element].split(" ").find((c) => c.startsWith("bg-")) || "bg-ink/20"}
                      style={{ width: `${f.percent}%`, height: "100%" }}
                    />
                  </div>
                  <span className="text-muted w-10 text-right">{f.percent.toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-2">
              {t("detail.day_master_verdict")}
            </div>
            <p className="text-sm">{deep.day_master.seasonal_influence}</p>
            <p className="mt-2 text-sm">{deep.day_master.explanation}</p>
            <div className="mt-4 text-xs text-muted">
              {t("detail.strength")}:{" "}
              <span className="font-medium text-ink">{deep.day_master.strength_level}</span>
              {" "}({deep.day_master.strength_score.toFixed(2)})
            </div>
          </div>
        </section>
      )}

      {/* --- Current luck (annual + 10-year pillar) -------------------- */}
      {deep && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-3">
            {t("dash.current_luck")}
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="rounded-xl border border-earth/30 bg-earth-soft/30 p-4">
              <div className="text-[11px] uppercase tracking-wider text-muted">
                {t("detail.annual_luck")} · {deep.annual_luck.year}
              </div>
              <div className="font-display text-3xl mt-1">
                {deep.annual_luck.stem}{deep.annual_luck.branch}
              </div>
              <div className="text-xs text-muted mt-1">
                {deep.annual_luck.stem_ten_god_cn} {deep.annual_luck.stem_ten_god_en}
              </div>
              <p className="mt-2 text-sm">{deep.annual_luck.note}</p>
            </div>
            {currentLuckPillar ? (
              <div className="rounded-xl border border-wood/30 bg-wood-soft/30 p-4">
                <div className="text-[11px] uppercase tracking-wider text-muted">
                  {t("dash.current_cycle")} · {t("detail.age")} {currentLuckPillar.start_age}-{currentLuckPillar.end_age - 1}
                </div>
                <div className="font-display text-3xl mt-1">
                  {currentLuckPillar.stem}{currentLuckPillar.branch}
                </div>
                <div className="text-xs text-muted mt-1">
                  {currentLuckPillar.stem_ten_god_cn} {currentLuckPillar.stem_ten_god_en} · {currentLuckPillar.nayin_en}
                </div>
                <div className="mt-2 flex gap-1">
                  <span className={`chip text-xs ${elementClass[currentLuckPillar.stem_element]}`}>
                    {currentLuckPillar.stem_element}
                  </span>
                  <span className={`chip text-xs ${elementClass[currentLuckPillar.branch_element]}`}>
                    {currentLuckPillar.branch_element}
                  </span>
                </div>
              </div>
            ) : (
              <div className="rounded-xl border border-ink/10 p-4 text-sm text-muted">
                {t("dash.cycle_before_start")}
              </div>
            )}
          </div>
        </section>
      )}

      {/* --- Today --------------------------------------------------------- */}
      {daily && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div>
              <div className="text-xs uppercase tracking-wider text-muted">
                {t("dash.todays_luck")} · {daily.date}
              </div>
              <div className="font-display text-2xl mt-1">
                {daily.day_pillar.stem}{daily.day_pillar.branch}
              </div>
              <div className="text-xs text-muted">{daily.day_pillar.pinyin}</div>
            </div>
            <ScoreRing score={daily.score} label={t("dash.luck")} />
          </div>
          <p className="mt-3 text-sm">{daily.summary}</p>
          <div className="mt-3 grid sm:grid-cols-2 gap-3">
            {daily.supportive_elements.length > 0 && (
              <div>
                <div className="text-xs uppercase tracking-wider text-wood mb-1">
                  ✓ {t("dash.supportive")}
                </div>
                <ul className="list-disc pl-5 text-sm space-y-0.5">
                  {daily.supportive_elements.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
            {daily.clashing_elements.length > 0 && (
              <div>
                <div className="text-xs uppercase tracking-wider text-fire mb-1">
                  ⚠ {t("dash.friction")}
                </div>
                <ul className="list-disc pl-5 text-sm space-y-0.5">
                  {daily.clashing_elements.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
          </div>
        </section>
      )}

      {/* --- Life Kua + directions ------------------------------------ */}
      {deep?.life_kua && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="flex items-start justify-between gap-3 flex-wrap mb-3">
            <div>
              <div className="text-xs uppercase tracking-wider text-muted">
                {t("detail.eight_mansions")}
              </div>
              <div className="font-display text-2xl">
                {deep.life_kua.number} · {deep.life_kua.trigram_cn} ({deep.life_kua.trigram_pinyin})
              </div>
              <div className="text-xs text-muted">
                {deep.life_kua.group === "East" ? t("detail.group_east") : t("detail.group_west")} ·
                {" "}{t("detail.seat")}: <b>{deep.life_kua.seated_direction}</b>
              </div>
            </div>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm font-medium text-wood mb-2">✓ {t("detail.lucky")}</div>
              <div className="space-y-1.5">
                {deep.lucky_directions.map((d) => (
                  <div key={d.category_key} className="flex items-start gap-2 text-sm">
                    <span className="chip element-wood w-10 justify-center">{d.direction}</span>
                    <div className="flex-1 min-w-0">
                      <div className="truncate"><b>{d.cn}</b> {d.en} · {d.direction_name}</div>
                      <div className="text-xs text-muted truncate">{d.meaning}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-fire mb-2">✗ {t("detail.unlucky")}</div>
              <div className="space-y-1.5">
                {deep.unlucky_directions.map((d) => (
                  <div key={d.category_key} className="flex items-start gap-2 text-sm">
                    <span className="chip element-fire w-10 justify-center">{d.direction}</span>
                    <div className="flex-1 min-w-0">
                      <div className="truncate"><b>{d.cn}</b> {d.en} · {d.direction_name}</div>
                      <div className="text-xs text-muted truncate">{d.meaning}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* --- Lifestyle palette ------------------------------------------ */}
      {deep && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-3">
            {t("dash.personalized")}
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-xs uppercase tracking-wider text-wood mb-1">{t("chart.colors_favor")}</div>
              <div className="flex flex-wrap gap-1.5">
                {deep.color_palette_favor.map((c) => <span key={c} className="chip element-wood text-xs">{c}</span>)}
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-fire mb-1">{t("chart.colors_avoid")}</div>
              <div className="flex flex-wrap gap-1.5">
                {deep.color_palette_avoid.map((c) => <span key={c} className="chip element-fire text-xs">{c}</span>)}
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("chart.gemstones")}</div>
              <div className="flex flex-wrap gap-1.5">
                {deep.gemstones.map((g) => <span key={g} className="chip element-earth text-xs">{g}</span>)}
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("chart.lucky_numbers")}</div>
              <div className="flex gap-1.5 flex-wrap">
                {deep.lucky_numbers.map((n) => (
                  <span key={n} className="font-display text-xl bg-earth-soft text-earth px-2 rounded">{n}</span>
                ))}
              </div>
              <div className="text-xs text-muted mt-2">
                {t("chart.best_direction")}: <b>{deep.best_direction}</b>
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-wood mb-1">{t("chart.foods_favor")}</div>
              <ul className="text-xs list-disc pl-5 text-muted">
                {deep.foods_favor.slice(0, 5).map((f) => <li key={f}>{f}</li>)}
              </ul>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-fire mb-1">{t("chart.foods_avoid")}</div>
              <ul className="text-xs list-disc pl-5 text-muted">
                {deep.foods_avoid.slice(0, 5).map((f) => <li key={f}>{f}</li>)}
              </ul>
            </div>
            <div className="sm:col-span-2">
              <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("chart.best_careers")}</div>
              <div className="flex flex-wrap gap-1.5">
                {deep.best_careers.map((c) => <span key={c} className="chip element-metal text-xs">{c}</span>)}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* --- Prevention / Enhancement -------------------------------- */}
      {deep && (deep.prevention.length > 0 || deep.enhancement.length > 0) && (
        <section className="grid md:grid-cols-2 gap-4">
          <div className="rounded-2xl border border-fire/30 bg-fire-soft/30 p-5">
            <div className="text-xs uppercase tracking-wider text-fire mb-2">⚠ {t("chart.prevention")}</div>
            <ul className="list-disc pl-5 text-sm space-y-1">
              {deep.prevention.map((p, i) => <li key={i}>{p}</li>)}
            </ul>
          </div>
          <div className="rounded-2xl border border-wood/30 bg-wood-soft/30 p-5">
            <div className="text-xs uppercase tracking-wider text-wood mb-2">✓ {t("chart.enhancement")}</div>
            <ul className="list-disc pl-5 text-sm space-y-1">
              {deep.enhancement.map((e, i) => <li key={i}>{e}</li>)}
            </ul>
          </div>
        </section>
      )}

      {/* --- Auxiliary stars ------------------------------------------ */}
      {deep && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-3">{t("detail.aux_stars")}</div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {Object.entries(deep.stars).map(([key, info]) => {
              const lbl = starLabels[key] || { cn: key, en: key };
              const active = info.present_in.length > 0;
              return (
                <div
                  key={key}
                  className={`rounded-xl border p-3 ${active ? "border-wood/40 bg-wood-soft/60" : "border-ink/10"}`}
                >
                  <div className="text-sm font-medium">{lbl.cn} · {lbl.en}</div>
                  <div className="text-xs mt-1">
                    {active
                      ? <span className="text-wood font-medium">{t("detail.star_present")}: {info.present_in.join(", ")}</span>
                      : <span className="text-muted">{t("detail.star_not_present")}</span>
                    }
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* --- Personality ---------------------------------------------- */}
      {deep && deep.personality_notes && deep.personality_notes.length > 0 && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.personality")}</div>
          <ul className="list-disc pl-5 text-sm space-y-1">
            {deep.personality_notes.map((n, i) => <li key={i}>{n}</li>)}
          </ul>
        </section>
      )}

      {error && <div className="text-fire text-sm">{error}</div>}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-2">
      <span className="text-muted min-w-[70px]">{label}:</span>
      <span className="font-medium text-ink">{value}</span>
    </div>
  );
}

function QuickStat({
  label, main, sub, tone,
}: {
  label: string;
  main: string;
  sub?: string;
  tone?: string;
}) {
  const toneCls = tone && elementClass[tone] ? elementClass[tone] : "bg-white";
  return (
    <div className="rounded-xl border border-ink/10 bg-white p-3">
      <div className="text-[10px] uppercase tracking-wider text-muted">{label}</div>
      <div className={`font-display text-2xl mt-1 ${tone ? "flex items-center gap-2" : ""}`}>
        {tone && <span className={`chip ${toneCls} text-[10px] w-6 justify-center`}>{tone}</span>}
        <span className="truncate">{main}</span>
      </div>
      {sub && <div className="text-[11px] text-muted mt-1 truncate">{sub}</div>}
    </div>
  );
}
