"""Chinese physiognomy (面相) reading engine.

Maps a structured set of user-selected facial traits onto traditional
physiognomy interpretations. Built around:

  * San Ting (三停) — the three horizontal thirds of the face (forehead,
    mid-face, chin) which map to early / middle / late life.
  * Twelve Palaces (十二宫) — a simplified subset covering the most
    popular features users care about (career, wealth, relationships,
    health, children, travel).
  * Five Elements (五行) — face shape is mapped to a governing element,
    which colours the personality summary.

The engine is deterministic and runs without any vision model. Inputs
are all categorical string traits; the caller (a form, or a future
vision pipeline that converts an image to traits) decides how to obtain
them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Trait categories
# ---------------------------------------------------------------------------

FaceShape = Literal["round", "square", "oval", "long", "heart", "diamond"]
Forehead = Literal["high", "medium", "low", "narrow", "wide"]
Brow = Literal["thick", "medium", "thin", "arched", "straight"]
Eye = Literal["big", "medium", "small", "phoenix", "deep"]
Nose = Literal["straight", "high", "flat", "hooked", "small"]
Mouth = Literal["full", "medium", "thin", "wide", "small"]
Ear = Literal["large", "medium", "small", "attached", "detached"]
Chin = Literal["strong", "rounded", "pointed", "double", "receding"]
Cheek = Literal["high", "full", "flat", "hollow"]
SkinTone = Literal["bright", "neutral", "dull", "ruddy"]

FACE_SHAPE_ELEMENT: dict[FaceShape, str] = {
    "round":   "water",
    "square":  "metal",
    "oval":    "wood",
    "long":    "wood",
    "heart":   "fire",
    "diamond": "fire",
}

ELEMENT_PERSONALITY = {
    "wood":  "grows steadily, leads through vision, and thrives in roles that reward patience and long-term thinking",
    "fire":  "radiates energy, inspires others, and does best where charisma and quick decisions are valued",
    "earth": "carries calm stability, becomes the trusted anchor in any group, and excels at systems and service",
    "metal": "moves with discipline and precision, cuts through noise, and shines in leadership or technical craft",
    "water": "reads people intuitively, adapts fluidly, and creates opportunity through connections and wisdom",
}


# ---------------------------------------------------------------------------
# Internal lookup tables — each returns (score_0_100, one-line verdict).
# Scores are combined later into the macro "life area" scores.
# ---------------------------------------------------------------------------

_FOREHEAD: dict[Forehead, tuple[int, str]] = {
    "high":   (88, "High, full forehead: strong intellect and bright early years (官禄宫)."),
    "wide":   (82, "Wide forehead: broad-minded, blessed by ancestors and early fortune."),
    "medium": (72, "Balanced forehead: steady early life and clear thinking."),
    "narrow": (55, "Narrow forehead: early challenges, but forge independence."),
    "low":    (50, "Low forehead: slow start; rewards come after age 30."),
}

_BROWS: dict[Brow, tuple[int, str]] = {
    "arched":   (85, "Arched brows (眉宇): expressive, natural leader, strong siblings/friends palace."),
    "thick":    (78, "Thick brows: loyalty, courage, reliable friendships."),
    "medium":   (72, "Even brows: balanced temperament and stable relationships."),
    "straight": (70, "Straight brows: practical, disciplined, steady siblings palace."),
    "thin":     (58, "Thin brows: sensitive, cultivate patience with siblings and close friends."),
}

_EYES: dict[Eye, tuple[int, str]] = {
    "phoenix": (92, "Phoenix eyes (丹凤眼): noble bearing, unusual achievement and influence."),
    "deep":    (80, "Deep-set eyes: profound thinker; strong career palace once settled."),
    "big":     (78, "Big bright eyes: warmth, charisma, fortunate in romance."),
    "medium":  (72, "Even eyes: balanced emotion and judgment."),
    "small":   (65, "Small focused eyes: discerning and self-reliant."),
}

_NOSE: dict[Nose, tuple[int, str]] = {
    "high":     (90, "High, full nose (财帛宫): strong wealth palace — income stability and prosperity."),
    "straight": (82, "Straight nose: steady income and integrity."),
    "small":    (65, "Small nose: income comes through careful accumulation, not windfalls."),
    "flat":     (58, "Flat nose bridge: wealth builds late; partnerships help."),
    "hooked":   (60, "Hooked nose: sharp wealth instincts; avoid risky ventures."),
}

_MOUTH: dict[Mouth, tuple[int, str]] = {
    "full":   (85, "Full lips (口): generous heart, strong communication, lifelong abundance."),
    "wide":   (80, "Wide mouth: bold, persuasive, rises through speech and leadership."),
    "medium": (72, "Balanced mouth: measured words and reliable speech."),
    "thin":   (60, "Thin lips: precise and truthful; cultivate warmth in words."),
    "small":  (62, "Small mouth: careful speaker; blessings come through listening."),
}

_EARS: dict[Ear, tuple[int, str]] = {
    "large":    (88, "Large ears: long life, wisdom, and a strong parents palace (父母宫)."),
    "detached": (80, "Detached lobes: independent thinker, self-made path."),
    "medium":   (72, "Even ears: balanced childhood fortune and steady health."),
    "attached": (68, "Attached lobes: family-centred, loyal, tradition-minded."),
    "small":    (62, "Small ears: protect your health and honour elders."),
}

_CHIN: dict[Chin, tuple[int, str]] = {
    "strong":   (88, "Strong chin (地阁): prosperous late years, property luck, loyal subordinates."),
    "rounded":  (80, "Rounded full chin: stable late life and family harmony."),
    "double":   (78, "Double chin: abundance and resources in later years."),
    "pointed":  (62, "Pointed chin: sharp-minded but pace yourself after 55."),
    "receding": (55, "Receding chin: build savings and community well before retirement."),
}

_CHEEK: dict[Cheek, tuple[int, str]] = {
    "high":   (85, "High cheekbones (颧骨): authority, power, respect from peers."),
    "full":   (80, "Full cheeks: good health qi and popularity."),
    "flat":   (65, "Flat cheeks: work on presence — earn authority through action."),
    "hollow": (55, "Hollow cheeks: guard your health and energy carefully."),
}

_SKIN: dict[SkinTone, tuple[int, str]] = {
    "bright":  (88, "Bright skin tone (神气): vitality and good fortune are active now."),
    "ruddy":   (78, "Ruddy glow: warm blood qi, strong drive."),
    "neutral": (72, "Neutral tone: balanced qi and steady energy."),
    "dull":    (55, "Dull tone: rest, adjust diet, and refresh your sleep."),
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FeatureReading:
    feature: str            # e.g. "forehead"
    trait: str              # e.g. "high"
    palace: str             # e.g. "官禄宫 (Career)"
    score: int              # 0-100
    verdict: str            # one-line description


@dataclass
class FaceReading:
    face_shape: str
    governing_element: str
    personality_summary: str
    features: list[FeatureReading]
    # Macro life-area scores aggregated from features:
    career_score: int
    wealth_score: int
    relationships_score: int
    health_score: int
    family_score: int
    overall_score: int
    # Narrative sections:
    san_ting_upper: str    # forehead / early life 15-30
    san_ting_middle: str   # mid-face / mid-life 31-50
    san_ting_lower: str    # chin / late life 51+
    strengths: list[str]
    watchouts: list[str]
    recommendations: list[str]


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

_FEATURE_PALACE = {
    "forehead": "官禄宫 (Career / early life)",
    "brows":    "兄弟宫 (Siblings & close ties)",
    "eyes":     "夫妻宫 (Relationships)",
    "nose":     "财帛宫 (Wealth)",
    "mouth":    "口德宫 (Speech & abundance)",
    "ears":     "父母宫 (Parents & longevity)",
    "chin":     "地阁宫 (Late life & property)",
    "cheeks":   "颧骨 (Authority & reputation)",
    "skin":     "神气 (Vital qi)",
}


def _pick(lookup: dict, key: str, fallback: tuple[int, str]) -> tuple[int, str]:
    return lookup.get(key, fallback)  # type: ignore[return-value]


def analyse_face(
    face_shape: str,
    forehead: str,
    brows: str,
    eyes: str,
    nose: str,
    mouth: str,
    ears: str,
    chin: str,
    cheeks: str,
    skin: str,
) -> FaceReading:
    """Map a full set of facial traits onto a rich physiognomy reading."""

    shape_elem = FACE_SHAPE_ELEMENT.get(face_shape, "earth")
    personality = (
        f"Your {face_shape} face is governed by the {shape_elem} element. "
        f"You {ELEMENT_PERSONALITY.get(shape_elem, ELEMENT_PERSONALITY['earth'])}."
    )

    readings: list[FeatureReading] = []
    for feat, trait, lookup in [
        ("forehead", forehead, _FOREHEAD),
        ("brows",    brows,    _BROWS),
        ("eyes",     eyes,     _EYES),
        ("nose",     nose,     _NOSE),
        ("mouth",    mouth,    _MOUTH),
        ("ears",     ears,     _EARS),
        ("chin",     chin,     _CHIN),
        ("cheeks",   cheeks,   _CHEEK),
        ("skin",     skin,     _SKIN),
    ]:
        score, verdict = _pick(lookup, trait, (70, "Balanced feature."))
        readings.append(
            FeatureReading(
                feature=feat,
                trait=trait,
                palace=_FEATURE_PALACE.get(feat, feat),
                score=score,
                verdict=verdict,
            )
        )

    by = {r.feature: r for r in readings}

    career = round((by["forehead"].score * 0.5) + (by["cheeks"].score * 0.3) + (by["eyes"].score * 0.2))
    wealth = round((by["nose"].score * 0.6) + (by["chin"].score * 0.25) + (by["mouth"].score * 0.15))
    relationships = round((by["eyes"].score * 0.5) + (by["mouth"].score * 0.3) + (by["brows"].score * 0.2))
    health = round((by["ears"].score * 0.35) + (by["cheeks"].score * 0.3) + (by["skin"].score * 0.35))
    family = round((by["ears"].score * 0.5) + (by["chin"].score * 0.3) + (by["brows"].score * 0.2))

    overall = round((career + wealth + relationships + health + family) / 5)

    san_ting_upper = (
        f"Your forehead speaks to ages 15-30. {by['forehead'].verdict} "
        f"Bright brows add: {by['brows'].verdict.lower()}"
    )
    san_ting_middle = (
        f"The middle third (eyes, nose, cheeks) governs ages 31-50. "
        f"{by['eyes'].verdict} {by['nose'].verdict}"
    )
    san_ting_lower = (
        f"Chin, mouth and jaw represent ages 51+. "
        f"{by['chin'].verdict} {by['mouth'].verdict}"
    )

    strengths: list[str] = [r.verdict for r in readings if r.score >= 80]
    watchouts: list[str] = [r.verdict for r in readings if r.score < 65]
    if not strengths:
        strengths = ["Balanced features overall — a steady temperament and reliable long-term luck."]

    recs: list[str] = []
    if wealth < 70:
        recs.append("Keep a clear household budget and avoid speculative ventures until age 40.")
    if relationships < 70:
        recs.append("Invest time in communication — slow, clear speech improves partnership luck.")
    if health < 70:
        recs.append("Prioritise sleep and balanced meals; your 神气 (vital qi) shows room to improve.")
    if career < 70:
        recs.append("Aim for mentorship and steady achievement over rapid promotion in the early career.")
    if not recs:
        recs.append("Maintain your current routines — the features suggest your path is well aligned.")

    return FaceReading(
        face_shape=face_shape,
        governing_element=shape_elem,
        personality_summary=personality,
        features=readings,
        career_score=career,
        wealth_score=wealth,
        relationships_score=relationships,
        health_score=health,
        family_score=family,
        overall_score=overall,
        san_ting_upper=san_ting_upper,
        san_ting_middle=san_ting_middle,
        san_ting_lower=san_ting_lower,
        strengths=strengths,
        watchouts=watchouts,
        recommendations=recs,
    )
