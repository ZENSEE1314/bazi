"""Deep two-person compatibility (synastry).

Scoring axes:
  romance      - intimate/romantic chemistry (day-pillar + peach blossom + spouse star)
  communication- stem interactions + Ten-God texture
  finance      - wealth star alignment + month pillar
  family       - resource stars + year pillar compatibility
  long_term    - overall structural fit + useful-god exchange

Engine also surfaces:
  - How each person's Day Master relates to the other (produces / controls / drains / nourishes).
  - Branch combinations (六合 / 三合 / 六冲) between their four pillars.
  - Whether each person's Useful God appears in the partner's chart.
  - The spousal-star check (wealth for male, officer for female).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .calculator import FourPillars
from .constants import BRANCH_ELEMENT, STEM_ELEMENT
from .elements import element_balance
from .relations import SIX_CLASHES, SIX_COMBINATIONS, THREE_HARMONY
from .strength import day_master_strength
from .ten_gods import CONTROLS, PRODUCES, TEN_GODS, ten_god_for


@dataclass
class PairInteraction:
    a_label: str
    b_label: str
    a_branch: str
    b_branch: str
    kind: str               # "clash" | "six_combination" | "three_harmony_partial"
    transforms_to: str | None
    note: str


@dataclass
class CompatibilityDeep:
    total_score: int
    verdict: str
    day_master_relation: dict
    spouse_star_check: dict
    useful_god_exchange: dict
    branch_interactions: list[PairInteraction]
    area_scores: dict[str, int]
    element_blend: dict[str, float]
    shared_weakness: list[str]
    complementary_strengths: list[str]
    harmony: list[str]
    tension: list[str]


def _dm_relation(a_elem: str, b_elem: str) -> tuple[str, str, int]:
    """Return (kind, note, score_delta)."""
    if a_elem == b_elem:
        return (
            "same",
            f"Shared Day-Master element ({a_elem}) — similar instincts, comfortable, risk of stagnation.",
            5,
        )
    if PRODUCES[a_elem] == b_elem:
        return (
            "a_produces_b",
            f"{a_elem.title()} produces {b_elem}: A nourishes B. A gives energy; B receives and grows.",
            18,
        )
    if PRODUCES[b_elem] == a_elem:
        return (
            "b_produces_a",
            f"{b_elem.title()} produces {a_elem}: B nourishes A. Classic support pairing; B gives strength to A.",
            18,
        )
    if CONTROLS[a_elem] == b_elem:
        return (
            "a_controls_b",
            f"{a_elem.title()} controls {b_elem}: A disciplines B. Power imbalance; A leads, B complies.",
            -12,
        )
    if CONTROLS[b_elem] == a_elem:
        return (
            "b_controls_a",
            f"{b_elem.title()} controls {a_elem}: B disciplines A. Power imbalance; B leads, A complies.",
            -12,
        )
    return ("neutral", "Neutral elemental interaction.", 0)


def _spouse_star_check(
    subject_fp: FourPillars,
    partner_fp: FourPillars,
    subject_gender: str | None,
) -> dict:
    """Check whether the partner's Day Master plays the 'spouse star' role in subject's chart.

    For male subject: spouse star = Wealth (what DM controls).
    For female subject: spouse star = Officer (what controls DM).
    """
    gender = (subject_gender or "").strip().lower()
    dm_elem = subject_fp.day_master_element
    partner_dm_elem = partner_fp.day_master_element

    if gender == "male":
        spouse_elem = CONTROLS[dm_elem]  # wealth element
        role = "wealth (wife star)"
    elif gender == "female":
        # officer = the element that controls DM
        spouse_elem = next(e for e, v in CONTROLS.items() if v == dm_elem)
        role = "officer (husband star)"
    else:
        return {"applicable": False, "note": "Subject gender unknown; skipping spouse-star check."}

    match = partner_dm_elem == spouse_elem
    return {
        "applicable": True,
        "role": role,
        "expected_element": spouse_elem,
        "partner_dm_element": partner_dm_elem,
        "partner_plays_spouse_star": match,
        "note": (
            f"Partner's {partner_dm_elem} Day Master plays the expected "
            f"{role} of {spouse_elem} — classical spouse-star fit."
            if match
            else
            f"Partner's {partner_dm_elem} Day Master is not the expected {spouse_elem} "
            f"spouse-star element; relationship works through other channels."
        ),
    }


def _useful_god_exchange(a_fp: FourPillars, b_fp: FourPillars) -> dict:
    a_dms = day_master_strength(a_fp)
    b_dms = day_master_strength(b_fp)
    a_bal = element_balance(a_fp).as_dict
    b_bal = element_balance(b_fp).as_dict

    def _presence(elem: str, bal: dict[str, float]) -> float:
        total = sum(bal.values()) or 1.0
        return bal.get(elem, 0.0) / total * 100.0

    a_useful_in_b = _presence(a_dms.useful_god, b_bal)
    b_useful_in_a = _presence(b_dms.useful_god, a_bal)

    return {
        "a_useful_god": a_dms.useful_god,
        "b_useful_god": b_dms.useful_god,
        "a_useful_percent_in_b": round(a_useful_in_b, 1),
        "b_useful_percent_in_a": round(b_useful_in_a, 1),
        "a_gets_what_a_needs": round(b_useful_in_a, 1) >= 15.0,
        "b_gets_what_b_needs": round(a_useful_in_b, 1) >= 15.0,
        "note": (
            f"A's Useful God is {a_dms.useful_god} ({round(a_useful_in_b,1)}% present in B's chart); "
            f"B's Useful God is {b_dms.useful_god} ({round(b_useful_in_a,1)}% present in A's chart). "
            "≥15% indicates the partner brings what the other needs."
        ),
    }


def _branch_interactions(a_fp: FourPillars, b_fp: FourPillars) -> list[PairInteraction]:
    labels = ["Year", "Month", "Day", "Hour"]
    a_branches = [
        (labels[0], a_fp.year.branch, a_fp.year.branch_index),
        (labels[1], a_fp.month.branch, a_fp.month.branch_index),
        (labels[2], a_fp.day.branch, a_fp.day.branch_index),
        (labels[3], a_fp.hour.branch, a_fp.hour.branch_index),
    ]
    b_branches = [
        (labels[0], b_fp.year.branch, b_fp.year.branch_index),
        (labels[1], b_fp.month.branch, b_fp.month.branch_index),
        (labels[2], b_fp.day.branch, b_fp.day.branch_index),
        (labels[3], b_fp.hour.branch, b_fp.hour.branch_index),
    ]
    out: list[PairInteraction] = []
    for (la, ca, ia), (lb, cb, ib) in product(a_branches, b_branches):
        pair = frozenset({ia, ib})
        if pair in SIX_CLASHES:
            out.append(PairInteraction(
                a_label=la, b_label=lb, a_branch=ca, b_branch=cb,
                kind="clash", transforms_to=None,
                note=f"Clash (六冲) between A's {la} and B's {lb}: friction in that life area.",
            ))
        elif pair in SIX_COMBINATIONS:
            out.append(PairInteraction(
                a_label=la, b_label=lb, a_branch=ca, b_branch=cb,
                kind="six_combination", transforms_to=SIX_COMBINATIONS[pair],
                note=(
                    f"Harmonious pair (六合) between A's {la} and B's {lb} → {SIX_COMBINATIONS[pair]}: "
                    "magnetic attraction and easy flow in this life area."
                ),
            ))
    # Three-harmony completion: if A has two of a triad and B contributes the third
    a_branch_set = {ib for _, _, ib in a_branches}
    b_branch_set = {ib for _, _, ib in b_branches}
    for triad, element in THREE_HARMONY.items():
        if len(triad & a_branch_set) == 2 and len(triad & b_branch_set) >= 1:
            missing = triad - a_branch_set
            if missing and next(iter(missing)) in b_branch_set:
                out.append(PairInteraction(
                    a_label="chart", b_label="chart", a_branch="—", b_branch="—",
                    kind="three_harmony_partial", transforms_to=element,
                    note=f"B's chart completes A's Three-Harmony (三合) → {element}: "
                         "B unlocks a dormant strength in A.",
                ))
        if len(triad & b_branch_set) == 2 and len(triad & a_branch_set) >= 1:
            missing = triad - b_branch_set
            if missing and next(iter(missing)) in a_branch_set:
                out.append(PairInteraction(
                    a_label="chart", b_label="chart", a_branch="—", b_branch="—",
                    kind="three_harmony_partial", transforms_to=element,
                    note=f"A's chart completes B's Three-Harmony (三合) → {element}: "
                         "A unlocks a dormant strength in B.",
                ))
    return out


def build_deep_compatibility(
    a_fp: FourPillars,
    b_fp: FourPillars,
    a_gender: str | None = None,
    b_gender: str | None = None,
) -> CompatibilityDeep:
    # Day Master relation
    kind, dm_note, dm_score = _dm_relation(a_fp.day_master_element, b_fp.day_master_element)
    dm_relation = {
        "a_element": a_fp.day_master_element,
        "b_element": b_fp.day_master_element,
        "kind": kind,
        "note": dm_note,
    }

    # Spouse star check (on both sides)
    a_spouse = _spouse_star_check(a_fp, b_fp, a_gender)
    b_spouse = _spouse_star_check(b_fp, a_fp, b_gender)
    spouse_check = {"a_checks_b": a_spouse, "b_checks_a": b_spouse}

    # Useful God exchange
    ug = _useful_god_exchange(a_fp, b_fp)

    # Branch interactions
    interactions = _branch_interactions(a_fp, b_fp)
    clash_count = sum(1 for i in interactions if i.kind == "clash")
    combo_count = sum(1 for i in interactions if i.kind == "six_combination")
    triad_boost = sum(1 for i in interactions if i.kind == "three_harmony_partial")

    # Day-branch special check (romance palace)
    day_pair = frozenset({a_fp.day.branch_index, b_fp.day.branch_index})
    day_six_combo = SIX_COMBINATIONS.get(day_pair)
    day_clash = day_pair in SIX_CLASHES

    # Element blend
    a_bal = element_balance(a_fp).as_dict
    b_bal = element_balance(b_fp).as_dict
    blend = {k: round(a_bal[k] + b_bal[k], 2) for k in a_bal}

    # Complementary strengths / shared weakness
    total = sum(blend.values()) or 1.0
    blend_pct = {k: v / total * 100 for k, v in blend.items()}
    shared_weak = [k for k, v in blend_pct.items() if v < 8.0]
    dom_a = max(a_bal, key=a_bal.get); weak_a = min(a_bal, key=a_bal.get)
    dom_b = max(b_bal, key=b_bal.get); weak_b = min(b_bal, key=b_bal.get)
    comps: list[str] = []
    if dom_b == weak_a:
        comps.append(f"B's dominant {dom_b} fills A's weakness in {weak_a}.")
    if dom_a == weak_b:
        comps.append(f"A's dominant {dom_a} fills B's weakness in {weak_b}.")

    # Area scoring
    romance = 55 + dm_score
    if day_six_combo:
        romance += 20
    if day_clash:
        romance -= 15
    if a_spouse.get("partner_plays_spouse_star") or b_spouse.get("partner_plays_spouse_star"):
        romance += 10
    romance += combo_count * 3
    romance -= clash_count * 2
    romance = max(0, min(100, romance))

    # Communication: depends on Ten-God texture of A's stems vs B's DM + vice versa
    def _stem_communication(a: FourPillars, b: FourPillars) -> int:
        score = 0
        for s in (a.year.stem_index, a.month.stem_index, a.hour.stem_index):
            tg = ten_god_for(b.day.stem_index, s)
            # Resource and Eating God are gentle; Killings/Rob are sharp
            if tg in {"direct_resource", "indirect_resource", "eating_god", "friend"}:
                score += 2
            elif tg in {"seven_killings", "rob_wealth"}:
                score -= 2
        return score
    comm = 55 + _stem_communication(a_fp, b_fp) + _stem_communication(b_fp, a_fp)
    comm -= clash_count * 3
    comm += combo_count * 2
    comm = max(0, min(100, comm))

    # Finance: wealth star alignment
    def _wealth_presence(fp: FourPillars) -> float:
        dm = fp.day_master_element
        wealth_elem = CONTROLS[dm]
        bal = element_balance(fp).as_dict
        total_b = sum(bal.values()) or 1.0
        return bal[wealth_elem] / total_b * 100
    finance = 50
    finance += int((_wealth_presence(a_fp) + _wealth_presence(b_fp)) / 4)
    # If A's or B's wealth star is the dominant combined element → boost
    combined_dom = max(blend, key=blend.get)
    if CONTROLS[a_fp.day_master_element] == combined_dom or CONTROLS[b_fp.day_master_element] == combined_dom:
        finance += 15
    finance = max(0, min(100, finance))

    # Family: resource star presence + year-pillar harmony
    family = 50
    # year-branch six-combination?
    year_pair = frozenset({a_fp.year.branch_index, b_fp.year.branch_index})
    if year_pair in SIX_COMBINATIONS: family += 12
    if year_pair in SIX_CLASHES: family -= 15
    # resource elements (mother element for each DM) present in blend
    for dm in (a_fp.day_master_element, b_fp.day_master_element):
        mother = next(e for e, v in PRODUCES.items() if v == dm)
        family += int(blend_pct[mother] / 5)
    family = max(0, min(100, family))

    # Long-term: Useful-God exchange + structural fit
    long_term = 50 + dm_score
    if ug["a_gets_what_a_needs"]: long_term += 10
    if ug["b_gets_what_b_needs"]: long_term += 10
    long_term += triad_boost * 8
    long_term -= clash_count * 3
    long_term = max(0, min(100, long_term))

    areas = {
        "romance": romance,
        "communication": comm,
        "finance": finance,
        "family": family,
        "long_term": long_term,
    }

    total_score = round(sum(areas.values()) / len(areas))

    # Narrative harmony / tension
    harmony: list[str] = [dm_note]
    if day_six_combo:
        harmony.append(f"Day-branches form 六合 → {day_six_combo}: deep intimate chemistry.")
    if a_spouse.get("partner_plays_spouse_star"):
        harmony.append(a_spouse["note"])
    if b_spouse.get("partner_plays_spouse_star"):
        harmony.append(b_spouse["note"])
    if ug["a_gets_what_a_needs"] and ug["b_gets_what_b_needs"]:
        harmony.append("Mutual Useful-God exchange — each brings what the other's chart needs.")
    elif ug["a_gets_what_a_needs"]:
        harmony.append("B's chart supplies A's Useful God — B supports A's growth.")
    elif ug["b_gets_what_b_needs"]:
        harmony.append("A's chart supplies B's Useful God — A supports B's growth.")
    harmony += comps

    tension: list[str] = []
    if day_clash:
        tension.append("Day-branches clash (六冲) — intimate friction, opposing instincts.")
    if kind in {"a_controls_b", "b_controls_a"}:
        tension.append(dm_note + " Negotiate decision-making domains explicitly.")
    if clash_count >= 2:
        tension.append(f"{clash_count} branch clashes across pillars — multiple friction points.")
    if shared_weak:
        tension.append(
            f"Shared weak element(s) — {', '.join(shared_weak)} — "
            "neither partner pushes the other into those domains; supplement consciously."
        )

    # Verdict
    if total_score >= 80: verdict = "Highly compatible — complementary energies across the board."
    elif total_score >= 65: verdict = "Strong match with room to grow."
    elif total_score >= 50: verdict = "Workable — requires conscious effort on friction points."
    elif total_score >= 35: verdict = "Challenging — significant elemental tension."
    else:                   verdict = "Difficult pairing — needs deep compromise."

    return CompatibilityDeep(
        total_score=total_score,
        verdict=verdict,
        day_master_relation=dm_relation,
        spouse_star_check=spouse_check,
        useful_god_exchange=ug,
        branch_interactions=interactions,
        area_scores=areas,
        element_blend=blend,
        shared_weakness=shared_weak,
        complementary_strengths=comps,
        harmony=harmony,
        tension=tension,
    )
