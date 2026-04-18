from datetime import datetime

from backend.core.bazi.calculator import four_pillars
from backend.core.bazi.elements import element_balance


def test_balance_for_known_chart():
    """2000-01-01 12:00 -> 己卯 丙子 戊午 戊午.

    Expected totals (with hidden stems):
      Stems:    己(earth), 丙(fire), 戊(earth), 戊(earth) -> earth=3, fire=1
      Hidden:   卯=乙(1.0 wood); 子=癸(1.0 water);
                午=丁(0.7)+己(0.3); 午=丁(0.7)+己(0.3)
      -> wood=1.0, fire=2.4, earth=3.6, metal=0.0, water=1.0
    """
    fp = four_pillars(datetime(2000, 1, 1, 12, 0))
    bal = element_balance(fp)
    assert round(bal.wood, 2) == 1.0
    assert round(bal.fire, 2) == 2.4
    assert round(bal.earth, 2) == 3.6
    assert round(bal.metal, 2) == 0.0
    assert round(bal.water, 2) == 1.0
    assert bal.dominant() == "earth"
    assert bal.weakest() == "metal"


def test_include_hidden_false_uses_main_branch_element():
    fp = four_pillars(datetime(2000, 1, 1, 12, 0))
    # 己卯 丙子 戊午 戊午
    # Stems:    己(earth), 丙(fire), 戊(earth), 戊(earth)
    # Branches: 卯(wood),  子(water), 午(fire), 午(fire)
    bal = element_balance(fp, include_hidden=False)
    assert bal.wood == 1.0
    assert bal.fire == 3.0   # 1 stem + 2 branches
    assert bal.earth == 3.0  # 3 stems
    assert bal.metal == 0.0
    assert bal.water == 1.0  # 子 branch


def test_balance_total_equals_expected_weight():
    fp = four_pillars(datetime(2024, 6, 15, 10, 30))
    bal = element_balance(fp, include_hidden=True)
    # 4 stems * 1.0 + 4 branches * 1.0 hidden-total = 8.0
    assert round(bal.total, 2) == 8.0


def test_balance_total_is_8_without_hidden_too():
    fp = four_pillars(datetime(1990, 5, 20, 14, 0))
    bal = element_balance(fp, include_hidden=False)
    assert round(bal.total, 2) == 8.0


def test_dominant_and_weakest_are_valid_elements():
    fp = four_pillars(datetime(1990, 5, 20, 14, 0))
    bal = element_balance(fp)
    valid = {"wood", "fire", "earth", "metal", "water"}
    assert bal.dominant() in valid
    assert bal.weakest() in valid


def test_as_dict_contains_all_five_elements():
    fp = four_pillars(datetime(1990, 5, 20, 14, 0))
    bal = element_balance(fp)
    assert set(bal.as_dict.keys()) == {"wood", "fire", "earth", "metal", "water"}
