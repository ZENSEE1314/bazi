"""Gregorian -> Julian Day Number conversion and solar-term approximations.

Known limitation: solar term dates are approximated by fixed Gregorian dates.
Actual solar terms drift by up to one day across years. A future version should
use an ephemeris (e.g., skyfield) or a precomputed table.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# Reference: 1900-01-31 was 甲辰 day (sexagenary index 40).
# JDN(1900-01-31) = 2_415_051. Offset chosen so:
#     sexagenary_index = (JDN - DAY_PILLAR_OFFSET) % 60 == 40 for that date.
DAY_PILLAR_OFFSET = 11


def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """Julian Day Number for a proleptic Gregorian date.

    Reference: Explanatory Supplement to the Astronomical Almanac, 3rd ed.
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return (
        day
        + (153 * m + 2) // 5
        + 365 * y
        + y // 4
        - y // 100
        + y // 400
        - 32045
    )


@dataclass(frozen=True)
class SolarMonth:
    """A solar year/month pair used for month pillar calculation.

    solar_year: the Ba Zi year (may differ from Gregorian year in Jan/early Feb).
    branch_index: 0..11 where 2 == 寅 (first solar month, starts at 立春).
    """

    solar_year: int
    branch_index: int


# (month, day, branch_index) — each tuple marks the start of a branch-month in
# the current Gregorian year. 寅 starts at 立春 (~Feb 4).
_TERMS_WITHIN_YEAR: tuple[tuple[int, int, int], ...] = (
    (2, 4, 2),    # 寅 Yin (Lichun)
    (3, 6, 3),    # 卯 Mao (Jingzhe)
    (4, 5, 4),    # 辰 Chen (Qingming)
    (5, 6, 5),    # 巳 Si (Lixia)
    (6, 6, 6),    # 午 Wu (Mangzhong)
    (7, 7, 7),    # 未 Wei (Xiaoshu)
    (8, 8, 8),    # 申 Shen (Liqiu)
    (9, 8, 9),    # 酉 You (Bailu)
    (10, 8, 10),  # 戌 Xu (Hanlu)
    (11, 7, 11),  # 亥 Hai (Lidong)
    (12, 7, 0),   # 子 Zi (Daxue)
)

XIAOHAN_JAN_DAY = 6  # 小寒: start of 丑 month (previous solar year)
LICHUN_FEB_DAY = 4   # 立春: start of 寅 month and new solar year


def solar_month_for(dt: datetime) -> SolarMonth:
    """Resolve the Ba Zi solar year and branch for a given datetime.

    Uses approximate solar-term dates. For exact boundaries near a term, a
    more precise ephemeris is required.
    """
    y, m, d = dt.year, dt.month, dt.day

    if m == 1:
        if d < XIAOHAN_JAN_DAY:
            return SolarMonth(solar_year=y - 1, branch_index=0)  # 子
        return SolarMonth(solar_year=y - 1, branch_index=1)  # 丑

    if m == 2 and d < LICHUN_FEB_DAY:
        return SolarMonth(solar_year=y - 1, branch_index=1)  # 丑

    current_branch = 2  # 寅 (default for Feb 4..Mar 5)
    for tm, td, branch in _TERMS_WITHIN_YEAR:
        if (m, d) >= (tm, td):
            current_branch = branch
    return SolarMonth(solar_year=y, branch_index=current_branch)
