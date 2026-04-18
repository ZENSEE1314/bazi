const TOKEN_KEY = "bazi.token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(t: string) {
  localStorage.setItem(TOKEN_KEY, t);
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export type User = {
  id: number;
  email: string;
  display_name: string | null;
  is_premium: boolean;
  created_at: string;
};

export type Profile = {
  id: number;
  name: string;
  birth_datetime: string;
  relationship_label: string | null;
  birth_location: string | null;
  gender: string | null;
  is_main: boolean;
  notes: string | null;
  created_at: string;
};

export type Pillar = {
  stem: string;
  branch: string;
  stem_element: string;
  branch_element: string;
  pinyin: string;
};

export type BaZi = {
  year: Pillar;
  month: Pillar;
  day: Pillar;
  hour: Pillar;
  day_master: string;
  day_master_element: string;
  zodiac: string;
  elements: Record<string, number>;
  dominant_element: string;
  weakest_element: string;
};

export type Daily = {
  date: string;
  day_pillar: Pillar;
  score: number;
  summary: string;
  supportive_elements: string[];
  clashing_elements: string[];
};

export type Numerology = {
  wealth: number;
  safety: number;
  health: number;
  overall: number;
  dominant_element: string;
  element_counts: Record<string, number>;
};

export type Compatibility = {
  score: number;
  summary: string;
  harmony: string[];
  tension: string[];
  shared_dominant: string | null;
  element_blend: Record<string, number>;
};

export type HiddenStem = {
  stem: string;
  element: string;
  weight: number;
  ten_god_cn: string;
  ten_god_en: string;
};

export type DeepPillar = {
  label: string;
  stem: string;
  branch: string;
  stem_element: string;
  branch_element: string;
  pinyin: string;
  sexagenary_index: number;
  nayin_cn: string;
  nayin_en: string;
  stem_ten_god_cn: string | null;
  stem_ten_god_en: string | null;
  hidden_stems: HiddenStem[];
};

export type DayMasterAnalysis = {
  element: string;
  stem: string;
  strength_score: number;
  strength_level: string;
  seasonal_influence: string;
  supportive_elements: string[];
  draining_elements: string[];
  useful_god: string;
  avoid_god: string;
  explanation: string;
};

export type FiveFactor = {
  key: string;
  label: string;
  element: string;
  amount: number;
  percent: number;
};

export type StarInfo = {
  trigger_branch: string | null;
  present_in: string[];
};

export type LifeKuaInfo = {
  number: number;
  trigram_cn: string;
  trigram_pinyin: string;
  element: string;
  seated_direction: string;
  group: string;
};

export type DirectionInfo = {
  direction: string;
  direction_name: string;
  category_key: string;
  cn: string;
  en: string;
  meaning: string;
};

export type LuckPillarOut = {
  index: number;
  start_age: number;
  end_age: number;
  stem: string;
  branch: string;
  stem_element: string;
  branch_element: string;
  pinyin: string;
  nayin_en: string;
  stem_ten_god_cn: string;
  stem_ten_god_en: string;
};

export type AnnualLuckOut = {
  year: number;
  stem: string;
  branch: string;
  stem_element: string;
  branch_element: string;
  stem_ten_god_cn: string;
  stem_ten_god_en: string;
  note: string;
};

export type RelationItem = {
  kind: string | null;
  pillars: string[] | null;
  branches: string[];
  transforms_to: string | null;
  note: string;
};

export type DeepBaZi = {
  pillars: DeepPillar[];
  chart_string: string;
  zodiac: string;
  day_master: DayMasterAnalysis;
  elements: Record<string, number>;
  dominant_element: string;
  weakest_element: string;
  five_factors: FiveFactor[];
  stars: Record<string, StarInfo>;
  life_kua: LifeKuaInfo | null;
  lucky_directions: DirectionInfo[];
  unlucky_directions: DirectionInfo[];
  relations: Record<string, RelationItem[]>;
  luck_pillars: LuckPillarOut[];
  annual_luck: AnnualLuckOut;
  life_areas: Record<string, { strength: number; gods: string[] }>;
  personality_notes: string[];
  career_paths: string[];
  wealth_strategy: string[];
  love_outlook: string[];
  health_watch: string[];
};

export type DailyCalendarDay = {
  date: string;
  score: number;
  label: "excellent" | "good" | "neutral" | "caution" | "difficult";
  day_pillar_cn: string;
  day_pillar_element: string;
};

async function request<T>(
  path: string,
  init: RequestInit = {},
  { json = true }: { json?: boolean } = {},
): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (json && !headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const resp = await fetch(path, { ...init, headers });
  if (!resp.ok) {
    let detail = `Request failed (${resp.status})`;
    try {
      const body = await resp.json();
      if (body?.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json();
}

export const api = {
  register: (email: string, password: string, display_name?: string) =>
    request<{ access_token: string; user: User }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }),

  login: async (email: string, password: string) => {
    const form = new URLSearchParams({ username: email, password });
    const resp = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      throw new Error(body?.detail || "Login failed");
    }
    return (await resp.json()) as { access_token: string; user: User };
  },

  me: () => request<User>("/api/auth/me"),

  listProfiles: () => request<Profile[]>("/api/profiles"),
  createProfile: (p: Partial<Profile>) =>
    request<Profile>("/api/profiles", { method: "POST", body: JSON.stringify(p) }),
  getProfile: (id: number) => request<Profile>(`/api/profiles/${id}`),
  updateProfile: (id: number, p: Partial<Profile>) =>
    request<Profile>(`/api/profiles/${id}`, { method: "PATCH", body: JSON.stringify(p) }),
  deleteProfile: (id: number) =>
    request<void>(`/api/profiles/${id}`, { method: "DELETE" }),

  bazi: (id: number) => request<BaZi>(`/api/profiles/${id}/bazi`),
  deep: (id: number) => request<DeepBaZi>(`/api/profiles/${id}/deep`),
  daily: (id: number, date?: string) =>
    request<Daily>(`/api/profiles/${id}/daily${date ? `?date=${date}` : ""}`),
  calendar: (id: number, year: number, month: number) =>
    request<DailyCalendarDay[]>(`/api/profiles/${id}/calendar?year=${year}&month=${month}`),
  numerology: (number: string) =>
    request<Numerology>("/api/numerology", {
      method: "POST",
      body: JSON.stringify({ number }),
    }),
  compatibility: (a: number, b: number) =>
    request<Compatibility>("/api/compatibility", {
      method: "POST",
      body: JSON.stringify({ profile_a_id: a, profile_b_id: b }),
    }),
};
