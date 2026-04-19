import { useEffect, useState } from "react";
import { api, FaceReading, FaceReadingRequest, Profile } from "../api";
import { CameraCapture } from "../components/CameraCapture";
import { HistorySidebar } from "../components/HistorySidebar";
import { useI18n } from "../i18n";

type Shape = FaceReadingRequest["face_shape"];
type Size = FaceReadingRequest["forehead"];
type Brow = FaceReadingRequest["brows"];
type Eye = FaceReadingRequest["eyes"];
type Nose = FaceReadingRequest["nose"];
type Mouth = FaceReadingRequest["mouth"];
type Ear = FaceReadingRequest["ears"];
type Chin = FaceReadingRequest["chin"];
type Cheek = FaceReadingRequest["cheeks"];
type Skin = FaceReadingRequest["skin"];

const SHAPES: Shape[] = ["round", "square", "oval", "long", "heart", "diamond"];
const FOREHEADS: Size[] = ["high", "medium", "low", "narrow", "wide"];
const BROWS: Brow[] = ["thick", "medium", "thin", "arched", "straight"];
const EYES: Eye[] = ["big", "medium", "small", "phoenix", "deep"];
const NOSES: Nose[] = ["straight", "high", "flat", "hooked", "small"];
const MOUTHS: Mouth[] = ["full", "medium", "thin", "wide", "small"];
const EARS: Ear[] = ["large", "medium", "small", "attached", "detached"];
const CHINS: Chin[] = ["strong", "rounded", "pointed", "double", "receding"];
const CHEEKS: Cheek[] = ["high", "full", "flat", "hollow"];
const SKINS: Skin[] = ["bright", "neutral", "dull", "ruddy"];

const DEFAULTS: FaceReadingRequest = {
  face_shape: "oval",
  forehead: "medium",
  brows: "medium",
  eyes: "medium",
  nose: "straight",
  mouth: "medium",
  ears: "medium",
  chin: "rounded",
  cheeks: "full",
  skin: "neutral",
};

export function FaceReadingPage() {
  const { t } = useI18n();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [form, setForm] = useState<FaceReadingRequest>(DEFAULTS);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FaceReading | null>(null);
  const [historyKey, setHistoryKey] = useState(0);
  const [openHistoryId, setOpenHistoryId] = useState<number | null>(null);

  useEffect(() => {
    api.listProfiles().then(setProfiles).catch(() => setProfiles([]));
  }, []);

  function setField<K extends keyof FaceReadingRequest>(k: K, v: FaceReadingRequest[K]) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function onAnalyze() {
    setBusy(true);
    setError(null);
    setResult(null);
    setOpenHistoryId(null);
    try {
      const payload: FaceReadingRequest = {
        ...form,
        profile_id: profileId === "" ? undefined : Number(profileId),
      };
      const r = await api.faceReading(payload);
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
          <p className="text-sm text-muted">{t("face.subtitle")}</p>
        </div>

        <section className="rounded-2xl border border-ink/10 bg-white p-5 space-y-4">
          <div className="grid md:grid-cols-[320px_1fr] gap-4">
            <CameraCapture facingMode="user" />
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
              <div className="text-xs uppercase tracking-wider text-muted mt-2">
                {t("face.section_form")}
              </div>

              <FieldSelect label={t("face.field_shape")} value={form.face_shape}
                options={SHAPES.map((s) => [s, t(`face.shape.${s}`)])}
                onChange={(v) => setField("face_shape", v as Shape)} />
              <FieldSelect label={t("face.field_forehead")} value={form.forehead}
                options={FOREHEADS.map((s) => [s, t(`face.size.${s}`)])}
                onChange={(v) => setField("forehead", v as Size)} />
              <FieldSelect label={t("face.field_brows")} value={form.brows}
                options={BROWS.map((b) => [b, t(b === "medium" ? "face.size.medium" : `face.brow.${b}`)])}
                onChange={(v) => setField("brows", v as Brow)} />
              <FieldSelect label={t("face.field_eyes")} value={form.eyes}
                options={EYES.map((e) => [e, t(e === "medium" ? "face.size.medium" : `face.eye.${e}`)])}
                onChange={(v) => setField("eyes", v as Eye)} />
              <FieldSelect label={t("face.field_nose")} value={form.nose}
                options={NOSES.map((n) => [n, t(n === "high" ? "face.size.high" : `face.nose.${n}`)])}
                onChange={(v) => setField("nose", v as Nose)} />
              <FieldSelect label={t("face.field_mouth")} value={form.mouth}
                options={MOUTHS.map((m) => [m, t(m === "medium" ? "face.size.medium" : `face.mouth.${m}`)])}
                onChange={(v) => setField("mouth", v as Mouth)} />
              <FieldSelect label={t("face.field_ears")} value={form.ears}
                options={EARS.map((e) => [e, t(e === "medium" ? "face.size.medium" : `face.ear.${e}`)])}
                onChange={(v) => setField("ears", v as Ear)} />
              <FieldSelect label={t("face.field_chin")} value={form.chin}
                options={CHINS.map((c) => [c, t(`face.chin.${c}`)])}
                onChange={(v) => setField("chin", v as Chin)} />
              <FieldSelect label={t("face.field_cheeks")} value={form.cheeks}
                options={CHEEKS.map((c) => [c, t(`face.cheek.${c}`)])}
                onChange={(v) => setField("cheeks", v as Cheek)} />
              <FieldSelect label={t("face.field_skin")} value={form.skin}
                options={SKINS.map((s) => [s, t(`face.skin.${s}`)])}
                onChange={(v) => setField("skin", v as Skin)} />

              <button
                type="button"
                onClick={onAnalyze}
                disabled={busy}
                className="btn-primary mt-2"
              >
                {busy ? t("face.analyzing") : t("face.analyze")}
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

function FieldSelect({ label, value, options, onChange }: {
  label: string;
  value: string;
  options: [string, string][];
  onChange: (v: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-xs text-muted">{label}</span>
      <select className="input mt-1" value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map(([v, lbl]) => <option key={v} value={v}>{lbl}</option>)}
      </select>
    </label>
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
          {t("face.features_breakdown")}
        </div>
        <ol className="space-y-2">
          {r.features.map((f, i) => (
            <li key={i} className="rounded-xl border border-ink/10 p-3">
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium">
                  {f.feature} · {f.trait}
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
