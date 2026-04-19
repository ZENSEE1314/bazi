"""Pydantic schemas for request/response bodies."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)
    referral_code: str | None = Field(default=None, max_length=16)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str | None
    is_premium: bool
    is_active: bool
    is_admin: bool
    referral_code: str | None
    referred_by_id: int | None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    chinese_name: str | None = Field(default=None, max_length=60)
    birth_datetime: datetime
    relationship_label: str | None = Field(default=None, max_length=60)
    birth_location: str | None = Field(default=None, max_length=160)
    gender: str | None = Field(default=None, max_length=10)
    is_main: bool = False
    notes: str | None = Field(default=None, max_length=500)


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    chinese_name: str | None = Field(default=None, max_length=60)
    birth_datetime: datetime | None = None
    relationship_label: str | None = Field(default=None, max_length=60)
    birth_location: str | None = Field(default=None, max_length=160)
    gender: str | None = Field(default=None, max_length=10)
    is_main: bool | None = None
    notes: str | None = Field(default=None, max_length=500)


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    chinese_name: str | None
    birth_datetime: datetime
    relationship_label: str | None
    birth_location: str | None
    gender: str | None
    is_main: bool
    notes: str | None
    created_at: datetime


# --- Business profiles ---------------------------------------------------

class BusinessCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    chinese_name: str | None = Field(default=None, max_length=60)
    open_datetime: datetime
    location: str | None = Field(default=None, max_length=200)
    facing_direction: str | None = Field(default=None, max_length=3)
    industry: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=500)
    is_main: bool = False


class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=160)
    chinese_name: str | None = Field(default=None, max_length=60)
    open_datetime: datetime | None = None
    location: str | None = Field(default=None, max_length=200)
    facing_direction: str | None = Field(default=None, max_length=3)
    industry: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=500)
    is_main: bool | None = None


class BusinessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    chinese_name: str | None
    open_datetime: datetime
    location: str | None
    facing_direction: str | None
    industry: str | None
    notes: str | None
    is_main: bool
    created_at: datetime


class BusinessOwnerMatch(BaseModel):
    profile_id: int
    profile_name: str
    score: int
    verdict: str
    dm_relation: dict
    harmony: list[str]
    tension: list[str]
    harmony_count: int
    tension_count: int
    element_blend: dict[str, float]

    # Owner-specific axes
    owner_useful_god: str
    owner_avoid_god: str
    business_supplies_useful_god_pct: float   # % of business chart that is owner's Useful God
    business_amplifies_avoid_god_pct: float   # % of business chart that is owner's Avoid God
    business_feeds_owner: bool                # True if business dominant element produces owner's DM
    business_drains_owner: bool               # True if business dominant element controls owner's DM
    area_scores: dict[str, int]               # romance/communication/finance/family/long_term
    shared_weakness: list[str]
    complementary_strengths: list[str]
    ai_reading: str                            # multi-sentence plain-English verdict


class BusinessReading(BaseModel):
    business: BusinessOut
    chart: DeepBaZiReading
    name_reading: ChineseNameReadingOut | None = None
    feng_shui: FengShuiReadingOut | None = None
    owner_matches: list[BusinessOwnerMatch] = Field(default_factory=list)
    best_match_profile_id: int | None = None
    summary: str


class Pillar(BaseModel):
    stem: str
    branch: str
    stem_element: str
    branch_element: str
    pinyin: str


class BaZiReading(BaseModel):
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    day_master: str
    day_master_element: str
    zodiac: str
    elements: dict[str, float]
    dominant_element: str
    weakest_element: str


class DailyLuck(BaseModel):
    date: str
    day_pillar: Pillar
    score: int
    summary: str
    supportive_elements: list[str]
    clashing_elements: list[str]


class NumerologyRequest(BaseModel):
    number: str = Field(min_length=1, max_length=64)


class NumerologyReading(BaseModel):
    wealth: int
    safety: int
    health: int
    overall: int
    dominant_element: str
    element_counts: dict[str, float]


class CompatibilityRequest(BaseModel):
    profile_a_id: int
    profile_b_id: int


class CompatibilityReading(BaseModel):
    score: int
    summary: str
    harmony: list[str]
    tension: list[str]
    shared_dominant: str | None
    element_blend: dict[str, float]


# ----- Deep Reading (rich personal reading) ------------------------------

class HiddenStem(BaseModel):
    stem: str
    element: str
    weight: float
    ten_god_cn: str
    ten_god_en: str


class DeepPillar(BaseModel):
    label: str
    stem: str
    branch: str
    stem_element: str
    branch_element: str
    pinyin: str
    sexagenary_index: int
    nayin_cn: str
    nayin_en: str
    stem_ten_god_cn: str | None   # None for Day pillar (Day Master itself)
    stem_ten_god_en: str | None
    hidden_stems: list[HiddenStem]


class DayMasterAnalysis(BaseModel):
    element: str
    stem: str
    strength_score: float
    strength_level: str
    seasonal_influence: str
    supportive_elements: list[str]
    draining_elements: list[str]
    useful_god: str
    avoid_god: str
    explanation: str


class LuckPillarOut(BaseModel):
    index: int
    start_age: int
    end_age: int
    stem: str
    branch: str
    stem_element: str
    branch_element: str
    pinyin: str
    nayin_en: str
    stem_ten_god_cn: str
    stem_ten_god_en: str


class AnnualLuckOut(BaseModel):
    year: int
    stem: str
    branch: str
    stem_element: str
    branch_element: str
    stem_ten_god_cn: str
    stem_ten_god_en: str
    note: str


class RelationItem(BaseModel):
    kind: str | None = None
    pillars: list[str] | None = None
    branches: list[str]
    transforms_to: str | None = None
    note: str


class FiveFactor(BaseModel):
    key: str
    label: str
    element: str
    amount: float
    percent: float


class DirectionInfo(BaseModel):
    direction: str            # "S", "NE", etc.
    direction_name: str       # "South", "Northeast"
    category_key: str
    cn: str
    en: str
    meaning: str


class LifeKuaInfo(BaseModel):
    number: int
    trigram_cn: str
    trigram_pinyin: str
    element: str
    seated_direction: str
    group: str


class StarInfo(BaseModel):
    trigger_branch: str | None  # branch char that triggers this star
    present_in: list[str]       # pillar labels where it appears


class DeepBaZiReading(BaseModel):
    pillars: list[DeepPillar]
    chart_string: str
    zodiac: str
    day_master: DayMasterAnalysis
    elements: dict[str, float]
    dominant_element: str
    weakest_element: str
    five_factors: list[FiveFactor]
    stars: dict[str, StarInfo]
    life_kua: LifeKuaInfo | None
    lucky_directions: list[DirectionInfo]
    unlucky_directions: list[DirectionInfo]
    relations: dict[str, list[RelationItem]]
    luck_pillars: list[LuckPillarOut]
    annual_luck: AnnualLuckOut
    life_areas: dict[str, dict[str, float | list[str]]]
    personality_notes: list[str]
    career_paths: list[str]
    wealth_strategy: list[str]
    love_outlook: list[str]
    health_watch: list[str]
    prevention: list[str]
    enhancement: list[str]
    color_palette_favor: list[str]
    color_palette_avoid: list[str]
    foods_favor: list[str]
    foods_avoid: list[str]
    gemstones: list[str]
    lucky_numbers: list[int]
    best_direction: str
    best_careers: list[str]


class DailyCalendarDay(BaseModel):
    date: str
    score: int
    label: str                 # "excellent" | "good" | "neutral" | "caution" | "difficult"
    day_pillar_cn: str
    day_pillar_element: str


# ----- Deep Compatibility -----------------------------------------------

class PairInteractionOut(BaseModel):
    a_label: str
    b_label: str
    a_branch: str
    b_branch: str
    kind: str
    transforms_to: str | None
    note: str


class SpouseStarCheckSide(BaseModel):
    applicable: bool
    role: str | None = None
    expected_element: str | None = None
    partner_dm_element: str | None = None
    partner_plays_spouse_star: bool | None = None
    note: str


class DeepCompatibility(BaseModel):
    profile_a: str
    profile_b: str
    total_score: int
    verdict: str

    day_master_relation: dict
    spouse_star_check: dict[str, SpouseStarCheckSide]
    useful_god_exchange: dict

    branch_interactions: list[PairInteractionOut]
    area_scores: dict[str, int]
    element_blend: dict[str, float]

    shared_weakness: list[str]
    complementary_strengths: list[str]
    harmony: list[str]
    tension: list[str]


# ----- Chinese name reading ----------------------------------------------

class CharStroke(BaseModel):
    char: str
    strokes: int


class NameGrid(BaseModel):
    number: int
    en: str
    quality: str
    theme: str


class ChineseNameGridsOut(BaseModel):
    heaven: NameGrid
    person: NameGrid
    earth: NameGrid
    total: NameGrid
    outer: NameGrid


class ChineseNameRequest(BaseModel):
    name: str = Field(min_length=1, max_length=16)
    surname_length: int | None = None


class ChineseNameReadingOut(BaseModel):
    name: str
    surname: str
    given: str
    character_strokes: list[CharStroke]
    grids: ChineseNameGridsOut
    element_profile: dict[str, int]
    dominant_element: str
    auspicious_grids: int
    inauspicious_grids: int
    mixed_grids: int
    summary: str


# ----- Feng Shui ----------------------------------------------------------

class FengShuiRequest(BaseModel):
    profile_id: int
    house_facing: str = Field(min_length=1, max_length=3)
    address: str | None = Field(default=None, max_length=240)
    latitude: float | None = None
    longitude: float | None = None
    rooms: dict[str, str] = Field(default_factory=dict)


class RoomVerdictOut(BaseModel):
    room: str
    current_direction: str
    direction_name: str
    category_cn: str | None
    category_en: str | None
    quality: str
    meaning: str
    recommendation: str


class FengShuiReadingOut(BaseModel):
    life_kua_number: int
    life_kua_group: str
    house_facing: str
    house_sitting: str
    house_group: str
    person_house_match: bool
    match_note: str
    lucky_directions: list[dict]
    unlucky_directions: list[dict]
    room_verdicts: list[RoomVerdictOut]
    overall_score: int
    summary: str
    recommendations: list[str]


# ----- Chat ---------------------------------------------------------------

class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime


class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    profile_id: int | None
    created_at: datetime


class ChatMessageCreate(BaseModel):
    session_id: int | None = None
    profile_id: int | None = None
    question: str = Field(min_length=1, max_length=2000)
    language: str | None = "en"  # en, zh, ms


class ChatReply(BaseModel):
    session: ChatSessionOut
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut


# ----- Referrals / admin --------------------------------------------------

class ReferredUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str | None
    is_premium: bool
    created_at: datetime


class ReferralSummary(BaseModel):
    code: str
    share_url: str
    tier_percents: list[int]
    monthly_fee_usd: float
    direct_referrals: list[ReferredUserOut]
    downline_tier_counts: dict[str, int]  # {"tier_1": n, "tier_2": n, "tier_3": n}
    pending_cents: int
    paid_cents: int
    pending_count: int
    paid_count: int


class CommissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    earner_user_id: int
    payer_user_id: int
    tier: int
    amount_cents: int
    period_month: str
    status: str
    paid_at: datetime | None
    created_at: datetime


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str | None
    is_premium: bool
    is_active: bool
    is_admin: bool
    referral_code: str | None
    referred_by_id: int | None
    created_at: datetime
    total_pending_cents: int = 0
    total_paid_cents: int = 0


class AdminUserAction(BaseModel):
    note: str | None = Field(default=None, max_length=200)


class MarkPremiumRequest(BaseModel):
    period_month: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")
    note: str | None = Field(default=None, max_length=200)


# ----- History -----------------------------------------------------------

class HistoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    label: str
    subtype: str | None
    created_at: datetime


class PairAnalysisItem(BaseModel):
    a: int
    b: int
    category_cn: str
    category_en: str
    theme: str
    auspicious: bool
    explanation: str


class NumerologyRequestDeep(BaseModel):
    number: str = Field(min_length=1, max_length=64)
    profile_id: int | None = None
    language: str | None = "en"


class NumberSuggestion(BaseModel):
    original: str
    issues: list[str]
    suggestions: list[str]


class DeepNumerologyReading(BaseModel):
    number: str
    scores: NumerologyReading
    life_path: int
    life_path_theme: str
    pairs: list[PairAnalysisItem]
    auspicious_pair_count: int
    inauspicious_pair_count: int
    # Profile-linked fields (populated when profile_id provided)
    profile_name: str | None = None
    profile_day_master: str | None = None
    profile_day_master_element: str | None = None
    profile_useful_god: str | None = None
    personalized_note: str | None = None
    preferred_digits: list[int] = Field(default_factory=list)
    digits_to_avoid: list[int] = Field(default_factory=list)
    suggestion: NumberSuggestion | None = None
