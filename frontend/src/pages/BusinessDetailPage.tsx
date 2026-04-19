import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, BusinessReading } from "../api";
import { ElementBar, ScoreRing } from "../components/PillarCard";
import { useI18n } from "../i18n";

const elementClass: Record<string, string> = {
  wood: "element-wood",
  fire: "element-fire",
  earth: "element-earth",
  metal: "element-metal",
  water: "element-water",
};

export function BusinessDetailPage() {
  const { t, lang } = useI18n();
  const { id } = useParams<{ id: string }>();
  const bizId = Number(id);
  const [data, setData] = useState<BusinessReading | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!bizId) return;
    api.businessReading(bizId, lang).then(setData).catch((e) => setError(String(e)));
  }, [bizId, lang]);

  if (error) return <div className="text-fire text-sm">{error}</div>;
  if (!data) return <div className="text-muted">{t("common.loading")}</div>;

  const best = data.owner_matches.find((m) => m.profile_id === data.best_match_profile_id);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 flex-wrap">
        <Link to="/businesses" className="text-sm text-muted hover:underline">← {t("biz.title")}</Link>
        <h1 className="font-display text-2xl">{data.business.name}</h1>
        {data.business.chinese_name && (
          <span className="font-display text-2xl text-muted">{data.business.chinese_name}</span>
        )}
        {data.business.is_main && <span className="chip element-fire">{t("profiles.main")}</span>}
      </div>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted">{t("biz.summary")}</div>
        <p className="text-sm mt-2">{data.summary}</p>
        <div className="mt-3 text-sm text-muted">
          {t("biz.opened_on")}: {new Date(data.business.open_datetime).toLocaleString()}
          {data.business.location ? ` · ${data.business.location}` : ""}
          {data.business.facing_direction ? ` · ${data.business.facing_direction}` : ""}
          {data.business.industry ? ` · ${data.business.industry}` : ""}
        </div>
      </section>

      {/* Business chart */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-2">
          {t("biz.chart_for_business")}
        </div>
        <div className="font-display text-2xl">{data.chart.chart_string}</div>
        <div className="mt-2 text-sm">
          {t("detail.day_master")}: <b>{data.chart.day_master.stem}</b> ({data.chart.day_master.element}) ·
          {t("detail.zodiac")}: <b>{data.chart.zodiac}</b> ·
          {t("detail.dominant")}: <b>{data.chart.dominant_element}</b> ·
          {t("detail.weakest")}: <b>{data.chart.weakest_element}</b>
        </div>
        <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-3">
          {data.chart.pillars.map((p) => (
            <div key={p.label} className="pillar-card">
              <div className="text-xs uppercase tracking-wider text-muted">{p.label}</div>
              <div className="font-display text-4xl mt-1">{p.stem}{p.branch}</div>
              <div className="text-xs text-muted">{p.pinyin}</div>
              <div className="mt-2 flex gap-1">
                <span className={`chip ${elementClass[p.stem_element]}`}>{p.stem_element}</span>
                <span className={`chip ${elementClass[p.branch_element]}`}>{p.branch_element}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4">
          <ElementBar elements={data.chart.elements} />
        </div>
      </section>

      {/* Owner compatibility */}
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
          <div className="text-xs uppercase tracking-wider text-muted">{t("biz.owner_match")}</div>
          {best && (
            <div className="text-xs">
              {t("biz.best_match")}: <b>{best.profile_name}</b>
            </div>
          )}
        </div>
        {data.owner_matches.length === 0 ? (
          <div className="text-sm text-muted">{t("biz.no_profiles")}</div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {data.owner_matches.map((m) => (
              <div
                key={m.profile_id}
                className={`rounded-xl border p-4 flex flex-col ${
                  m.profile_id === data.best_match_profile_id
                    ? "border-wood/40 bg-wood-soft/40"
                    : "border-ink/10 bg-white"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium">{m.profile_name}</div>
                  <ScoreRing score={m.score} label={t("biz.match_score")} />
                </div>
                <div className="text-xs text-muted mt-2">
                  <span className={`chip ${elementClass[m.dm_relation.a_element]}`}>{m.dm_relation.a_element}</span>
                  <span className="mx-1">↔</span>
                  <span className={`chip ${elementClass[m.dm_relation.b_element]}`}>{m.dm_relation.b_element}</span>
                </div>
                <div className="text-xs mt-2">{m.verdict}</div>
                <div className="text-[11px] text-muted mt-2">
                  {m.harmony_count} ♡ · {m.tension_count} ⚡
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Business name reading */}
      {data.name_reading && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("biz.name_reading")}</div>
          <div className="font-display text-3xl">{data.name_reading.name}</div>
          <p className="text-sm mt-2">{data.name_reading.summary}</p>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs uppercase text-muted">
                  <th className="text-left py-1">{t("name.grid")}</th>
                  <th className="text-left py-1">{t("name.grid_number")}</th>
                  <th className="text-left py-1">{t("name.grid_meaning")}</th>
                  <th className="text-left py-1">{t("name.grid_quality")}</th>
                </tr>
              </thead>
              <tbody>
                {(["heaven", "person", "earth", "total", "outer"] as const).map((k) => {
                  const g = data.name_reading!.grids[k];
                  const cn = { heaven: "天格", person: "人格", earth: "地格", total: "总格", outer: "外格" }[k];
                  const cls = g.quality === "auspicious" ? "element-wood" : g.quality === "inauspicious" ? "element-fire" : "element-earth";
                  return (
                    <tr key={k} className="border-t border-ink/5">
                      <td className="py-1.5"><b>{cn}</b></td>
                      <td className="font-display text-lg">{g.number}</td>
                      <td>{g.en}</td>
                      <td><span className={`chip ${cls}`}>{g.quality}</span></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Premises feng shui */}
      {data.feng_shui ? (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <div className="text-xs uppercase tracking-wider text-muted">{t("biz.premises_fs")}</div>
              <div className="font-display text-xl mt-1">{data.feng_shui.summary}</div>
              <div className="text-sm mt-1">
                {t("fs.house_sits")} {data.feng_shui.house_sitting} ({data.feng_shui.house_group}) ·
                {data.feng_shui.person_house_match
                  ? <span className="chip element-wood ml-1">{t("fs.match")}</span>
                  : <span className="chip element-fire ml-1">{t("fs.mismatch")}</span>}
              </div>
            </div>
            <ScoreRing score={data.feng_shui.overall_score} label={t("fs.score")} />
          </div>
          <div className="mt-4 grid md:grid-cols-2 gap-3">
            <div>
              <div className="text-sm font-medium text-wood mb-1">✓ {t("detail.lucky")}</div>
              <ul className="text-xs space-y-0.5">
                {data.feng_shui.lucky_directions.map((d) => (
                  <li key={d.category_key}>
                    <span className="chip element-wood mr-1 w-10 justify-center">{d.direction}</span>
                    <b>{d.cn} {d.en}</b> — {d.meaning}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <div className="text-sm font-medium text-fire mb-1">✗ {t("detail.unlucky")}</div>
              <ul className="text-xs space-y-0.5">
                {data.feng_shui.unlucky_directions.map((d) => (
                  <li key={d.category_key}>
                    <span className="chip element-fire mr-1 w-10 justify-center">{d.direction}</span>
                    <b>{d.cn} {d.en}</b> — {d.meaning}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="mt-3">
            <div className="text-xs uppercase tracking-wider text-muted mb-1">{t("fs.recommendations")}</div>
            <ul className="list-disc pl-5 text-sm space-y-1">
              {data.feng_shui.recommendations.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </div>
        </section>
      ) : data.business.facing_direction ? null : (
        <section className="rounded-2xl border border-dashed border-ink/20 bg-white p-5 text-sm text-muted">
          {t("biz.add_facing_for_fs")}
        </section>
      )}
    </div>
  );
}
