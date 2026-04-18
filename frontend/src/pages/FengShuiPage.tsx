import { FormEvent, useEffect, useState } from "react";
import { api, FengShuiReading, Profile } from "../api";
import { ScoreRing } from "../components/PillarCard";

const DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] as const;
const DIR_NAMES: Record<string, string> = {
  N: "North", NE: "Northeast", E: "East", SE: "Southeast",
  S: "South", SW: "Southwest", W: "West", NW: "Northwest",
};
const ROOMS = [
  { key: "main_door",  label: "Main door faces" },
  { key: "bed_head",   label: "Bed head points" },
  { key: "desk",       label: "Desk faces" },
  { key: "stove",      label: "Stove sits" },
  { key: "living_room",label: "Living room faces" },
  { key: "kids_room",  label: "Kids room faces" },
];

export function FengShuiPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState<number | "">("");
  const [facing, setFacing] = useState<string>("S");
  const [address, setAddress] = useState("");
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [rooms, setRooms] = useState<Record<string, string>>({});
  const [result, setResult] = useState<FengShuiReading | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.listProfiles().then((list) => {
      setProfiles(list);
      const main = list.find((p) => p.is_main) ?? list[0];
      if (main) setProfileId(main.id);
    }).catch((e) => setError(String(e)));
  }, []);

  function pickCurrentLocation() {
    if (!navigator.geolocation) {
      setError("Your browser does not support geolocation.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLatitude(pos.coords.latitude);
        setLongitude(pos.coords.longitude);
      },
      (err) => setError("Geolocation: " + err.message),
      { enableHighAccuracy: false, timeout: 8000 },
    );
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (profileId === "") { setError("Pick a profile first"); return; }
    setBusy(true); setError(null); setResult(null);
    try {
      setResult(
        await api.fengShui(
          Number(profileId),
          facing,
          rooms,
          address || undefined,
          latitude ?? undefined,
          longitude ?? undefined,
        ),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl">Feng Shui — Home Reading</h1>
        <p className="text-sm text-muted">
          Enter your home's main-door facing direction and key room directions.
          We compare them against your Life Kua (八宅) to tell you what's good,
          what's bad, and what to change.
        </p>
      </div>

      <form onSubmit={onSubmit} className="rounded-2xl border border-ink/10 bg-white p-5 space-y-4">
        <div className="grid sm:grid-cols-2 gap-3">
          <label className="block">
            <span className="text-xs text-muted">Occupant profile (needs gender)</span>
            <select className="input mt-1" value={profileId}
              onChange={(e) => setProfileId(e.target.value === "" ? "" : Number(e.target.value))} required>
              <option value="">Select…</option>
              {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </label>
          <label className="block">
            <span className="text-xs text-muted">House facing direction</span>
            <select className="input mt-1" value={facing} onChange={(e) => setFacing(e.target.value)} required>
              {DIRECTIONS.map((d) => <option key={d} value={d}>{d} — {DIR_NAMES[d]}</option>)}
            </select>
          </label>
        </div>
        <div className="grid sm:grid-cols-[1fr_auto] gap-3 items-end">
          <label className="block">
            <span className="text-xs text-muted">Address (optional)</span>
            <input className="input mt-1" value={address} onChange={(e) => setAddress(e.target.value)} placeholder="Street, city" />
          </label>
          <button type="button" onClick={pickCurrentLocation} className="btn-ghost text-sm">
            📍 Use my GPS location
          </button>
        </div>
        {(latitude != null && longitude != null) && (
          <div className="text-xs text-muted">
            GPS: {latitude.toFixed(4)}, {longitude.toFixed(4)}
          </div>
        )}

        <div>
          <div className="text-xs uppercase tracking-wider text-muted mb-2">Room directions (optional)</div>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
            {ROOMS.map((r) => (
              <label key={r.key} className="block">
                <span className="text-xs text-muted">{r.label}</span>
                <select
                  className="input mt-1"
                  value={rooms[r.key] || ""}
                  onChange={(e) => setRooms({ ...rooms, [r.key]: e.target.value })}
                >
                  <option value="">—</option>
                  {DIRECTIONS.map((d) => <option key={d} value={d}>{d}</option>)}
                </select>
              </label>
            ))}
          </div>
        </div>

        <button type="submit" disabled={busy} className="btn-primary">
          {busy ? "Analyzing…" : "Analyze Home"}
        </button>
      </form>

      {error && <div className="text-fire text-sm">{error}</div>}

      {result && (
        <>
          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <div className="text-xs uppercase tracking-wider text-muted">Overall</div>
                <div className="font-display text-xl mt-1">{result.summary}</div>
                <div className="mt-2 text-sm">
                  Your Kua: <b>{result.life_kua_number}</b> ({result.life_kua_group} group) ·
                  House sits {result.house_sitting} ({result.house_group} group) ·
                  {result.person_house_match ? <span className="chip element-wood ml-1">MATCH</span> : <span className="chip element-fire ml-1">MISMATCH</span>}
                </div>
                <p className="text-sm text-muted mt-2">{result.match_note}</p>
              </div>
              <ScoreRing score={result.overall_score} label="Score" />
            </div>
          </section>

          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-2">Your Directions</div>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm font-medium text-wood mb-1">✓ Lucky</div>
                <ul className="text-sm space-y-1">
                  {result.lucky_directions.map((d) => (
                    <li key={d.category_key}>
                      <span className="chip element-wood mr-2 w-10 justify-center">{d.direction}</span>
                      <b>{d.cn} {d.en}</b> — {d.meaning}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="text-sm font-medium text-fire mb-1">✗ Unlucky</div>
                <ul className="text-sm space-y-1">
                  {result.unlucky_directions.map((d) => (
                    <li key={d.category_key}>
                      <span className="chip element-fire mr-2 w-10 justify-center">{d.direction}</span>
                      <b>{d.cn} {d.en}</b> — {d.meaning}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          {result.room_verdicts.length > 0 && (
            <section className="rounded-2xl border border-ink/10 bg-white p-5">
              <div className="text-xs uppercase tracking-wider text-muted mb-3">Room Verdicts</div>
              <div className="space-y-2">
                {result.room_verdicts.map((rv) => (
                  <div key={rv.room} className={`rounded-xl border p-3 ${
                    rv.quality === "lucky" ? "border-wood/40 bg-wood-soft" :
                    rv.quality === "unlucky" ? "border-fire/40 bg-fire-soft" :
                    "border-ink/10"
                  }`}>
                    <div className="flex items-center gap-2 flex-wrap">
                      <b>{rv.room.replace(/_/g, " ")}</b>
                      <span className="text-muted text-xs">@ {rv.current_direction} {rv.direction_name}</span>
                      {rv.quality === "lucky" && rv.category_cn &&
                        <span className="chip element-wood">{rv.category_cn} {rv.category_en}</span>}
                      {rv.quality === "unlucky" && rv.category_cn &&
                        <span className="chip element-fire">{rv.category_cn} {rv.category_en}</span>}
                    </div>
                    {rv.meaning && <div className="text-xs text-muted mt-1">{rv.meaning}</div>}
                    <div className="text-sm mt-1">{rv.recommendation}</div>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="rounded-2xl border border-ink/10 bg-white p-5">
            <div className="text-xs uppercase tracking-wider text-muted mb-2">Recommendations</div>
            <ul className="list-disc pl-5 text-sm space-y-1">
              {result.recommendations.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}
