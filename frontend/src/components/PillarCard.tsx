import { Pillar } from "../api";

const elementClass: Record<string, string> = {
  wood: "element-wood",
  fire: "element-fire",
  earth: "element-earth",
  metal: "element-metal",
  water: "element-water",
};

export function PillarCard({ label, pillar }: { label: string; pillar: Pillar }) {
  return (
    <div className="pillar-card">
      <div className="text-xs uppercase tracking-wider text-muted">{label}</div>
      <div className="font-display text-4xl mt-1">{pillar.stem}{pillar.branch}</div>
      <div className="text-xs text-muted mt-1">{pillar.pinyin}</div>
      <div className="mt-3 flex gap-1">
        <span className={`chip ${elementClass[pillar.stem_element]}`}>{pillar.stem_element}</span>
        <span className={`chip ${elementClass[pillar.branch_element]}`}>{pillar.branch_element}</span>
      </div>
    </div>
  );
}

export function ElementBar({ elements }: { elements: Record<string, number> }) {
  const total = Object.values(elements).reduce((a, b) => a + b, 0) || 1;
  const order: Array<keyof typeof elements> = ["wood", "fire", "earth", "metal", "water"];
  return (
    <div>
      <div className="flex rounded-full overflow-hidden h-3 border border-ink/10">
        {order.map((e) => (
          <div
            key={e as string}
            className={elementClass[e as string].replace("text-", "")}
            style={{ width: `${((elements[e as string] || 0) / total) * 100}%` }}
            title={`${e as string}: ${(elements[e as string] || 0).toFixed(2)}`}
          />
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-2">
        {order.map((e) => (
          <span key={e as string} className={`chip ${elementClass[e as string]}`}>
            {e as string}: {(elements[e as string] || 0).toFixed(1)}
          </span>
        ))}
      </div>
    </div>
  );
}

export function ScoreRing({ score, label }: { score: number; label: string }) {
  const clamped = Math.max(0, Math.min(100, score));
  const color =
    clamped >= 75 ? "#2f8f5e" : clamped >= 55 ? "#b8864b" : clamped >= 35 ? "#c8a42d" : "#c8382d";
  const radius = 34;
  const circ = 2 * Math.PI * radius;
  const offset = circ * (1 - clamped / 100);
  return (
    <div className="flex flex-col items-center">
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r={radius} fill="none" stroke="#eee" strokeWidth="8" />
        <circle
          cx="45"
          cy="45"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 45 45)"
        />
        <text x="45" y="52" textAnchor="middle" className="font-display" fontSize="22" fill="#1a1a1a">
          {clamped}
        </text>
      </svg>
      <div className="text-xs uppercase tracking-wider text-muted mt-1">{label}</div>
    </div>
  );
}
