"""Chinese palmistry (手相) reading engine.

Covers the four most-consulted lines — life (生命线), heart (感情线),
head (智慧线), fate (事业线 / 命运线) — plus an optional marriage line
(婚姻线), the palm element (4-element hand shape), and finger length
signals. Traits are categorical; the caller picks them from a form or
from a future image-analysis pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

HandShape = Literal["earth", "air", "water", "fire"]
FingerLen = Literal["short", "medium", "long"]
DominantHand = Literal["left", "right"]

LineLength = Literal["long", "medium", "short", "absent"]
LineDepth = Literal["deep", "medium", "shallow", "broken"]
MarriageLineCount = Literal["none", "one", "two", "many"]


# ---------------------------------------------------------------------------
# Hand-shape elements (Western-palmistry-style 4 elements mapped to
# Chinese 五行-lite interpretation)
# ---------------------------------------------------------------------------

HAND_SHAPE_INFO: dict[HandShape, dict[str, str]] = {
    "earth": {
        "label":       "Earth hand (square palm, short fingers)",
        "personality": "grounded, dependable, practical — a natural builder and trusted caretaker.",
        "strength":    "Finishes what you start; steady income and strong stability in later life.",
    },
    "air": {
        "label":       "Air hand (square palm, long fingers)",
        "personality": "intellectual, communicative, restless-minded — thrives in ideas, teaching, writing.",
        "strength":    "Career luck through words and networks; sharp analysis is your edge.",
    },
    "water": {
        "label":       "Water hand (long palm, long fingers)",
        "personality": "intuitive, emotional, artistic — reads people instantly and creates with feeling.",
        "strength":    "Deep relationship and creative lines; wealth flows through people and art.",
    },
    "fire": {
        "label":       "Fire hand (long palm, short fingers)",
        "personality": "energetic, enterprising, charismatic — fast decisions and bold ambition.",
        "strength":    "Career breakthroughs come early; leads teams, starts ventures, moves fast.",
    },
}


# ---------------------------------------------------------------------------
# Line-trait lookups → (score, verdict)
# ---------------------------------------------------------------------------

# Life line (生命线) — vitality, family, health trajectory
_LIFE_LENGTH: dict[LineLength, tuple[int, str]] = {
    "long":   (90, "Long life line: strong constitution, good longevity and rooted qi."),
    "medium": (75, "Medium life line: normal vitality; cultivate consistent habits."),
    "short":  (55, "Short life line — NOTE this never means short life. It signals external support matters more than sheer stamina."),
    "absent": (45, "Faint/absent life line: energy is uneven; prioritise sleep and stress management."),
}
_LIFE_DEPTH: dict[LineDepth, tuple[int, str]] = {
    "deep":    (88, "Deep line: robust health and strong family foundation."),
    "medium":  (72, "Clear medium line: steady health."),
    "shallow": (58, "Shallow line: moderate vitality; eat well and avoid over-work."),
    "broken":  (50, "Broken line: one significant transition — a move, career pivot, or health scare. Plan savings."),
}

# Heart line (感情线) — romance, emotion, partnerships
_HEART_LENGTH: dict[LineLength, tuple[int, str]] = {
    "long":   (88, "Long heart line: deep capacity to love, loyal partnerships."),
    "medium": (75, "Medium heart line: warm and balanced in love."),
    "short":  (55, "Short heart line: guarded emotions; takes time to trust."),
    "absent": (50, "Faint heart line: rational in love — pair with a partner who values directness."),
}
_HEART_DEPTH: dict[LineDepth, tuple[int, str]] = {
    "deep":    (90, "Deep heart line: passionate and devoted; a devoted partner."),
    "medium":  (75, "Clear heart line: honest, steady in affection."),
    "shallow": (60, "Shallow heart line: surface affection; cultivate emotional openness."),
    "broken":  (55, "Broken heart line: one serious heartbreak heals into wisdom — love arrives stronger afterwards."),
}

# Head line (智慧线) — thinking, decision making, career aptitude
_HEAD_LENGTH: dict[LineLength, tuple[int, str]] = {
    "long":   (90, "Long head line: deep thinker, strong academic and strategic mind."),
    "medium": (78, "Medium head line: balanced practical reasoning."),
    "short":  (60, "Short head line: action-first thinker; decisive under pressure."),
    "absent": (52, "Faint head line: feelings often lead decisions; cultivate structure."),
}
_HEAD_DEPTH: dict[LineDepth, tuple[int, str]] = {
    "deep":    (90, "Deep head line: sustained focus, strong memory, professional success."),
    "medium":  (75, "Clear head line: solid judgment."),
    "shallow": (60, "Shallow head line: mental stamina fluctuates — rest when needed."),
    "broken":  (55, "Broken head line: a pivotal education or career change after which life accelerates."),
}

# Fate line (事业线) — career path, destiny, purpose
_FATE_LENGTH: dict[LineLength, tuple[int, str]] = {
    "long":   (92, "Strong fate line running deep up the palm: clear career path, visible achievement."),
    "medium": (78, "Medium fate line: career builds in phases; each chapter pays off."),
    "short":  (65, "Short fate line: self-directed; you shape your own work independently."),
    "absent": (55, "No clear fate line: free of a fixed path — entrepreneurs and artists often show this."),
}
_FATE_DEPTH: dict[LineDepth, tuple[int, str]] = {
    "deep":    (90, "Deep fate line: destiny pulls strongly — major achievement is indicated."),
    "medium":  (75, "Clear fate line: reliable promotions and recognition."),
    "shallow": (62, "Shallow fate line: diversify income streams and keep a side project."),
    "broken":  (60, "Broken fate line: one major career pivot mid-life; it is needed growth."),
}

_MARRIAGE_LINES: dict[MarriageLineCount, tuple[int, str]] = {
    "none":  (60, "No clear marriage line: focus on self first; relationships arrive late and solid."),
    "one":   (90, "Single clear marriage line: one lasting, loyal partnership."),
    "two":   (72, "Two marriage lines: a short early attachment clears the way for the lasting one."),
    "many":  (62, "Multiple marriage lines: rich romantic life; take time to choose carefully."),
}

_FINGER_INTERP: dict[FingerLen, str] = {
    "short":  "Short fingers: decisive, fast to act, prefers big picture over detail.",
    "medium": "Medium fingers: balanced between action and reflection.",
    "long":   "Long fingers: careful, detail-oriented, thinks before acting.",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LineReading:
    line: str        # life / heart / head / fate / marriage
    chinese: str     # 生命线 / 感情线 / ...
    score: int       # 0-100
    length_verdict: str
    depth_verdict: str


@dataclass
class PalmReading:
    hand_shape: str
    hand_shape_label: str
    governing_element: str
    personality_summary: str
    dominant_hand: str
    finger_interpretation: str
    lines: list[LineReading]
    # Macro scores:
    vitality_score: int
    love_score: int
    intellect_score: int
    career_score: int
    marriage_score: int
    overall_score: int
    # Narrative sections:
    life_path: str
    love_path: str
    career_path: str
    strengths: list[str]
    watchouts: list[str]
    recommendations: list[str]


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _combo(
    length_lookup: dict, length_key: str,
    depth_lookup: dict, depth_key: str,
) -> tuple[int, str, str]:
    ls, lv = length_lookup.get(length_key, (70, "Balanced length."))
    ds, dv = depth_lookup.get(depth_key, (70, "Balanced depth."))
    score = round(ls * 0.55 + ds * 0.45)
    return score, lv, dv


def analyse_palm(
    hand_shape: str,
    dominant_hand: str,
    finger_length: str,
    life_length: str, life_depth: str,
    heart_length: str, heart_depth: str,
    head_length: str, head_depth: str,
    fate_length: str, fate_depth: str,
    marriage_lines: str = "one",
) -> PalmReading:
    info = HAND_SHAPE_INFO.get(hand_shape, HAND_SHAPE_INFO["earth"])
    personality = (
        f"{info['label']} — you are {info['personality']} {info['strength']}"
    )
    finger_txt = _FINGER_INTERP.get(finger_length, _FINGER_INTERP["medium"])

    # Score each line by combining length and depth.
    life_s, life_lv, life_dv = _combo(_LIFE_LENGTH, life_length, _LIFE_DEPTH, life_depth)
    heart_s, heart_lv, heart_dv = _combo(_HEART_LENGTH, heart_length, _HEART_DEPTH, heart_depth)
    head_s, head_lv, head_dv = _combo(_HEAD_LENGTH, head_length, _HEAD_DEPTH, head_depth)
    fate_s, fate_lv, fate_dv = _combo(_FATE_LENGTH, fate_length, _FATE_DEPTH, fate_depth)
    marriage_score, marriage_v = _MARRIAGE_LINES.get(
        marriage_lines, _MARRIAGE_LINES["one"]
    )

    lines = [
        LineReading("life",     "生命线", life_s, life_lv, life_dv),
        LineReading("heart",    "感情线", heart_s, heart_lv, heart_dv),
        LineReading("head",     "智慧线", head_s, head_lv, head_dv),
        LineReading("fate",     "事业线", fate_s, fate_lv, fate_dv),
        LineReading("marriage", "婚姻线", marriage_score,
                    marriage_v, f"Count: {marriage_lines}"),
    ]

    vitality = life_s
    love = round(heart_s * 0.7 + marriage_score * 0.3)
    intellect = head_s
    career = round(fate_s * 0.7 + head_s * 0.3)
    overall = round((vitality + love + intellect + career + marriage_score) / 5)

    life_path = (
        f"{life_lv} {life_dv} "
        f"Your dominant {dominant_hand} hand is the working palm, so these signs "
        f"describe the path you are actively shaping."
    )
    love_path = f"{heart_lv} {heart_dv} {marriage_v}"
    career_path = f"{fate_lv} {fate_dv} {head_lv}"

    strengths = [r.length_verdict for r in lines if r.score >= 80]
    if not strengths:
        strengths = ["Balanced palm — consistent, incremental growth across life areas."]
    watchouts = [r.length_verdict for r in lines if r.score < 65]

    recs: list[str] = []
    if vitality < 70:
        recs.append("Protect sleep, limit late-night screens; your 生命线 needs more root qi.")
    if career < 70:
        recs.append("Pick ONE career focus for the next 2 years — scattered efforts weaken the fate line.")
    if love < 70:
        recs.append("Practise honest emotional expression; strong love palaces grow from clear communication.")
    if intellect < 70:
        recs.append("Add a daily 20-minute reading or learning habit to sharpen the head line.")
    if not recs:
        recs.append("Continue your current rhythm — the palm indicates steady, aligned progress.")

    return PalmReading(
        hand_shape=hand_shape,
        hand_shape_label=info["label"],
        governing_element=hand_shape,
        personality_summary=personality,
        dominant_hand=dominant_hand,
        finger_interpretation=finger_txt,
        lines=lines,
        vitality_score=vitality,
        love_score=love,
        intellect_score=intellect,
        career_score=career,
        marriage_score=marriage_score,
        overall_score=overall,
        life_path=life_path,
        love_path=love_path,
        career_path=career_path,
        strengths=strengths,
        watchouts=watchouts,
        recommendations=recs,
    )
