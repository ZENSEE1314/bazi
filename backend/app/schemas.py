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
