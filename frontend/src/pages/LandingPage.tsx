import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useI18n } from "../i18n";

/**
 * Public landing page. Atmospheric hero with a slowly-rotating 3D Ba Gua
 * compass, floating Four-Pillar cards, and scroll-revealed feature sections.
 * Animations are CSS-only — no heavy 3D deps. See index.css for keyframes.
 */
export function LandingPage() {
  const { t, lang, setLang } = useI18n();
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Scroll-reveal: observe elements tagged with `.reveal` and add
  // `.reveal--in` when they cross into the viewport.
  useEffect(() => {
    const nodes = document.querySelectorAll(".reveal");
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            e.target.classList.add("reveal--in");
            io.unobserve(e.target);
          }
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -50px 0px" },
    );
    nodes.forEach((n) => io.observe(n));
    return () => io.disconnect();
  }, []);

  return (
    <div ref={scrollRef} className="min-h-screen bg-parchment text-ink overflow-x-hidden">
      {/* ---- Top bar ------------------------------------------------- */}
      <header className="sticky top-0 z-30 border-b border-ink/5 bg-parchment/70 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center gap-3">
          <Link to="/welcome" className="flex items-center gap-2">
            <img src="/favicon.svg" alt="" className="w-8 h-8 rounded-lg" />
            <span className="font-display text-lg">八字 · Metaphysical Suite</span>
          </Link>
          <div className="flex-1" />
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value as "en" | "zh" | "ms")}
            className="text-xs rounded-lg border border-ink/15 bg-white/70 px-2 py-1.5"
            aria-label={t("common.language")}
          >
            <option value="en">EN</option>
            <option value="zh">中文</option>
            <option value="ms">BM</option>
          </select>
          <Link to="/login" className="btn-ghost text-sm">{t("land.sign_in")}</Link>
          <Link to="/register" className="btn-primary text-sm">{t("land.sign_up")}</Link>
        </div>
      </header>

      {/* ---- Hero ---------------------------------------------------- */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="cloud-sheet cloud-sheet--a" />
          <div className="cloud-sheet cloud-sheet--b" />
        </div>

        <div className="relative mx-auto max-w-6xl px-4 pt-14 pb-20 md:pt-24 md:pb-28 grid md:grid-cols-[1.1fr_1fr] gap-8 md:gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-earth/40 bg-white/60 px-3 py-1 text-xs text-earth backdrop-blur">
              <span className="w-1.5 h-1.5 rounded-full bg-earth animate-pulse" />
              {t("land.badge")}
            </div>
            <h1 className="mt-5 font-display text-5xl md:text-7xl leading-[1.05] tracking-tight">
              <span className="block">{t("land.hero_line1")}</span>
              <span className="block bg-gradient-to-br from-earth via-water to-ink bg-clip-text text-transparent">
                {t("land.hero_line2")}
              </span>
            </h1>
            <p className="mt-6 text-lg text-muted max-w-xl leading-relaxed">
              {t("land.hero_sub")}
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="btn-primary text-base px-5 py-3">
                {t("land.cta_primary")}
              </Link>
              <Link to="/login" className="btn-ghost text-base px-5 py-3">
                {t("land.cta_secondary")}
              </Link>
            </div>
            <div className="mt-8 flex items-center gap-6 text-xs text-muted">
              <BadgeLine label={t("land.badge_free")} />
              <BadgeLine label={t("land.badge_langs")} />
              <BadgeLine label={t("land.badge_ai")} />
            </div>
          </div>

          {/* Compass mandala */}
          <div className="relative compass-stage h-[440px] md:h-[520px]">
            <div className="sun-glow" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="compass-3d">
                <BaGuaCompass />
              </div>
            </div>
            {/* Orbiting element dots */}
            <div className="absolute inset-0">
              <ElementOrbit color="bg-wood"  radius={220} delay={0}  />
              <ElementOrbit color="bg-fire"  radius={220} delay={-5} />
              <ElementOrbit color="bg-earth" radius={220} delay={-10}/>
              <ElementOrbit color="bg-metal" radius={220} delay={-15}/>
              <ElementOrbit color="bg-water" radius={220} delay={-20}/>
            </div>
          </div>
        </div>
      </section>

      {/* ---- Ba Zi pillars showcase --------------------------------- */}
      <section className="relative py-20 md:py-28 bg-gradient-to-b from-parchment via-white to-parchment">
        <div className="mx-auto max-w-6xl px-4">
          <div className="max-w-2xl reveal">
            <div className="text-xs uppercase tracking-[0.2em] text-earth font-semibold">
              {t("land.section_bazi_kicker")}
            </div>
            <h2 className="mt-2 font-display text-4xl md:text-5xl">
              {t("land.section_bazi_title")}
            </h2>
            <p className="mt-4 text-muted text-lg leading-relaxed">
              {t("land.section_bazi_sub")}
            </p>
          </div>

          {/* Floating 3D four-pillars */}
          <div className="mt-14 perspective-[1400px]" style={{ perspective: "1400px" }}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
              {[
                { cn: "甲", branch: "子", label: t("dash.year"),  element: "wood",  zi: "甲子" },
                { cn: "丙", branch: "午", label: t("dash.month"), element: "fire",  zi: "丙午" },
                { cn: "戊", branch: "辰", label: t("dash.day"),   element: "earth", zi: "戊辰" },
                { cn: "壬", branch: "申", label: t("dash.hour"),  element: "water", zi: "壬申" },
              ].map((p, i) => (
                <div
                  key={i}
                  className="pillar-float reveal"
                  data-delay={i + 1}
                  style={{ transformStyle: "preserve-3d" }}
                >
                  <div className={`rounded-3xl border border-${p.element}/30 bg-white/80 p-5 backdrop-blur shadow-xl`}
                       style={{ boxShadow: "0 20px 40px -24px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.7)" }}>
                    <div className="text-[10px] uppercase tracking-[0.2em] text-muted">{p.label}</div>
                    <div className={`mt-3 font-display text-6xl md:text-7xl text-${p.element}`}>{p.cn}</div>
                    <div className="font-display text-3xl md:text-4xl text-muted">{p.branch}</div>
                    <div className={`mt-3 chip element-${p.element} text-[10px]`}>{p.element}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ---- Feature grid ------------------------------------------- */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="cloud-sheet cloud-sheet--a" style={{ opacity: 0.4 }} />
        </div>
        <div className="relative mx-auto max-w-6xl px-4">
          <div className="text-center max-w-2xl mx-auto reveal">
            <div className="text-xs uppercase tracking-[0.2em] text-water font-semibold">
              {t("land.section_features_kicker")}
            </div>
            <h2 className="mt-2 font-display text-4xl md:text-5xl">
              {t("land.section_features_title")}
            </h2>
          </div>

          <div className="mt-14 grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            <FeatureCard
              glyph="命"
              accent="water"
              title={t("land.feat_bazi_title")}
              body={t("land.feat_bazi_body")}
              delay={1}
            />
            <FeatureCard
              glyph="宅"
              accent="wood"
              title={t("land.feat_fengshui_title")}
              body={t("land.feat_fengshui_body")}
              delay={2}
            />
            <FeatureCard
              glyph="数"
              accent="earth"
              title={t("land.feat_num_title")}
              body={t("land.feat_num_body")}
              delay={3}
            />
            <FeatureCard
              glyph="名"
              accent="metal"
              title={t("land.feat_name_title")}
              body={t("land.feat_name_body")}
              delay={4}
            />
            <FeatureCard
              glyph="相"
              accent="fire"
              title={t("land.feat_face_title")}
              body={t("land.feat_face_body")}
              delay={5}
            />
            <FeatureCard
              glyph="問"
              accent="earth"
              title={t("land.feat_chat_title")}
              body={t("land.feat_chat_body")}
              delay={5}
            />
          </div>
        </div>
      </section>

      {/* ---- Feng Shui 3D compass spotlight ------------------------- */}
      <section className="relative py-20 md:py-28 bg-gradient-to-b from-white via-parchment to-white overflow-hidden">
        <div className="mx-auto max-w-6xl px-4 grid md:grid-cols-[1fr_1.1fr] gap-10 items-center">
          <div className="relative compass-stage h-[360px] md:h-[480px] reveal">
            <div className="sun-glow" style={{ background: "radial-gradient(circle at center, rgba(47, 143, 94, 0.25) 0%, transparent 55%)" }} />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="compass-3d">
                <FengShuiDial />
              </div>
            </div>
          </div>

          <div className="reveal" data-delay="1">
            <div className="text-xs uppercase tracking-[0.2em] text-wood font-semibold">
              {t("land.section_fs_kicker")}
            </div>
            <h2 className="mt-2 font-display text-4xl md:text-5xl">
              {t("land.section_fs_title")}
            </h2>
            <p className="mt-4 text-muted text-lg leading-relaxed">
              {t("land.section_fs_sub")}
            </p>
            <ul className="mt-6 space-y-2 text-sm">
              <CheckLine text={t("land.fs_point1")} />
              <CheckLine text={t("land.fs_point2")} />
              <CheckLine text={t("land.fs_point3")} />
              <CheckLine text={t("land.fs_point4")} />
            </ul>
          </div>
        </div>
      </section>

      {/* ---- Pricing strip ------------------------------------------ */}
      <section className="relative py-20 md:py-28">
        <div className="mx-auto max-w-5xl px-4">
          <div className="text-center reveal">
            <div className="text-xs uppercase tracking-[0.2em] text-earth font-semibold">
              {t("land.pricing_kicker")}
            </div>
            <h2 className="mt-2 font-display text-4xl md:text-5xl">{t("land.pricing_title")}</h2>
            <p className="mt-3 text-muted">{t("land.pricing_sub")}</p>
          </div>
          <div className="mt-10 grid md:grid-cols-3 gap-4">
            <PriceTier
              tier={t("land.tier_free")}
              price="$0"
              sub={t("land.tier_free_sub")}
              features={[t("land.tier_free_f1"), t("land.tier_free_f2"), t("land.tier_free_f3")]}
              delay={1}
            />
            <PriceTier
              tier={t("land.tier_payg")}
              price="$8"
              sub={t("land.tier_payg_sub")}
              features={[t("land.tier_payg_f1"), t("land.tier_payg_f2"), t("land.tier_payg_f3")]}
              delay={2}
            />
            <PriceTier
              tier={t("land.tier_unlimited")}
              price="$88"
              sub={t("land.tier_unlimited_sub")}
              features={[t("land.tier_unlimited_f1"), t("land.tier_unlimited_f2"), t("land.tier_unlimited_f3")]}
              highlight
              delay={3}
            />
          </div>
        </div>
      </section>

      {/* ---- CTA Aurora --------------------------------------------- */}
      <section className="relative py-24 md:py-32 overflow-hidden">
        <div className="aurora" />
        <div className="relative mx-auto max-w-3xl px-4 text-center reveal">
          <h2 className="font-display text-4xl md:text-6xl leading-tight">
            {t("land.final_cta_title")}
          </h2>
          <p className="mt-4 text-muted text-lg">{t("land.final_cta_sub")}</p>
          <div className="mt-8 flex justify-center gap-3 flex-wrap">
            <Link to="/register" className="btn-primary text-base px-6 py-3">
              {t("land.cta_primary")}
            </Link>
            <Link to="/login" className="btn-ghost text-base px-6 py-3">
              {t("land.cta_secondary")}
            </Link>
          </div>
        </div>
      </section>

      {/* ---- Footer ------------------------------------------------- */}
      <footer className="border-t border-ink/10 py-8 text-center text-xs text-muted">
        {t("common.footer")}
      </footer>
    </div>
  );
}

// ============================================================================
// Subcomponents
// ============================================================================

function BadgeLine({ label }: { label: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        <polyline points="20 6 9 17 4 12" />
      </svg>
      {label}
    </span>
  );
}

function CheckLine({ text }: { text: string }) {
  return (
    <li className="flex gap-2 items-start">
      <span className="mt-0.5 w-5 h-5 rounded-full bg-wood/15 text-wood flex items-center justify-center shrink-0">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </span>
      <span>{text}</span>
    </li>
  );
}

function FeatureCard({
  glyph, accent, title, body, delay,
}: {
  glyph: string;
  accent: "wood" | "fire" | "earth" | "metal" | "water";
  title: string;
  body: string;
  delay: number;
}) {
  return (
    <article className="glass-card reveal" data-delay={delay}>
      <div className={`font-display text-5xl text-${accent}`}>{glyph}</div>
      <h3 className="mt-3 font-display text-xl">{title}</h3>
      <p className="mt-2 text-sm text-muted leading-relaxed">{body}</p>
    </article>
  );
}

function PriceTier({
  tier, price, sub, features, highlight, delay,
}: {
  tier: string;
  price: string;
  sub: string;
  features: string[];
  highlight?: boolean;
  delay: number;
}) {
  const { t } = useI18n();
  return (
    <article
      className={`reveal rounded-3xl p-6 flex flex-col ${
        highlight
          ? "border-2 border-earth/50 bg-gradient-to-br from-earth-soft/60 via-white to-parchment shadow-xl"
          : "border border-ink/10 bg-white"
      }`}
      data-delay={delay}
    >
      {highlight && (
        <div className="self-start mb-3 chip bg-earth text-white">
          {t("billing.best_value")}
        </div>
      )}
      <div className="text-xs uppercase tracking-[0.2em] text-muted font-semibold">{tier}</div>
      <div className="mt-2 flex items-baseline gap-1">
        <span className="font-display text-5xl">{price}</span>
        <span className="text-sm text-muted">{sub}</span>
      </div>
      <ul className="mt-5 space-y-2 text-sm flex-1">
        {features.map((f, i) => (
          <CheckLine key={i} text={f} />
        ))}
      </ul>
      <Link
        to="/register"
        className={`mt-6 text-center rounded-lg px-4 py-2 text-sm font-medium ${
          highlight ? "bg-ink text-parchment hover:bg-black" : "border border-ink/15 hover:bg-ink/5"
        }`}
      >
        {t("land.tier_cta")}
      </Link>
    </article>
  );
}

// ---- 3D-ish Ba Gua compass (SVG) -----------------------------------------

const TRIGRAMS = [
  { sym: "☰", name: "乾", en: "Heaven"   },
  { sym: "☱", name: "兑", en: "Lake"     },
  { sym: "☲", name: "离", en: "Fire"     },
  { sym: "☳", name: "震", en: "Thunder"  },
  { sym: "☷", name: "坤", en: "Earth"    },
  { sym: "☶", name: "艮", en: "Mountain" },
  { sym: "☵", name: "坎", en: "Water"    },
  { sym: "☴", name: "巽", en: "Wind"     },
];

function BaGuaCompass() {
  const size = 360;
  const cx = size / 2;
  const cy = size / 2;
  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className="drop-shadow-2xl"
      role="img"
      aria-label="Ba Gua compass"
    >
      {/* Outer ring with trigrams — slow clockwise */}
      <g className="compass-ring" style={{ transformOrigin: `${cx}px ${cy}px` }}>
        <circle cx={cx} cy={cy} r={170} fill="none" stroke="#b8864b" strokeOpacity="0.35" strokeWidth="1" />
        <circle cx={cx} cy={cy} r={150} fill="none" stroke="#b8864b" strokeOpacity="0.2" strokeWidth="1" />
        {TRIGRAMS.map((t, i) => {
          const angle = (i * 360) / TRIGRAMS.length - 90;
          const r = 160;
          const x = cx + r * Math.cos((angle * Math.PI) / 180);
          const y = cy + r * Math.sin((angle * Math.PI) / 180);
          return (
            <g key={i}>
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="32"
                fill="#1a1a1a"
                style={{ fontFamily: "Noto Serif SC, serif" }}
              >
                {t.sym}
              </text>
            </g>
          );
        })}
      </g>

      {/* Middle ring with the Chinese names — reverse rotation */}
      <g className="compass-ring compass-ring--reverse" style={{ transformOrigin: `${cx}px ${cy}px` }}>
        <circle cx={cx} cy={cy} r={120} fill="none" stroke="#1e4f7a" strokeOpacity="0.25" strokeWidth="1" />
        {TRIGRAMS.map((t, i) => {
          const angle = (i * 360) / TRIGRAMS.length - 90;
          const r = 110;
          const x = cx + r * Math.cos((angle * Math.PI) / 180);
          const y = cy + r * Math.sin((angle * Math.PI) / 180);
          return (
            <text
              key={i}
              x={x}
              y={y}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize="16"
              fill="#6b6b6b"
              style={{ fontFamily: "Noto Serif SC, serif" }}
            >
              {t.name}
            </text>
          );
        })}
      </g>

      {/* Taiji core — stays still */}
      <g>
        <circle cx={cx} cy={cy} r={80} fill="url(#taiji-bg)" stroke="#1a1a1a" strokeOpacity="0.3" />
        <defs>
          <radialGradient id="taiji-bg" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#faf6ed" />
            <stop offset="100%" stopColor="#f1e3c9" />
          </radialGradient>
        </defs>
        {/* S-curve taiji */}
        <path
          d={`
            M ${cx} ${cy - 70}
            A 70 70 0 0 1 ${cx} ${cy + 70}
            A 35 35 0 0 1 ${cx} ${cy}
            A 35 35 0 0 0 ${cx} ${cy - 70}
            Z
          `}
          fill="#1a1a1a"
        />
        <circle cx={cx} cy={cy - 35} r={8} fill="#faf6ed" />
        <circle cx={cx} cy={cy + 35} r={8} fill="#1a1a1a" />
      </g>
    </svg>
  );
}

// ---- Feng Shui 8-direction dial -------------------------------------------

const DIRECTIONS = [
  { label: "N",  cn: "坎" },
  { label: "NE", cn: "艮" },
  { label: "E",  cn: "震" },
  { label: "SE", cn: "巽" },
  { label: "S",  cn: "离" },
  { label: "SW", cn: "坤" },
  { label: "W",  cn: "兑" },
  { label: "NW", cn: "乾" },
];

function FengShuiDial() {
  const size = 360;
  const cx = size / 2;
  const cy = size / 2;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="drop-shadow-2xl">
      <defs>
        <radialGradient id="fs-bg" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#faf6ed" />
          <stop offset="100%" stopColor="#d5ebd9" />
        </radialGradient>
      </defs>
      <circle cx={cx} cy={cy} r={170} fill="url(#fs-bg)" stroke="#2f8f5e" strokeOpacity="0.3" />
      <g className="compass-ring" style={{ transformOrigin: `${cx}px ${cy}px` }}>
        {DIRECTIONS.map((d, i) => {
          const angle = (i * 360) / DIRECTIONS.length - 90;
          const r = 140;
          const x1 = cx + (r - 20) * Math.cos((angle * Math.PI) / 180);
          const y1 = cy + (r - 20) * Math.sin((angle * Math.PI) / 180);
          const x2 = cx + r * Math.cos((angle * Math.PI) / 180);
          const y2 = cy + r * Math.sin((angle * Math.PI) / 180);
          const tx = cx + (r - 40) * Math.cos((angle * Math.PI) / 180);
          const ty = cy + (r - 40) * Math.sin((angle * Math.PI) / 180);
          return (
            <g key={i}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#1a1a1a" strokeOpacity="0.4" strokeWidth="2" />
              <text x={tx} y={ty} textAnchor="middle" dominantBaseline="central" fontSize="18" fill="#1a1a1a" style={{ fontFamily: "Noto Serif SC, serif" }}>
                {d.cn}
              </text>
            </g>
          );
        })}
      </g>
      {/* Directional needle */}
      <g className="compass-ring compass-ring--reverse" style={{ transformOrigin: `${cx}px ${cy}px` }}>
        <polygon points={`${cx},${cy - 90} ${cx - 10},${cy} ${cx},${cy + 90} ${cx + 10},${cy}`} fill="#c8382d" opacity="0.8" />
        <circle cx={cx} cy={cy} r={10} fill="#1a1a1a" />
        <circle cx={cx} cy={cy} r={4} fill="#faf6ed" />
      </g>
      {DIRECTIONS.map((d, i) => {
        const angle = (i * 360) / DIRECTIONS.length - 90;
        const r = 190;
        const x = cx + r * Math.cos((angle * Math.PI) / 180);
        const y = cy + r * Math.sin((angle * Math.PI) / 180);
        return (
          <text
            key={`lbl-${i}`}
            x={x}
            y={y}
            textAnchor="middle"
            dominantBaseline="central"
            fontSize="11"
            fill="#6b6b6b"
            style={{ fontFamily: "Inter, sans-serif" }}
          >
            {d.label}
          </text>
        );
      })}
    </svg>
  );
}

function ElementOrbit({
  color, radius, delay,
}: {
  color: string;
  radius: number;
  delay: number;
}) {
  return (
    <span
      className={`orbit-dot ${color} shadow-lg`}
      style={{
        // @ts-expect-error CSS custom property
        "--r": `${radius}px`,
        animationDelay: `${delay}s`,
      }}
      aria-hidden
    />
  );
}
