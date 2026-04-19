import { FormEvent, useEffect, useState } from "react";
import { api, DeepNumerology, GeneratedNumberResponse, Profile } from "../api";
import { ElementBar, ScoreRing } from "../components/PillarCard";
import { HistorySidebar } from "../components/HistorySidebar";
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
  const [historyKey, setHistoryKey] = useState(0);
  const [openHistoryId, setOpenHistoryId] = useState<number | null>(null);
  const [generated, setGenerated] = useState<GeneratedNumberResponse | null>(null);
  const [genBusy, setGenBusy] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);

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
      const item = await api.getHistory<DeepNumerology>(id);
      setResult(item.payload);
      setNumber(item.label);
      setOpenHistoryId(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  }

  async function generate(purposeArg?: string, lengthArg?: number, count = 10, prefixArg?: string) {
    if (profileId === "") return;
    setGenBusy(true);
    setGenError(null);
    try {
      const out = await api.numerologyGenerate(
        Number(profileId),
        purposeArg || type,
        lengthArg,
        count,
        prefixArg,
      );
      setGenerated(out);
    } catch (err) {
      setGenError(err instanceof Error ? err.message : "Failed");
    } finally {
      setGenBusy(false);
    }
  }

  async function useGenerated(n: string) {
    setNumber(n);
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.numerologyDeep(n, profileId === "" ? undefined : Number(profileId), lang));
      setHistoryKey((k) => k + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid lg:grid-cols-[1fr_240px] gap-4">
      <div className="space-y-6 min-w-0">
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

      {/* Lucky number generator — visible once a profile is linked */}
      <GeneratorCard
        profileLinked={profileId !== ""}
        profileName={profiles.find((p) => p.id === profileId)?.name ?? ""}
        purpose={type}
        busy={genBusy}
        error={genError}
        generated={generated}
        onGenerate={(purposeArg, lengthArg, count, prefixArg) =>
          generate(purposeArg, lengthArg, count, prefixArg)
        }
        onUse={useGenerated}
      />

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
      <div className="order-first lg:order-none">
        <HistorySidebar
          kind="numerology"
          refreshKey={historyKey}
          currentId={openHistoryId}
          onOpen={openHistory}
        />
      </div>
    </div>
  );
}


type GenProps = {
  profileLinked: boolean;
  profileName: string;
  purpose: string;
  busy: boolean;
  error: string | null;
  generated: GeneratedNumberResponse | null;
  onGenerate: (purpose: string, length: number | undefined, count: number, prefix: string) => void;
  onUse: (n: string) => void;
};

function GeneratorCard({
  profileLinked,
  profileName,
  purpose,
  busy,
  error,
  generated,
  onGenerate,
  onUse,
}: GenProps) {
  const { t } = useI18n();
  const [localPurpose, setLocalPurpose] = useState(purpose);
  const [length, setLength] = useState<number | "">("");
  const [count, setCount] = useState(10);
  const [prefix, setPrefix] = useState("");
  const [copied, setCopied] = useState<string | null>(null);

  const header = profileLinked
    ? t("gen.subtitle").replace("{profile}", profileName)
    : t("gen.need_profile");

  async function copy(s: string) {
    try {
      await navigator.clipboard.writeText(s);
      setCopied(s);
      setTimeout(() => setCopied(null), 1500);
    } catch {/* ignore */}
  }

  return (
    <section className="rounded-2xl border border-earth/30 bg-gradient-to-br from-parchment via-white to-earth-soft/40 p-5">
      <div className="flex items-center justify-between flex-wrap gap-2 mb-2">
        <div className="text-xs uppercase tracking-wider text-muted">
          ✨ {t("gen.title")}
        </div>
      </div>
      <p className="text-sm text-muted mb-3">{header}</p>

      {profileLinked && (
        <>
          <div className="grid sm:grid-cols-[1fr_1fr_1fr_1fr_auto] gap-2 items-end">
            <label className="block">
              <span className="text-xs text-muted">{t("gen.purpose")}</span>
              <select className="input mt-1" value={localPurpose} onChange={(e) => setLocalPurpose(e.target.value)}>
                <option value="phone">{t("numerology.type_phone")}</option>
                <option value="bank">{t("numerology.type_bank")}</option>
                <option value="car">{t("numerology.type_car")}</option>
                <option value="id">{t("numerology.type_id")}</option>
                <option value="credit">{t("numerology.type_credit")}</option>
                <option value="custom">custom</option>
              </select>
            </label>
            <label className="block">
              <span className="text-xs text-muted">{t("gen.length")}</span>
              <input
                type="number"
                min={4}
                max={20}
                className="input mt-1"
                value={length}
                onChange={(e) => setLength(e.target.value === "" ? "" : Number(e.target.value))}
                placeholder="auto"
              />
            </label>
            <label className="block">
              <span className="text-xs text-muted">{t("gen.count")}</span>
              <input
                type="number"
                min={1}
                max={30}
                className="input mt-1"
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
              />
            </label>
            <label className="block">
              <span className="text-xs text-muted">{t("gen.prefix")}</span>
              <input
                className="input mt-1 font-mono"
                value={prefix}
                onChange={(e) => setPrefix(e.target.value)}
                placeholder={t("gen.prefix_ph")}
                maxLength={8}
              />
            </label>
            <button
              type="button"
              disabled={busy}
              className="btn-primary"
              onClick={() => onGenerate(localPurpose, length === "" ? undefined : Number(length), count, prefix)}
            >
              {busy ? t("gen.generating") : t("gen.button")}
            </button>
          </div>

          {error && <div className="text-fire text-sm mt-2">{error}</div>}

          {generated && generated.candidates.length > 0 && (
            <div className="mt-4">
              <div className="text-xs text-muted mb-2">
                Useful God: <b>{generated.useful_god}</b> · favored digits {generated.preferred_digits.join(", ")} · avoid {generated.digits_to_avoid.join(", ") || "—"}
              </div>
              <ol className="space-y-2">
                {generated.candidates.map((c, i) => (
                  <li key={i} className="flex items-center gap-2 flex-wrap rounded-xl border border-ink/10 bg-white p-3">
                    <span className="text-xs text-muted w-6">{i + 1}.</span>
                    <span className="font-mono text-base font-semibold tracking-wider">{c.number}</span>
                    <span className="chip element-wood text-xs">W {c.wealth}</span>
                    <span className="chip element-metal text-xs">S {c.safety}</span>
                    <span className="chip element-water text-xs">H {c.health}</span>
                    <span className="chip element-earth text-xs">★ {c.overall}</span>
                    <span className="text-[11px] text-muted">
                      ✓ {c.auspicious_pair_count} / ✗ {c.inauspicious_pair_count} {t("gen.pairs")}
                    </span>
                    <div className="ml-auto flex gap-2">
                      <button
                        className="btn-ghost text-xs"
                        onClick={() => copy(c.number)}
                      >
                        {copied === c.number ? t("ref.copied") : t("gen.copy")}
                      </button>
                      <button
                        className="btn-primary text-xs py-1"
                        onClick={() => onUse(c.number)}
                      >
                        {t("gen.use")}
                      </button>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </>
      )}
    </section>
  );
}
