"""Pydantic schemas for request/response bodies."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str | None
    is_premium: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    birth_datetime: datetime
    relationship_label: str | None = Field(default=None, max_length=60)
    birth_location: str | None = Field(default=None, max_length=160)
    gender: str | None = Field(default=None, max_length=10)
    is_main: bool = False
    notes: str | None = Field(default=None, max_length=500)


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
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
    birth_datetime: datetime
    relationship_label: str | None
    birth_location: str | None
    gender: str | None
    is_main: bool
    notes: str | None
    created_at: datetime


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


class DailyCalendarDay(BaseModel):
    date: str
    score: int
    label: str                 # "excellent" | "good" | "neutral" | "caution" | "difficult"
    day_pillar_cn: str
    day_pillar_element: str


class PairAnalysisItem(BaseModel):
    a: int
    b: int
    category_cn: str
    category_en: str
    theme: str
    auspicious: bool


class DeepNumerologyReading(BaseModel):
    number: str
    scores: NumerologyReading
    life_path: int
    life_path_theme: str
    pairs: list[PairAnalysisItem]
    auspicious_pair_count: int
    inauspicious_pair_count: int
