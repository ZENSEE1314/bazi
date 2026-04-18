import pytest

from backend.core.numerology.scorer import score_number


def test_score_is_deterministic():
    assert score_number("12345678") == score_number("12345678")


def test_scores_in_0_100_range():
    s = score_number("98765432")
    assert 0 <= s.wealth <= 100
    assert 0 <= s.safety <= 100
    assert 0 <= s.health <= 100


def test_auspicious_number_beats_inauspicious_on_wealth():
    lucky = score_number("88888888")
    unlucky = score_number("44444444")
    assert lucky.wealth > unlucky.wealth


def test_strips_non_digits():
    a = score_number("+1 (555) 888-8888")
    b = score_number("15558888888")
    assert a.wealth == b.wealth
    assert a.safety == b.safety


def test_raises_on_empty_input():
    with pytest.raises(ValueError):
        score_number("abcd")


def test_last_digits_weight_more():
    """Moving wealth-digits to the tail should raise wealth vs. head-heavy."""
    tail_heavy = score_number("11118888")
    head_heavy = score_number("88881111")
    assert tail_heavy.wealth > head_heavy.wealth


def test_balanced_number_has_higher_health_than_skewed():
    balanced = score_number("1234567890")  # covers every element
    skewed = score_number("0000000000")    # all water
    assert balanced.health > skewed.health


def test_overall_is_average_of_three_axes():
    s = score_number("12345678")
    assert s.overall == round((s.wealth + s.safety + s.health) / 3)


def test_dominant_element_is_one_of_five():
    s = score_number("98765432")
    assert s.dominant_element in {"wood", "fire", "earth", "metal", "water"}


def test_inauspicious_penalty_reduces_safety():
    no_fours = score_number("11111111")
    with_fours = score_number("14141414")
    assert no_fours.safety > with_fours.safety


def test_element_counts_sum_matches_weight_total():
    """Last 4 digits count 2x, first n-4 count 1x. For 8 digits: 4*1 + 4*2 = 12."""
    s = score_number("12345678")
    assert round(sum(s.element_counts.values()), 2) == 12.0
