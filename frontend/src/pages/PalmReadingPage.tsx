import { useEffect, useState } from "react";
import { api, PalmReading, PalmReadingRequest, Profile } from "../api";
import { CameraCapture } from "../components/CameraCapture";
import { HistorySidebar } from "../components/HistorySidebar";
import { useI18n } from "../i18n";

type HandShape = PalmReadingRequest["hand_shape"];
type Hand = PalmReadingRequest["dominant_hand"];
type FingerLen = PalmReadingRequest["finger_length"];
type LineLen = PalmReadingRequest["life_length"];
type LineDep = PalmReadingRequest["life_depth"];
type Marriage = PalmReadingRequest["marriage_lines"];

const HAND_SHAPES: HandShape[] = ["earth", "air", "water", "fire"];
const HANDS: Hand[] = ["right", "left"];
const FINGERS: FingerLen[] = ["short", "medium", "long"];
const LINE_LENS: LineLen[] = ["long", "medium", "short", "absent"];
const LINE_DEPS: LineDep[] = ["deep", "medium", "shallow", "broken"];
const MARRIAGE: Marriage[] = ["none", "one", "two", "many"];

const DEFAULTS: PalmReadingRequest = {
  hand_shape: "earth",
  dominant_hand: "right",
  finger_length: "medium",
  life_length: "medium",  life_depth: "medium",
  heart_length: "medium", heart_depth: "medium",
  head_length: "medium",  head_depth: "medium",
  fate_length: "medium",  fate_depth: "medium",
  marriage_lines: "one",
};

export function PalmReadingPage() {
  const { t } = useI18n();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [form, setForm] = useState<PalmReadingRequest>(DEFAULTS);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PalmReading | null>(null);
  const [historyKey, setHistoryKey] = useState(0);
  const [openHistoryId, setOpenHistoryId] = useState<number | null>(null);

  useEffect(() => {
    api.listProfiles().then(setProfiles).catch(() => setProfiles([]));
  }, []);

  function setField<K extends keyof PalmReadingRequest>(k: K, v: PalmReadingRequest[K]) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function onAnalyze() {
    setBusy(true);
    setError(null);
    setResult(null);
    setOpenHistoryId(null);
    try {
      const payload: PalmReadingRequest = {
        ...form,
        profile_id: profileId === "" ? undefined : Number(profileId),
      };
      const r = await api.palmReading(payload);
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
      const item = await api.getHistory<PalmReading>(id);
      setResult(item.payload);
      setOpenHistoryId(id);
    } catch { /* ignore */ }
  }

  return (
    <div className="grid lg:grid-cols-[1fr_240px] gap-4">
      <div className="space-y-5 min-w-0">
        <div>
          <h1 className="font-display text-2xl">{t("palm.title")}</h1>
          <p className="text-sm text-muted">{t("palm.subtitle")}</p>
        </div>

        <section className="rounded-2xl border border-ink/10 bg-white p-5 space-y-4">
          <div className="grid md:grid-cols-[320px_1fr] gap-4">
            <CameraCapture facingMode="environment" />
            <div className="space-y-3">
              <label className="block">
                <span className="text-xs text-muted">{t("palm.link_profile")}</span>
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
                {t("palm.section_shape")}
              </div>
              <FieldSelect label={t("palm.hand_shape")} value={form.hand_shape}
                options={HAND_SHAPES.map((s) => [s, t(`palm.shape.${s}`)])}
                onChange={(v) => setField("hand_shape", v as HandShape)} />
              <FieldSelect label={t("palm.dominant_hand")} value={form.dominant_hand}
                options={HANDS.map((h) => [h, t(`palm.hand.${h}`)])}
                onChange={(v) => setField("dominant_hand", v as Hand)} />
              <FieldSelect label={t("palm.finger_length")} value={form.finger_length}
                options={FINGERS.map((f) => [f, t(`palm.finger.${f}`)])}
                onChange={(v) => setField("finger_length", v as FingerLen)} />

              <div className="text-xs uppercase tracking-wider text-muted mt-3">
                {t("palm.section_lines")}
              </div>
              <LinePair
                label={t("palm.life_line")}
                length={form.life_length} depth={form.life_depth}
                onLength={(v) => setField("life_length", v as LineLen)}
                onDepth={(v) => setField("life_depth", v as LineDep)}
              />
              <LinePair
                label={t("palm.heart_line")}
                length={form.heart_length} depth={form.heart_depth}
                onLength={(v) => setField("heart_length", v as LineLen)}
                onDepth={(v) => setField("heart_depth", v as LineDep)}
              />
              <LinePair
                label={t("palm.head_line")}
                length={form.head_length} depth={form.head_depth}
                onLength={(v) => setField("head_length", v as LineLen)}
                onDepth={(v) => setField("head_depth", v as LineDep)}
              />
              <LinePair
                label={t("palm.fate_line")}
                length={form.fate_length} depth={form.fate_depth}
                onLength={(v) => setField("fate_length", v as LineLen)}
                onDepth={(v) => setField("fate_depth", v as LineDep)}
              />
              <FieldSelect label={t("palm.marriage_lines")} value={form.marriage_lines}
                options={MARRIAGE.map((m) => [m, t(`palm.mar.${m}`)])}
                onChange={(v) => setField("marriage_lines", v as Marriage)} />

              <button type="button" onClick={onAnalyze} disabled={busy} className="btn-primary mt-2">
                {busy ? t("palm.analyzing") : t("palm.analyze")}
              </button>
              {error && <div className="text-fire text-sm">{error}</div>}
            </div>
          </div>
        </section>

        {result && <PalmResult r={result} />}
      </div>
      <HistorySidebar
        kind="palm"
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

function LinePair(props: {
  label: string;
  length: string;
  depth: string;
  onLength: (v: string) => void;
  onDepth: (v: string) => void;
}) {
  const { t } = useI18n();
  return (
    <div className="rounded-xl border border-ink/10 p-3">
      <div className="text-sm font-medium mb-2">{props.label}</div>
      <div className="grid grid-cols-2 gap-2">
        <FieldSelect
          label={t("palm.length")}
          value={props.length}
          options={LINE_LENS.map((l) => [l, t(`palm.len.${l}`)])}
          onChange={props.onLength}
        />
        <FieldSelect
          label={t("palm.depth")}
          value={props.depth}
          options={LINE_DEPS.map((d) => [d, t(`palm.dep.${d}`)])}
          onChange={props.onDepth}
        />
      </div>
    </div>
  );
}

function PalmResult({ r }: { r: PalmReading }) {
  const { t } = useI18n();
  const areas: [string, number][] = [
    [t("palm.vitality"), r.vitality_score],
    [t("palm.love"), r.love_score],
    [t("palm.intellect"), r.intellect_score],
    [t("palm.career"), r.career_score],
    [t("palm.marriage"), r.marriage_score],
    [t("palm.overall"), r.overall_score],
  ];
  return (
    <>
      <section className="rounded-2xl border border-earth/30 bg-gradient-to-br from-parchment via-white to-earth-soft/40 p-6">
        <div className="text-xs uppercase tracking-wider text-muted">
          <span className={`chip element-${r.governing_element}`}>{r.hand_shape_label}</span>
        </div>
        <p className="mt-2 text-sm leading-relaxed">{r.personality_summary}</p>
        <p className="mt-1 text-xs text-muted">{r.finger_interpretation}</p>
      </section>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
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
        <Row title={t("palm.life_path")}   text={r.life_path} />
        <Row title={t("palm.love_path")}   text={r.love_path} />
        <Row title={t("palm.career_path")} text={r.career_path} />
      </section>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-xs uppercase tracking-wider text-muted mb-2">{t("palm.section_lines")}</div>
        <ol className="space-y-2">
          {r.lines.map((ln, i) => (
            <li key={i} className="rounded-xl border border-ink/10 p-3">
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium">{ln.chinese} · {ln.line}</div>
                <span className="chip element-earth text-xs">{ln.score}</span>
              </div>
              <p className="text-sm mt-1">{ln.length_verdict}</p>
              <p className="text-xs text-muted">{ln.depth_verdict}</p>
            </li>
          ))}
        </ol>
      </section>

      <div className="grid md:grid-cols-3 gap-3">
        <ListCard title={t("palm.strengths")} items={r.strengths} tone="wood" />
        <ListCard title={t("palm.watchouts")} items={r.watchouts} tone="metal" />
        <ListCard title={t("palm.recs")} items={r.recommendations} tone="water" />
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
