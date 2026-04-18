"""Compute the Four Pillars (Year, Month, Day, Hour) for a given datetime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .calendar import DAY_PILLAR_OFFSET, gregorian_to_jdn, solar_month_for
from .constants import (
    BRANCH_ELEMENT,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    STEM_ELEMENT,
    ZODIAC_ANIMALS,
)


@dataclass(frozen=True)
class Pillar:
    stem_index: int
    branch_index: int

    @property
    def stem(self) -> str:
        return HEAVENLY_STEMS[self.stem_index]

    @property
    def branch(self) -> str:
        return EARTHLY_BRANCHES[self.branch_index]

    @property
    def stem_element(self) -> str:
        return STEM_ELEMENT[self.stem_index]

    @property
    def branch_element(self) -> str:
        return BRANCH_ELEMENT[self.branch_index]

    @property
    def sexagenary_index(self) -> int:
        """0..59 index in the Jiazi (60) cycle."""
        for i in range(60):
            if i % 10 == self.stem_index and i % 12 == self.branch_index:
                return i
        raise ValueError("Invalid pillar: stem/branch combination has no sexagenary index")

    def __str__(self) -> str:
        return f"{self.stem}{self.branch}"


@dataclass(frozen=True)
class FourPillars:
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar

    @property
    def day_master(self) -> str:
        return self.day.stem

    @property
    def day_master_element(self) -> str:
        return self.day.stem_element

    @property
    def zodiac(self) -> str:
        return ZODIAC_ANIMALS[self.year.branch_index]

    def __str__(self) -> str:
        return f"{self.year} {self.month} {self.day} {self.hour}"


# Reference: year 4 CE has stem=0 (甲) and branch=0 (子).
_YEAR_EPOCH = 4


def _year_pillar(solar_year: int) -> Pillar:
    idx = solar_year - _YEAR_EPOCH
    return Pillar(stem_index=idx % 10, branch_index=idx % 12)


def _month_pillar(year_stem_index: int, month_branch_index: int) -> Pillar:
    """Month pillar via 五虎遁 (Five Tiger) rule.

    The 寅 (Yin) month stem for a given year stem follows:
        first = ((year_stem % 5) * 2 + 2) mod 10
    """
    first_month_stem = ((year_stem_index % 5) * 2 + 2) % 10
    months_from_yin = (month_branch_index - 2) % 12
    stem = (first_month_stem + months_from_yin) % 10
    return Pillar(stem_index=stem, branch_index=month_branch_index)


def _day_pillar(jdn: int) -> Pillar:
    sex = (jdn - DAY_PILLAR_OFFSET) % 60
    return Pillar(stem_index=sex % 10, branch_index=sex % 12)


def _hour_pillar(day_stem_index: int, hour_of_day: int) -> Pillar:
    """Hour pillar via 五鼠遁 (Five Rat) rule.

    Hour blocks start at 23:00 (子时):
        23-01 子, 01-03 丑, 03-05 寅, ... 21-23 亥.
    """
    branch_index = ((hour_of_day + 1) // 2) % 12
    first_hour_stem = ((day_stem_index % 5) * 2) % 10
    stem = (first_hour_stem + branch_index) % 10
    return Pillar(stem_index=stem, branch_index=branch_index)


def four_pillars(dt: datetime) -> FourPillars:
    """Compute the Four Pillars for a local datetime.

    The datetime is treated as local solar time at the birthplace. For precise
    astrological work, callers should adjust for longitude offset from the
    standard timezone meridian; this function does not perform that correction.

    The day boundary follows the 晚子时 convention: times at or after 23:00
    belong to the next day's pillar.
    """
    solar = solar_month_for(dt)
    year = _year_pillar(solar.solar_year)
    month = _month_pillar(year.stem_index, solar.branch_index)

    effective = dt + timedelta(hours=1) if dt.hour == 23 else dt
    jdn = gregorian_to_jdn(effective.year, effective.month, effective.day)
    day = _day_pillar(jdn)

    hour = _hour_pillar(day.stem_index, dt.hour)
    return FourPillars(year=year, month=month, day=day, hour=hour)
