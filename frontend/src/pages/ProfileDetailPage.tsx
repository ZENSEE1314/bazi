import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  api,
  Daily,
  DailyCalendarDay,
  DeepBaZi,
  Profile,
} from "../api";
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
  nobleman: { cn: "天乙贵人", en: "Nobleman" },
  peach_blossom: { cn: "桃花", en: "Peach Blossom" },
  academic: { cn: "文昌", en: "Intelligence" },
  sky_horse: { cn: "驿马", en: "Sky Horse" },
};

const dayLabelColor: Record<DailyCalendarDay["label"], string> = {
  excellent: "bg-wood text-white",
  good: "bg-wood-soft text-wood",
  neutral: "bg-metal-soft text-ink",
  caution: "bg-earth-soft text-earth",
  difficult: "bg-fire-soft text-fire",
};

function formatDate(d: Date) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export function ProfileDetailPage() {
  const { t } = useI18n();
  const { id } = useParams<{ id: string }>();
  const profileId = Number(id);

  const [profile, setProfile] = useState<Profile | null>(null);
  const [deep, setDeep] = useState<DeepBaZi | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Daily luck date picker
  const today = useMemo(() => new Date(), []);
  const [selectedDate, setSelectedDate] = useState<string>(formatDate(today));
  const [daily, setDaily] = useState<Daily | null>(null);

  // Calendar month
  const [calMonth, setCalMonth] = useState<{ year: number; month: number }>({
    year: today.getFullYear(),
    month: today.getMonth() + 1,
  });
  const [calendar, setCalendar] = useState<DailyCalendarDay[] | null>(null);

  useEffect(() => {
    if (!profileId) return;
    Promise.all([api.getProfile(profileId), api.deep(profileId)])
      .then(([p, d]) => {
        setProfile(p);
        setDeep(d);
      })
      .catch((e) => setError(String(e)));
  }, [profileId]);

  useEffect(() => {
    if (!profileId) return;
    api
      .daily(profileId, selectedDate)
      .then(setDaily)
      .catch((e) => setError(String(e)));
  }, [profileId, selectedDate]);

  useEffect(() => {
    if (!profileId) return;
    api
      .calendar(profileId, calMonth.year, calMonth.month)
      .then(setCalendar)
      .catch((e) => setError(String(e)));
  }, [profileId, calMonth.year, calMonth.month]);

  if (error) return <div className="text-fire">{error}</div>;
  if (!profile || !deep) return <div className="text-muted">Loading…</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 flex-wrap">
        <Link to="/profiles" className="text-sm text-muted hover:underline">
          {t("detail.back")}
        </Link>
        <h1 className="font-display text-2xl">{profile.name}</h1>
        {profile.is_main && <span className="chip element-fire">{t("profiles.main")}</span>}
        <span className="text-sm text-muted">
          {new Date(profile.birth_datetime).toLocaleString()}
          {profile.birth_location ? ` · ${profile.birth_location}` : ""}
          {profile.gender ? ` · ${profile.gender}` : ""}
        </span>
      </div>

      {/* --- Header summary ------------------------------------------------ */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted">{t("detail.four_pillars")}</div>
            <div className="font-display text-3xl mt-1">{deep.chart_string}</div>
            <div className="mt-2 text-sm">
              {t("detail.day_master")}: <b>{deep.day_master.stem}</b> ({deep.day_master.element}) ·
              {t("detail.zodiac")}: <b>{deep.zodiac}</b> · {t("detail.dominant")}: <b>{deep.dominant_element}</b> ·
              {t("detail.weakest")}: <b>{deep.weakest_element}</b>
            </div>
            <div className="mt-1 text-sm text-muted">
              {t("detail.strength")}: <span className="font-medium">{deep.day_master.strength_level}</span> ({deep.day_master.strength_score.toFixed(2)}) ·
              {t("detail.useful_god")}: <span className="font-medium">{deep.day_master.useful_god}</span> ·
              {t("detail.avoid_god")}: <span className="font-medium">{deep.day_master.avoid_god}</span>
            </div>
          </div>
          {deep.life_kua && (
            <div className="rounded-xl border border-ink/10 p-3 min-w-[180px]">
              <div className="text-xs uppercase tracking-wider text-muted">{t("detail.life_kua")}</div>
              <div className="font-display text-2xl">{deep.life_kua.number} · {deep.life_kua.trigram_cn}</div>
              <div className="text-sm text-muted">
                {deep.life_kua.trigram_pinyin} · {deep.life_kua.element} · {deep.life_kua.group === "East" ? t("detail.group_east") : t("detail.group_west")}
              </div>
              <div className="text-xs text-muted mt-1">{t("detail.seat")}: {deep.life_kua.seated_direction}</div>
            </div>
          )}
        </div>

        {/* Pillars */}
        <div className="mt-5 grid grid-cols-2 md:grid-cols-4 gap-3">
          {deep.pillars.map((p) => (
            <div key={p.label} className="pillar-card">
              <div className="text-xs uppercase tracking-wider text-muted">{p.label}</div>
              <div className="font-display text-4xl mt-1">
                {p.stem}{p.branch}
              </div>
              <div className="text-xs text-muted">{p.pinyin}</div>
              <div className="mt-2 flex gap-1">
                <span className={`chip ${elementClass[p.stem_element]}`}>{p.stem_element}</span>
                <span className={`chip ${elementClass[p.branch_element]}`}>{p.branch_element}</span>
              </div>
              <div className="mt-2 text-xs text-muted">
                {p.stem_ten_god_en ? (
                  <span>{t("detail.stem")}: <b>{p.stem_ten_god_cn}</b> {p.stem_ten_god_en}</span>
                ) : (
                  <span><b>{t("detail.day_master_word")}</b></span>
                )}
              </div>
              <div className="mt-1 text-[11px] text-muted italic">
                {t("detail.nayin")}: {p.nayin_cn} ({p.nayin_en})
              </div>
              {p.hidden_stems.length > 0 && (
                <div className="mt-2 text-[11px] text-muted border-t border-ink/5 pt-1 w-full">
                  <div className="font-semibold">{t("detail.hidden")}:</div>
                  {p.hidden_stems.map((h, i) => (
                    <div key={i}>
                      {h.stem} ({h.element}) · {h.ten_god_cn} {h.ten_god_en} · {h.weight.toFixed(1)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Five Factors + Raw Elements */}
        <div className="mt-6 grid md:grid-cols-2 gap-5">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.five_factors")}</div>
            <div className="space-y-1">
              {deep.five_factors.map((f) => (
                <div key={f.key} className="flex items-center gap-2 text-sm">
                  <span className={`chip ${elementClass[f.element]}`}>{f.element}</span>
                  <span className="w-28">{f.label}</span>
                  <div className="flex-1 h-2 bg-ink/5 rounded-full overflow-hidden">
                    <div
                      className={elementClass[f.element].split(" ").find((c) => c.startsWith("bg-")) || "bg-ink/20"}
                      style={{ width: `${f.percent}%`, height: "100%" }}
                    />
                  </div>
                  <span className="text-xs text-muted w-12 text-right">{f.percent.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.five_elements_raw")}</div>
            <ElementBar elements={deep.elements} />
          </div>
        </div>
      </section>

      {/* --- Day Master Verdict ------------------------------------------- */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted">{t("detail.day_master_verdict")}</div>
        <p className="mt-2 text-sm">{deep.day_master.seasonal_influence}</p>
        <p className="mt-2 text-sm">{deep.day_master.explanation}</p>
      </section>

      {/* --- Stars --------------------------------------------------------- */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-3">{t("detail.aux_stars")}</div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {Object.entries(deep.stars).map(([key, info]) => {
            const lbl = starLabels[key] || { cn: key, en: key };
            const active = info.present_in.length > 0;
            return (
              <div
                key={key}
                className={`rounded-xl border p-3 ${active ? "border-wood/40 bg-wood-soft" : "border-ink/10 bg-white"}`}
              >
                <div className="text-sm font-medium">{lbl.cn} {lbl.en}</div>
                <div className="text-xs text-muted mt-1">
                  {t("detail.star_trigger")}: <b>{info.trigger_branch ?? "—"}</b>
                </div>
                <div className="text-xs mt-1">
                  {active ? (
                    <>{t("detail.star_present")}: {info.present_in.join(", ")}</>
                  ) : (
                    <span className="text-muted">{t("detail.star_not_present")}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* --- 8 Mansions --------------------------------------------------- */}
      {deep.life_kua && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-3">
            {t("detail.eight_mansions")} {deep.life_kua.number} ({deep.life_kua.trigram_cn})
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm font-medium text-wood mb-2">✓ {t("detail.lucky")}</div>
              <div className="space-y-1">
                {deep.lucky_directions.map((d) => (
                  <div key={d.category_key} className="flex items-start gap-2 text-sm">
                    <span className="chip element-wood w-10 justify-center">{d.direction}</span>
                    <div className="flex-1">
                      <div><b>{d.cn} {d.en}</b> · {d.direction_name}</div>
                      <div className="text-xs text-muted">{d.meaning}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-fire mb-2">✗ {t("detail.unlucky")}</div>
              <div className="space-y-1">
                {deep.unlucky_directions.map((d) => (
                  <div key={d.category_key} className="flex items-start gap-2 text-sm">
                    <span className="chip element-fire w-10 justify-center">{d.direction}</span>
                    <div className="flex-1">
                      <div><b>{d.cn} {d.en}</b> · {d.direction_name}</div>
                      <div className="text-xs text-muted">{d.meaning}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* --- Life areas --------------------------------------------------- */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-3">{t("detail.life_areas")}</div>
        <div className="grid sm:grid-cols-5 gap-3">
          {Object.entries(deep.life_areas).map(([area, v]) => (
            <div key={area} className="rounded-xl border border-ink/10 p-3">
              <div className="text-xs uppercase text-muted">{area}</div>
              <div className="font-display text-2xl mt-1">{v.strength.toFixed(1)}</div>
              <div className="text-[11px] text-muted mt-1">{v.gods.join(", ")}</div>
            </div>
          ))}
        </div>
      </section>

      {/* --- Prevention / Enhancement ------------------------------------ */}
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

      {/* --- Lifestyle palette ------------------------------------------ */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-xs uppercase tracking-wider text-wood mb-1">{t("chart.colors_favor")}</div>
            <div className="flex flex-wrap gap-1.5">
              {deep.color_palette_favor.map((c) => <span key={c} className="chip element-wood">{c}</span>)}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-fire mb-1">{t("chart.colors_avoid")}</div>
            <div className="flex flex-wrap gap-1.5">
              {deep.color_palette_avoid.map((c) => <span key={c} className="chip element-fire">{c}</span>)}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("chart.gemstones")}</div>
            <div className="flex flex-wrap gap-1.5">
              {deep.gemstones.map((g) => <span key={g} className="chip element-earth">{g}</span>)}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("chart.lucky_numbers")}</div>
            <div className="flex gap-1.5">
              {deep.lucky_numbers.map((n) => (
                <span key={n} className="font-display text-2xl bg-earth-soft text-earth px-2 rounded">{n}</span>
              ))}
            </div>
            <div className="text-xs text-muted mt-2">{t("chart.best_direction")}: <b>{deep.best_direction}</b></div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-wood mb-1">{t("chart.foods_favor")}</div>
            <ul className="text-xs list-disc pl-5">
              {deep.foods_favor.slice(0, 5).map((f) => <li key={f}>{f}</li>)}
            </ul>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-fire mb-1">{t("chart.foods_avoid")}</div>
            <ul className="text-xs list-disc pl-5">
              {deep.foods_avoid.slice(0, 5).map((f) => <li key={f}>{f}</li>)}
            </ul>
          </div>
          <div className="sm:col-span-2">
            <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("chart.best_careers")}</div>
            <div className="flex flex-wrap gap-1.5">
              {deep.best_careers.map((c) => <span key={c} className="chip element-metal">{c}</span>)}
            </div>
          </div>
        </div>
      </section>

      {/* --- Career / Wealth / Love / Health ------------------------------ */}
      <section className="grid md:grid-cols-2 gap-4">
        <div className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.career")}</div>
          <div className="flex flex-wrap gap-1.5">
            {deep.career_paths.map((c) => (
              <span key={c} className="chip element-metal">{c}</span>
            ))}
          </div>
        </div>
        <div className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.wealth_strategy")}</div>
          <ul className="list-disc pl-5 text-sm space-y-1">
            {deep.wealth_strategy.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
        <div className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.love_outlook")}</div>
          <ul className="list-disc pl-5 text-sm space-y-1">
            {deep.love_outlook.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
        <div className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.health_watch")}</div>
          <ul className="list-disc pl-5 text-sm space-y-1">
            {deep.health_watch.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      </section>

      {/* --- Relations ---------------------------------------------------- */}
      {Object.values(deep.relations).some((arr) => arr.length > 0) && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-3">{t("detail.branch_relations")}</div>
          <div className="space-y-3">
            {Object.entries(deep.relations).map(([kind, items]) =>
              items.length > 0 ? (
                <div key={kind}>
                  <div className="text-sm font-semibold capitalize">{kind.replace("_", " ")}</div>
                  <ul className="list-disc pl-5 text-sm space-y-1 mt-1">
                    {items.map((it, i) => (
                      <li key={i}>
                        <b>{it.branches.join(" ")}</b>
                        {it.transforms_to && <> → <span className={`chip ${elementClass[it.transforms_to]}`}>{it.transforms_to}</span></>}
                        {" "}· {it.note}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null
            )}
          </div>
        </section>
      )}

      {/* --- Annual + Luck Pillars --------------------------------------- */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.annual_luck")} · {deep.annual_luck.year}</div>
        <div className="font-display text-2xl">
          {deep.annual_luck.stem}{deep.annual_luck.branch}
          <span className="ml-2 chip element-wood">{deep.annual_luck.stem_ten_god_cn} {deep.annual_luck.stem_ten_god_en}</span>
        </div>
        <p className="text-sm text-muted mt-2">{deep.annual_luck.note}</p>

        <div className="text-xs uppercase tracking-wider text-muted mt-5 mb-2">{t("detail.ten_year_luck")}</div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-xs uppercase">
                <th className="text-left py-1">{t("detail.age")}</th>
                <th className="text-left py-1">{t("detail.pillar")}</th>
                <th className="text-left py-1">{t("detail.pinyin")}</th>
                <th className="text-left py-1">{t("detail.ten_god")}</th>
                <th className="text-left py-1">{t("detail.elements")}</th>
                <th className="text-left py-1">{t("detail.nayin")}</th>
              </tr>
            </thead>
            <tbody>
              {deep.luck_pillars.map((lp) => (
                <tr key={lp.index} className="border-t border-ink/5">
                  <td className="py-1.5">{lp.start_age}-{lp.end_age - 1}</td>
                  <td className="font-display text-lg">{lp.stem}{lp.branch}</td>
                  <td className="text-muted">{lp.pinyin}</td>
                  <td>{lp.stem_ten_god_cn} {lp.stem_ten_god_en}</td>
                  <td>
                    <span className={`chip ${elementClass[lp.stem_element]} mr-1`}>{lp.stem_element}</span>
                    <span className={`chip ${elementClass[lp.branch_element]}`}>{lp.branch_element}</span>
                  </td>
                  <td className="text-muted text-xs">{lp.nayin_en}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* --- Daily picker -------------------------------------------------- */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted">{t("detail.daily_reading")}</div>
            <div className="mt-1 flex items-center gap-2">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="input w-auto"
              />
              <button className="btn-ghost text-xs" onClick={() => setSelectedDate(formatDate(new Date()))}>
                {t("common.today")}
              </button>
            </div>
          </div>
          {daily && <ScoreRing score={daily.score} label={t("dash.luck")} />}
        </div>
        {daily && (
          <>
            <div className="font-display text-xl mt-3">
              {daily.day_pillar.stem}{daily.day_pillar.branch} <span className="text-muted text-base">({daily.day_pillar.pinyin})</span>
            </div>
            <p className="mt-1 text-sm">{daily.summary}</p>
            {daily.supportive_elements.length > 0 && (
              <div className="mt-3">
                <div className="text-xs uppercase tracking-wider text-wood mb-1">{t("dash.supportive")}</div>
                <ul className="list-disc pl-5 text-sm space-y-0.5">
                  {daily.supportive_elements.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
            {daily.clashing_elements.length > 0 && (
              <div className="mt-3">
                <div className="text-xs uppercase tracking-wider text-fire mb-1">{t("dash.friction")}</div>
                <ul className="list-disc pl-5 text-sm space-y-0.5">
                  {daily.clashing_elements.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
          </>
        )}
      </section>

      {/* --- Monthly calendar ---------------------------------------------- */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="flex items-center justify-between flex-wrap gap-3 mb-3">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted">{t("detail.calendar_title")}</div>
            <div className="font-display text-xl">
              {new Date(calMonth.year, calMonth.month - 1, 1).toLocaleString("default", {
                month: "long",
                year: "numeric",
              })}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              className="btn-ghost text-xs"
              onClick={() => {
                const d = new Date(calMonth.year, calMonth.month - 2, 1);
                setCalMonth({ year: d.getFullYear(), month: d.getMonth() + 1 });
              }}
            >
              ←
            </button>
            <button
              className="btn-ghost text-xs"
              onClick={() => {
                const now = new Date();
                setCalMonth({ year: now.getFullYear(), month: now.getMonth() + 1 });
              }}
            >
              {t("detail.this_month")}
            </button>
            <button
              className="btn-ghost text-xs"
              onClick={() => {
                const d = new Date(calMonth.year, calMonth.month, 1);
                setCalMonth({ year: d.getFullYear(), month: d.getMonth() + 1 });
              }}
            >
              →
            </button>
          </div>
        </div>

        {calendar ? (
          <>
            <div className="grid grid-cols-7 gap-1 text-xs text-muted text-center mb-1">
              {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d) => <div key={d}>{d}</div>)}
            </div>
            <CalendarGrid days={calendar} year={calMonth.year} month={calMonth.month} onPick={setSelectedDate} />
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className={`chip ${dayLabelColor.excellent}`}>{t("detail.legend_excellent")}</span>
              <span className={`chip ${dayLabelColor.good}`}>{t("detail.legend_good")}</span>
              <span className={`chip ${dayLabelColor.neutral}`}>{t("detail.legend_neutral")}</span>
              <span className={`chip ${dayLabelColor.caution}`}>{t("detail.legend_caution")}</span>
              <span className={`chip ${dayLabelColor.difficult}`}>{t("detail.legend_difficult")}</span>
            </div>
          </>
        ) : (
          <div className="text-muted text-sm">Loading…</div>
        )}
      </section>

      {/* --- Personality --------------------------------------------------- */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("detail.personality")}</div>
        <ul className="list-disc pl-5 text-sm space-y-1">
          {deep.personality_notes.map((n, i) => <li key={i}>{n}</li>)}
        </ul>
      </section>
    </div>
  );
}


function CalendarGrid({
  days,
  year,
  month,
  onPick,
}: {
  days: DailyCalendarDay[];
  year: number;
  month: number;
  onPick: (iso: string) => void;
}) {
  // Figure out the day-of-week of the 1st (Mon=0 .. Sun=6).
  const first = new Date(year, month - 1, 1);
  const jsDow = first.getDay(); // 0=Sun .. 6=Sat
  const leading = (jsDow + 6) % 7; // 0=Mon

  const cells: (DailyCalendarDay | null)[] = [];
  for (let i = 0; i < leading; i++) cells.push(null);
  for (const d of days) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);

  return (
    <div className="grid grid-cols-7 gap-1">
      {cells.map((cell, i) => {
        if (!cell) return <div key={i} className="aspect-square" />;
        const day = parseInt(cell.date.slice(-2), 10);
        return (
          <button
            key={i}
            onClick={() => onPick(cell.date)}
            className={`aspect-square rounded-lg text-left p-1.5 text-xs transition hover:ring-2 hover:ring-ink/20 ${dayLabelColor[cell.label]}`}
            title={`${cell.date} · ${cell.day_pillar_cn} · score ${cell.score}`}
          >
            <div className="font-medium">{day}</div>
            <div className="font-display text-[13px] leading-none mt-1">{cell.day_pillar_cn}</div>
            <div className="text-[10px] opacity-80 mt-0.5">{cell.score}</div>
          </button>
        );
      })}
    </div>
  );
}
