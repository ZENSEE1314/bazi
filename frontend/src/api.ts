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
  is_active: boolean;
  is_admin: boolean;
  referral_code: string | null;
  referred_by_id: number | null;
  created_at: string;
  stripe_customer_id?: string | null;
  stripe_subscription_id?: string | null;
};

export type Business = {
  id: number;
  name: string;
  chinese_name: string | null;
  open_datetime: string;
  location: string | null;
  facing_direction: string | null;
  industry: string | null;
  notes: string | null;
  is_main: boolean;
  created_at: string;
};

export type BusinessOwnerMatch = {
  profile_id: number;
  profile_name: string;
  score: number;
  verdict: string;
  dm_relation: { a_element: string; b_element: string; kind: string; note: string };
  harmony: string[];
  tension: string[];
  harmony_count: number;
  tension_count: number;
  element_blend: Record<string, number>;

  owner_useful_god: string;
  owner_avoid_god: string;
  business_supplies_useful_god_pct: number;
  business_amplifies_avoid_god_pct: number;
  business_feeds_owner: boolean;
  business_drains_owner: boolean;
  area_scores: { romance: number; communication: number; finance: number; family: number; long_term: number };
  shared_weakness: string[];
  complementary_strengths: string[];
  ai_reading: string;
};

export type BusinessReading = {
  business: Business;
  chart: DeepBaZi;
  name_reading: ChineseNameReading | null;
  feng_shui: FengShuiReading | null;
  owner_matches: BusinessOwnerMatch[];
  best_match_profile_id: number | null;
  summary: string;
};

export type HistoryItem = {
  id: number;
  kind: "numerology" | "name";
  label: string;
  subtype: string | null;
  created_at: string;
};

export type HistoryDetail<T = any> = {
  id: number;
  kind: string;
  label: string;
  subtype: string | null;
  created_at: string;
  payload: T;
};

export type BillingConfig = {
  enabled: boolean;
  publishable_key: string | null;
  price_cents: number;
  price_usd: number;
  price_id: string | null;
  interval: "month" | "year";
};

export type ReferralSummary = {
  code: string;
  share_url: string;
  tier_percents: number[];
  monthly_fee_usd: number;
  direct_referrals: Array<{
    id: number;
    email: string;
    display_name: string | null;
    is_premium: boolean;
    created_at: string;
  }>;
  downline_tier_counts: { tier_1: number; tier_2: number; tier_3: number };
  pending_cents: number;
  paid_cents: number;
  pending_count: number;
  paid_count: number;
};

export type AdminUser = User & {
  total_pending_cents: number;
  total_paid_cents: number;
};

export type Commission = {
  id: number;
  earner_user_id: number;
  payer_user_id: number;
  tier: number;
  amount_cents: number;
  period_month: string;
  status: "pending" | "paid";
  paid_at: string | null;
  created_at: string;
};

export type Profile = {
  id: number;
  name: string;
  chinese_name: string | null;
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
  prevention: string[];
  enhancement: string[];
  color_palette_favor: string[];
  color_palette_avoid: string[];
  foods_favor: string[];
  foods_avoid: string[];
  gemstones: string[];
  lucky_numbers: number[];
  best_direction: string;
  best_careers: string[];
};

export type PairInteractionOut = {
  a_label: string;
  b_label: string;
  a_branch: string;
  b_branch: string;
  kind: "clash" | "six_combination" | "three_harmony_partial";
  transforms_to: string | null;
  note: string;
};

export type SpouseStarCheckSide = {
  applicable: boolean;
  role?: string | null;
  expected_element?: string | null;
  partner_dm_element?: string | null;
  partner_plays_spouse_star?: boolean | null;
  note: string;
};

export type DeepCompatibility = {
  profile_a: string;
  profile_b: string;
  total_score: number;
  verdict: string;

  day_master_relation: {
    a_element: string;
    b_element: string;
    kind: string;
    note: string;
  };
  spouse_star_check: {
    a_checks_b: SpouseStarCheckSide;
    b_checks_a: SpouseStarCheckSide;
  };
  useful_god_exchange: {
    a_useful_god: string;
    b_useful_god: string;
    a_useful_percent_in_b: number;
    b_useful_percent_in_a: number;
    a_gets_what_a_needs: boolean;
    b_gets_what_b_needs: boolean;
    note: string;
  };
  branch_interactions: PairInteractionOut[];
  area_scores: {
    romance: number;
    communication: number;
    finance: number;
    family: number;
    long_term: number;
  };
  element_blend: Record<string, number>;
  shared_weakness: string[];
  complementary_strengths: string[];
  harmony: string[];
  tension: string[];
};

export type NumerologyPair = {
  a: number;
  b: number;
  category_cn: string;
  category_en: string;
  theme: string;
  auspicious: boolean;
  explanation: string;
};

export type NumberSuggestion = {
  original: string;
  issues: string[];
  suggestions: string[];
};

export type DeepNumerology = {
  number: string;
  scores: Numerology;
  life_path: number;
  life_path_theme: string;
  pairs: NumerologyPair[];
  auspicious_pair_count: number;
  inauspicious_pair_count: number;
  profile_name: string | null;
  profile_day_master: string | null;
  profile_day_master_element: string | null;
  profile_useful_god: string | null;
  personalized_note: string | null;
  preferred_digits: number[];
  digits_to_avoid: number[];
  suggestion: NumberSuggestion | null;
};

export type NameGrid = {
  number: number;
  en: string;
  quality: "auspicious" | "inauspicious" | "mixed";
  theme: string;
};

export type ThreeTalents = {
  heaven_element: string;
  person_element: string;
  earth_element: string;
  heaven_person: string;
  person_earth: string;
  heaven_earth: string;
  level: "great" | "good" | "mixed" | "neutral" | "bad";
  label_en: string;
  label_cn: string;
  note: string;
};

export type LifeStage = {
  grid: string;
  age_label_en: string;
  age_label_zh: string;
  role: string;
  number: number;
  quality: "auspicious" | "inauspicious" | "mixed";
  theme: string;
  note: string;
};

export type YinYangBalance = {
  odd_count: number;
  even_count: number;
  total: number;
  verdict: string;
};

export type ChineseNameReading = {
  name: string;
  surname: string;
  given: string;
  character_strokes: { char: string; strokes: number; meaning?: string | null }[];
  grids: {
    heaven: NameGrid;
    person: NameGrid;
    earth: NameGrid;
    total: NameGrid;
    outer: NameGrid;
  };
  element_profile: Record<string, number>;
  dominant_element: string;
  auspicious_grids: number;
  inauspicious_grids: number;
  mixed_grids: number;
  summary: string;
  three_talents: ThreeTalents;
  life_stages: LifeStage[];
  yin_yang: YinYangBalance;
  aspect_scores: { career: number; wealth: number; health: number; marriage: number; social: number };
  aspect_notes: string[];
  total_strokes: number;
  surname_strokes: number;
  given_strokes: number;
};

export type RoomVerdict = {
  room: string;
  current_direction: string;
  direction_name: string;
  category_cn: string | null;
  category_en: string | null;
  quality: "lucky" | "unlucky" | "unknown";
  meaning: string;
  recommendation: string;
};

export type FengShuiReading = {
  life_kua_number: number;
  life_kua_group: string;
  house_facing: string;
  house_sitting: string;
  house_group: string;
  person_house_match: boolean;
  match_note: string;
  lucky_directions: Array<{ direction: string; [key: string]: any }>;
  unlucky_directions: Array<{ direction: string; [key: string]: any }>;
  room_verdicts: RoomVerdict[];
  overall_score: number;
  summary: string;
  recommendations: string[];
};

export type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export type ChatSession = {
  id: number;
  title: string;
  profile_id: number | null;
  created_at: string;
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
  register: (email: string, password: string, display_name?: string, referral_code?: string) =>
    request<{ access_token: string; user: User }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name, referral_code }),
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
  deep: (id: number, lang?: string) =>
    request<DeepBaZi>(`/api/profiles/${id}/deep${lang ? `?lang=${lang}` : ""}`),
  daily: (id: number, date?: string) =>
    request<Daily>(`/api/profiles/${id}/daily${date ? `?date=${date}` : ""}`),
  calendar: (id: number, year: number, month: number) =>
    request<DailyCalendarDay[]>(`/api/profiles/${id}/calendar?year=${year}&month=${month}`),
  numerology: (number: string) =>
    request<Numerology>("/api/numerology", {
      method: "POST",
      body: JSON.stringify({ number }),
    }),
  numerologyDeep: (number: string, profile_id?: number, language?: string) =>
    request<DeepNumerology>("/api/numerology/deep", {
      method: "POST",
      body: JSON.stringify({ number, profile_id, language }),
    }),
  chineseName: (name: string, surname_length?: number) =>
    request<ChineseNameReading>("/api/name/chinese", {
      method: "POST",
      body: JSON.stringify({ name, surname_length }),
    }),
  fengShui: (profile_id: number, house_facing: string, rooms: Record<string, string>, address?: string, latitude?: number, longitude?: number) =>
    request<FengShuiReading>("/api/fengshui/home", {
      method: "POST",
      body: JSON.stringify({ profile_id, house_facing, rooms, address, latitude, longitude }),
    }),
  chatSessions: () => request<ChatSession[]>("/api/chat/sessions"),
  chatMessages: (sessionId: number) => request<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`),
  chatDeleteSession: (sessionId: number) =>
    request<void>(`/api/chat/sessions/${sessionId}`, { method: "DELETE" }),
  chatSend: (question: string, session_id?: number, profile_id?: number, language?: string) =>
    request<{ session: ChatSession; user_message: ChatMessage; assistant_message: ChatMessage }>(
      "/api/chat/message",
      { method: "POST", body: JSON.stringify({ question, session_id, profile_id, language }) },
    ),
  compatibility: (a: number, b: number) =>
    request<Compatibility>("/api/compatibility", {
      method: "POST",
      body: JSON.stringify({ profile_a_id: a, profile_b_id: b }),
    }),
  compatibilityDeep: (a: number, b: number) =>
    request<DeepCompatibility>("/api/compatibility/deep", {
      method: "POST",
      body: JSON.stringify({ profile_a_id: a, profile_b_id: b }),
    }),

  // Referrals
  myReferrals: () => request<ReferralSummary>("/api/referrals/me"),

  // Admin
  adminListUsers: (q?: string) =>
    request<AdminUser[]>(`/api/admin/users${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  adminBan: (id: number) => request<User>(`/api/admin/users/${id}/ban`, { method: "POST" }),
  adminUnban: (id: number) => request<User>(`/api/admin/users/${id}/unban`, { method: "POST" }),
  adminSetPremium: (id: number, period_month?: string, note?: string) =>
    request<User>(`/api/admin/users/${id}/set_premium`, {
      method: "POST",
      body: JSON.stringify({ period_month, note }),
    }),
  adminUnsetPremium: (id: number) =>
    request<User>(`/api/admin/users/${id}/unset_premium`, { method: "POST" }),
  adminMakeAdmin: (id: number) =>
    request<User>(`/api/admin/users/${id}/admin`, { method: "POST" }),
  adminUnmakeAdmin: (id: number) =>
    request<User>(`/api/admin/users/${id}/unadmin`, { method: "POST" }),
  adminListCommissions: (params?: {
    status?: "pending" | "paid";
    period_month?: string;
    earner_id?: number;
  }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.period_month) qs.set("period_month", params.period_month);
    if (params?.earner_id != null) qs.set("earner_id", String(params.earner_id));
    const q = qs.toString();
    return request<Commission[]>(`/api/admin/commissions${q ? `?${q}` : ""}`);
  },
  adminMarkCommissionPaid: (id: number) =>
    request<Commission>(`/api/admin/commissions/${id}/mark_paid`, { method: "POST" }),
  adminPayAllPending: (period_month?: string) =>
    request<{ count: number; amount_cents: number }>(
      `/api/admin/commissions/pay_all${period_month ? `?period_month=${period_month}` : ""}`,
      { method: "POST" },
    ),

  // Businesses
  listBusinesses: () => request<Business[]>("/api/businesses"),
  createBusiness: (b: Partial<Business>) =>
    request<Business>("/api/businesses", { method: "POST", body: JSON.stringify(b) }),
  getBusiness: (id: number) => request<Business>(`/api/businesses/${id}`),
  updateBusiness: (id: number, b: Partial<Business>) =>
    request<Business>(`/api/businesses/${id}`, { method: "PATCH", body: JSON.stringify(b) }),
  deleteBusiness: (id: number) =>
    request<void>(`/api/businesses/${id}`, { method: "DELETE" }),
  businessReading: (id: number, lang?: string) =>
    request<BusinessReading>(`/api/businesses/${id}/reading${lang ? `?lang=${lang}` : ""}`),

  // History
  listHistory: (kind: "numerology" | "name", q?: string) => {
    const qs = new URLSearchParams({ kind });
    if (q) qs.set("q", q);
    return request<HistoryItem[]>(`/api/history?${qs.toString()}`);
  },
  getHistory: <T = any>(id: number) =>
    request<HistoryDetail<T>>(`/api/history/${id}`),
  deleteHistory: (id: number) =>
    request<void>(`/api/history/${id}`, { method: "DELETE" }),

  // Billing
  billingConfig: () => request<BillingConfig>("/api/billing/config"),
  billingCheckout: () =>
    request<{ url: string; id: string }>("/api/billing/checkout", { method: "POST" }),
  billingPortal: () =>
    request<{ url: string }>("/api/billing/portal", { method: "POST" }),
};
