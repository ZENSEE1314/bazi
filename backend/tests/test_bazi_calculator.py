from datetime import datetime

from backend.core.bazi.calculator import Pillar, four_pillars


def _code(p: Pillar) -> tuple[int, int]:
    return (p.stem_index, p.branch_index)


def test_jan_1_2000_noon():
    """Jan 1, 2000 at 12:00 is a well-known reference.

    Jan 1 falls before 小寒 (Jan 6), so the month is 子 of 1999 solar year.

    Expected (standard tables):
        Year:  己卯 (5, 3) -- still 1999 solar year (before 立春)
        Month: 丙子 (2, 0) -- 子 month before 小寒 2000
        Day:   戊午 (4, 6)
        Hour:  戊午 (4, 6) -- 午 hour (11:00-13:00)
    """
    fp = four_pillars(datetime(2000, 1, 1, 12, 0))
    assert _code(fp.year) == (5, 3), f"year was {fp.year}"
    assert _code(fp.month) == (2, 0), f"month was {fp.month}"
    assert _code(fp.day) == (4, 6), f"day was {fp.day}"
    assert _code(fp.hour) == (4, 6), f"hour was {fp.hour}"


def test_four_pillars_string_representation():
    fp = four_pillars(datetime(2000, 1, 1, 12, 0))
    assert str(fp) == "己卯 丙子 戊午 戊午"


def test_month_pillar_switches_at_xiaohan():
    """Crossing 小寒 (Jan 6) moves the month from 子 to 丑 (stem advances by 1)."""
    before = four_pillars(datetime(2000, 1, 5, 12, 0))
    after = four_pillars(datetime(2000, 1, 7, 12, 0))
    assert before.month.branch_index == 0  # 子
    assert after.month.branch_index == 1   # 丑
    assert (after.month.stem_index - before.month.stem_index) % 10 == 1


def test_month_pillar_at_lichun_crosses_year_and_month():
    """Crossing 立春 (Feb 4) advances the solar year and moves to 寅 month."""
    before = four_pillars(datetime(2000, 2, 3, 12, 0))
    after = four_pillars(datetime(2000, 2, 5, 12, 0))
    # Year pillar advances by one sexagenary step.
    assert (after.year.stem_index - before.year.stem_index) % 10 == 1
    assert (after.year.branch_index - before.year.branch_index) % 12 == 1
    # Month becomes 寅.
    assert after.month.branch_index == 2


def test_zodiac_is_derived_from_year_branch():
    fp = four_pillars(datetime(2000, 6, 15, 10, 0))
    assert fp.zodiac == "Dragon"


def test_day_master_is_day_stem():
    fp = four_pillars(datetime(2000, 1, 1, 12, 0))
    assert fp.day_master == "戊"
    assert fp.day_master_element == "earth"


def test_late_zi_hour_shifts_day_pillar():
    """23:30 is 晚子时: day pillar should match the following day."""
    fp_late = four_pillars(datetime(2000, 1, 1, 23, 30))
    fp_next = four_pillars(datetime(2000, 1, 2, 0, 30))
    assert _code(fp_late.day) == _code(fp_next.day)
    assert fp_late.hour.branch_index == 0  # 子
    assert fp_next.hour.branch_index == 0


def test_hour_branches_across_day():
    base = datetime(2024, 6, 15)
    hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 23]
    expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0]
    for h, exp in zip(hours, expected):
        fp = four_pillars(base.replace(hour=h, minute=30))
        assert fp.hour.branch_index == exp, f"hour {h} -> {fp.hour.branch_index}, expected {exp}"


def test_pillar_sexagenary_index():
    assert Pillar(0, 0).sexagenary_index == 0       # 甲子
    assert Pillar(9, 11).sexagenary_index == 59     # 癸亥
    assert Pillar(4, 6).sexagenary_index == 54      # 戊午


def test_pillar_invalid_combination_raises():
    import pytest

    # 甲 (stem 0) can never pair with 丑 (branch 1) in the 60 cycle.
    with pytest.raises(ValueError):
        Pillar(0, 1).sexagenary_index


def test_many_dates_produce_valid_pillars():
    """Sanity: every computed pillar must have a valid sexagenary index."""
    sample = [
        datetime(1950, 3, 15, 6, 0),
        datetime(1975, 7, 7, 7, 0),
        datetime(1984, 2, 5, 0, 30),
        datetime(1999, 12, 31, 23, 59),
        datetime(2024, 5, 1, 14, 0),
        datetime(2026, 4, 18, 9, 30),
    ]
    for dt in sample:
        fp = four_pillars(dt)
        for p in (fp.year, fp.month, fp.day, fp.hour):
            _ = p.sexagenary_index  # must not raise
            assert 0 <= p.stem_index < 10
            assert 0 <= p.branch_index < 12
