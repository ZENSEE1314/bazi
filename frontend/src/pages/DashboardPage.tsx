import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, BaZi, Daily, Profile } from "../api";
import { ElementBar, PillarCard, ScoreRing } from "../components/PillarCard";

export function DashboardPage() {
  const [profile, setProfile] = useState<Profile | null | undefined>(undefined);
  const [bazi, setBazi] = useState<BaZi | null>(null);
  const [daily, setDaily] = useState<Daily | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listProfiles()
      .then((profiles) => {
        const main = profiles.find((p) => p.is_main) ?? profiles[0] ?? null;
        setProfile(main);
        if (main) {
          Promise.all([api.bazi(main.id), api.daily(main.id)])
            .then(([b, d]) => {
              setBazi(b);
              setDaily(d);
            })
            .catch((e) => setError(String(e)));
        }
      })
      .catch((e) => {
        setError(String(e));
        setProfile(null);
      });
  }, []);

  if (profile === undefined) {
    return <div className="text-muted">Loading…</div>;
  }

  if (profile === null) {
    return (
      <div className="rounded-2xl border border-dashed border-ink/20 p-8 text-center">
        <div className="font-display text-3xl">欢迎</div>
        <p className="mt-2 text-muted">
          Add your first profile to generate a chart and a daily reading.
        </p>
        <Link to="/profiles" className="btn-primary mt-4">Add a profile</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="text-xs text-muted uppercase tracking-wider">Main Profile</div>
            <h1 className="font-display text-3xl mt-1">{profile.name}</h1>
            <div className="text-sm text-muted mt-1">
              {new Date(profile.birth_datetime).toLocaleString()} • {profile.birth_location || "—"}
            </div>
          </div>
          <Link to={`/profiles/${profile.id}`} className="btn-ghost text-sm">Open full chart →</Link>
        </div>

        {bazi && (
          <>
            <div className="mt-5 grid grid-cols-2 md:grid-cols-4 gap-3">
              <PillarCard label="Year" pillar={bazi.year} />
              <PillarCard label="Month" pillar={bazi.month} />
              <PillarCard label="Day" pillar={bazi.day} />
              <PillarCard label="Hour" pillar={bazi.hour} />
            </div>
            <div className="mt-4 text-sm">
              Day Master: <b>{bazi.day_master}</b> ({bazi.day_master_element}) • Zodiac: <b>{bazi.zodiac}</b> • Dominant: <b>{bazi.dominant_element}</b> • Weakest: <b>{bazi.weakest_element}</b>
            </div>
            <div className="mt-3">
              <ElementBar elements={bazi.elements} />
            </div>
          </>
        )}
      </section>

      {daily && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <div className="text-xs text-muted uppercase tracking-wider">Today's Luck · {daily.date}</div>
              <div className="font-display text-2xl mt-1">
                {daily.day_pillar.stem}{daily.day_pillar.branch} day
              </div>
              <div className="text-sm text-muted">{daily.day_pillar.pinyin}</div>
            </div>
            <ScoreRing score={daily.score} label="Luck" />
          </div>
          <p className="mt-3 text-sm">{daily.summary}</p>

          {daily.supportive_elements.length > 0 && (
            <div className="mt-3">
              <div className="text-xs uppercase tracking-wider text-muted mb-1">Supportive</div>
              <ul className="list-disc pl-5 text-sm space-y-0.5">
                {daily.supportive_elements.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
          {daily.clashing_elements.length > 0 && (
            <div className="mt-3">
              <div className="text-xs uppercase tracking-wider text-muted mb-1">Friction</div>
              <ul className="list-disc pl-5 text-sm space-y-0.5">
                {daily.clashing_elements.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </section>
      )}

      {error && <div className="text-fire text-sm">{error}</div>}
    </div>
  );
}
