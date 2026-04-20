import { useEffect, useState } from "react";
import { api, FaceReading, Profile } from "../api";
import { CameraCapture } from "../components/CameraCapture";
import { HistorySidebar } from "../components/HistorySidebar";
import { useI18n } from "../i18n";

export function FaceReadingPage() {
  const { t } = useI18n();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [image, setImage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FaceReading | null>(null);
  const [historyKey, setHistoryKey] = useState(0);
  const [openHistoryId, setOpenHistoryId] = useState<number | null>(null);

  useEffect(() => {
    api.listProfiles().then(setProfiles).catch(() => setProfiles([]));
  }, []);

  async function onAnalyze() {
    if (!image) return;
    setBusy(true);
    setError(null);
    setResult(null);
    setOpenHistoryId(null);
    try {
      const r = await api.faceReading({
        image,
        profile_id: profileId === "" ? undefined : Number(profileId),
      });
      setResult(r);
      setHistoryKey((k) => k + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  async function openHistory(id: number) {
    try {
      const item = await api.getHistory<FaceReading>(id);
      setResult(item.payload);
      setOpenHistoryId(id);
    } catch { /* ignore */ }
  }

  return (
    <div className="grid lg:grid-cols-[1fr_240px] gap-4">
      <div className="space-y-5 min-w-0">
        <div>
          <h1 className="font-display text-2xl">{t("face.title")}</h1>
          <p className="text-sm text-muted">{t("face.ai_subtitle")}</p>
        </div>

        <section className="rounded-2xl border border-ink/10 bg-white p-5 space-y-4">
          <div className="grid md:grid-cols-[360px_1fr] gap-4 items-start">
            <CameraCapture
              facingMode="user"
              onCapture={(dataUrl) => { setImage(dataUrl); setResult(null); }}
              onClear={() => setImage(null)}
            />
            <div className="space-y-3">
              <label className="block">
                <span className="text-xs text-muted">{t("face.link_profile")}</span>
                <select
                  className="input mt-1"
                  value={profileId}
                  onChange={(e) => setProfileId(e.target.value === "" ? "" : Number(e.target.value))}
                >
                  <option value="">{t("face.select_profile")}</option>
                  {profiles.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </label>

              <div className="rounded-xl border border-ink/10 bg-parchment/50 p-3 text-xs text-muted leading-relaxed">
                {t("face.how_it_works")}
              </div>

              <button
                type="button"
                onClick={onAnalyze}
                disabled={busy || !image}
                className="btn-primary w-full"
              >
                {busy ? t("face.analyzing_ai") : image ? t("face.analyze") : t("face.need_photo")}
              </button>
              {error && <div className="text-fire text-sm">{error}</div>}
            </div>
          </div>
        </section>

        {result && <FaceResult r={result} />}
      </div>
      <HistorySidebar
        kind="face"
        refreshKey={historyKey}
        onOpen={openHistory}
        currentId={openHistoryId}
      />
    </div>
  );
}

function FaceResult({ r }: { r: FaceReading }) {
  const { t } = useI18n();
  const areas: [string, number][] = [
    [t("face.career"), r.career_score],
    [t("face.wealth"), r.wealth_score],
    [t("face.relationships"), r.relationships_score],
    [t("face.health"), r.health_score],
    [t("face.family"), r.family_score],
    [t("face.overall"), r.overall_score],
  ];
  return (
    <>
      <section className="rounded-2xl border border-earth/30 bg-gradient-to-br from-parchment via-white to-earth-soft/40 p-6">
        <div className="text-xs uppercase tracking-wider text-muted">
          {t("face.personality")} · <span className={`chip element-${r.governing_element}`}>{r.governing_element}</span>
        </div>
        <p className="mt-2 text-sm leading-relaxed">{r.personality_summary}</p>
      </section>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-3">{t("face.areas")}</div>
        <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
          {areas.map(([label, score]) => (
            <div key={label} className="rounded-xl border border-ink/10 p-3 text-center">
              <div className="font-mono text-2xl">{score}</div>
              <div className="text-xs text-muted">{label}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-ink/10 bg-white p-5 space-y-2">
        <div className="text-xs uppercase tracking-wider text-muted">{t("face.san_ting")}</div>
        <Row title={t("face.upper")}  text={r.san_ting_upper} />
        <Row title={t("face.middle")} text={r.san_ting_middle} />
        <Row title={t("face.lower")}  text={r.san_ting_lower} />
      </section>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-2">
          {t("face.detected_features")}
        </div>
        <div className="text-[11px] text-muted mb-3">{t("face.detected_hint")}</div>
        <ol className="space-y-2">
          {r.features.map((f, i) => (
            <li key={i} className="rounded-xl border border-ink/10 p-3">
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium">
                  {f.feature} · <span className="text-muted">{f.trait}</span>
                </div>
                <span className="chip element-earth text-xs">{f.score}</span>
              </div>
              <div className="text-xs text-muted">{f.palace}</div>
              <p className="text-sm mt-1">{f.verdict}</p>
            </li>
          ))}
        </ol>
      </section>

      <div className="grid md:grid-cols-3 gap-3">
        <ListCard title={t("face.strengths")} items={r.strengths} tone="wood" />
        <ListCard title={t("face.watchouts")} items={r.watchouts} tone="metal" />
        <ListCard title={t("face.recs")} items={r.recommendations} tone="water" />
      </div>
    </>
  );
}

function Row({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <div className="text-xs text-muted">{title}</div>
      <p className="text-sm">{text}</p>
    </div>
  );
}

function ListCard({ title, items, tone }: { title: string; items: string[]; tone: string }) {
  if (!items?.length) return null;
  return (
    <section className={`rounded-2xl border border-${tone}/40 bg-${tone}-soft/60 p-4`}>
      <div className="text-xs uppercase tracking-wider text-muted mb-2">{title}</div>
      <ul className="text-sm space-y-1 list-disc list-inside">
        {items.map((s, i) => <li key={i}>{s}</li>)}
      </ul>
    </section>
  );
}
