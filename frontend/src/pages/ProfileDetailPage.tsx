import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, BaZi, Daily, Profile } from "../api";
import { ElementBar, PillarCard, ScoreRing } from "../components/PillarCard";

export function ProfileDetailPage() {
  const { id } = useParams<{ id: string }>();
  const profileId = Number(id);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [bazi, setBazi] = useState<BaZi | null>(null);
  const [daily, setDaily] = useState<Daily | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!profileId) return;
    Promise.all([api.getProfile(profileId), api.bazi(profileId), api.daily(profileId)])
      .then(([p, b, d]) => {
        setProfile(p);
        setBazi(b);
        setDaily(d);
      })
      .catch((e) => setError(String(e)));
  }, [profileId]);

  if (error) return <div className="text-fire">{error}</div>;
  if (!profile || !bazi) return <div className="text-muted">Loading…</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/profiles" className="text-sm text-muted hover:underline">← Vault</Link>
        <h1 className="font-display text-2xl">{profile.name}</h1>
        {profile.is_main && <span className="chip element-fire">MAIN</span>}
      </div>

      <section className="rounded-2xl border border-ink/10 bg-white p-5">
        <div className="text-sm text-muted">
          {new Date(profile.birth_datetime).toLocaleString()}
          {profile.birth_location ? ` • ${profile.birth_location}` : ""}
        </div>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          <PillarCard label="Year" pillar={bazi.year} />
          <PillarCard label="Month" pillar={bazi.month} />
          <PillarCard label="Day" pillar={bazi.day} />
          <PillarCard label="Hour" pillar={bazi.hour} />
        </div>
        <div className="mt-4 grid sm:grid-cols-2 gap-4">
          <div className="text-sm">
            <div><span className="text-muted">Day Master:</span> <b>{bazi.day_master}</b> ({bazi.day_master_element})</div>
            <div><span className="text-muted">Zodiac:</span> <b>{bazi.zodiac}</b></div>
            <div><span className="text-muted">Dominant:</span> <b>{bazi.dominant_element}</b></div>
            <div><span className="text-muted">Weakest:</span> <b>{bazi.weakest_element}</b></div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted mb-1">Five Elements</div>
            <ElementBar elements={bazi.elements} />
          </div>
        </div>
      </section>

      {daily && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <div className="text-xs text-muted uppercase tracking-wider">Today · {daily.date}</div>
              <div className="font-display text-xl mt-1">
                {daily.day_pillar.stem}{daily.day_pillar.branch} day
              </div>
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

      {profile.notes && (
        <section className="rounded-2xl border border-ink/10 bg-white p-5">
          <div className="text-xs uppercase tracking-wider text-muted mb-1">Notes</div>
          <p className="text-sm whitespace-pre-wrap">{profile.notes}</p>
        </section>
      )}
    </div>
  );
}
