from datetime import datetime

from backend.core.bazi.calendar import (
    DAY_PILLAR_OFFSET,
    gregorian_to_jdn,
    solar_month_for,
)


def test_gregorian_to_jdn_known_dates():
    assert gregorian_to_jdn(2000, 1, 1) == 2451545
    assert gregorian_to_jdn(1900, 1, 31) == 2415051
    assert gregorian_to_jdn(2024, 1, 1) == 2460311


def test_day_pillar_offset_matches_reference():
    # 1900-01-31 is the reference 甲辰 day (sexagenary index 40).
    jdn = gregorian_to_jdn(1900, 1, 31)
    assert (jdn - DAY_PILLAR_OFFSET) % 60 == 40


def test_solar_month_jan_before_xiaohan_is_prev_year_zi():
    sm = solar_month_for(datetime(2024, 1, 3, 12, 0))
    assert sm.solar_year == 2023
    assert sm.branch_index == 0  # 子


def test_solar_month_jan_after_xiaohan_is_prev_year_chou():
    sm = solar_month_for(datetime(2024, 1, 20, 12, 0))
    assert sm.solar_year == 2023
    assert sm.branch_index == 1  # 丑


def test_solar_month_feb_before_lichun_is_prev_year_chou():
    sm = solar_month_for(datetime(2024, 2, 2, 8, 0))
    assert sm.solar_year == 2023
    assert sm.branch_index == 1  # 丑


def test_solar_month_feb_after_lichun_is_current_year_yin():
    sm = solar_month_for(datetime(2024, 2, 10, 8, 0))
    assert sm.solar_year == 2024
    assert sm.branch_index == 2  # 寅


def test_solar_month_mid_year():
    sm = solar_month_for(datetime(2024, 6, 10, 0, 0))
    assert sm.solar_year == 2024
    assert sm.branch_index == 6  # 午


def test_solar_month_december_is_zi():
    sm = solar_month_for(datetime(2024, 12, 15, 0, 0))
    assert sm.solar_year == 2024
    assert sm.branch_index == 0  # 子
