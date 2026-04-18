"""Feng Shui home analysis against the occupant's Life Kua + Ba Zi.

Compares the house facing direction + main rooms to the person's lucky /
unlucky directions (八宅). Returns recommendations for every room the user
describes (bed head, desk, main door, stove, altar).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..bazi.kua import compute_life_kua
from ..bazi.mansions import LUCKY_CATEGORIES, UNLUCKY_CATEGORIES, mansions_for

DIRECTION_DEGREES = {
    "N": 0, "NE": 45, "E": 90, "SE": 135,
    "S": 180, "SW": 225, "W": 270, "NW": 315,
}
DIRECTION_ORDER = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def facing_from_degrees(deg: float) -> str:
    """Convert a bearing in degrees (0-360, 0=N) to one of the 8 cardinal dirs."""
    deg = deg % 360.0
    # Each octant is 45°; 0° N sits at the center of N (-22.5 .. 22.5).
    idx = int(((deg + 22.5) % 360) // 45)
    return DIRECTION_ORDER[idx]


# House type: a house "faces" one direction; it "sits" in the opposite.
# The "sitting" direction determines the house type (East group vs West group),
# which in turn maps to 8 mansions like a person's Kua.
EAST_HOUSE_SITTINGS = {"N", "S", "E", "SE"}   # Kan, Li, Zhen, Xun
WEST_HOUSE_SITTINGS = {"NE", "SW", "W", "NW"} # Gen, Kun, Dui, Qian


_OPPOSITE: dict[str, str] = {
    "N": "S", "S": "N", "E": "W", "W": "E",
    "NE": "SW", "SW": "NE", "NW": "SE", "SE": "NW",
}


@dataclass
class RoomVerdict:
    room: str
    current_direction: str
    direction_name: str
    category_cn: str | None
    category_en: str | None
    quality: str         # "lucky" | "unlucky" | "unknown"
    meaning: str
    recommendation: str


@dataclass
class FengShuiReading:
    life_kua_number: int
    life_kua_group: str
    house_facing: str
    house_sitting: str
    house_group: str
    person_house_match: bool
    match_note: str
    lucky_directions: list[dict]
    unlucky_directions: list[dict]
    room_verdicts: list[RoomVerdict]
    overall_score: int
    summary: str
    recommendations: list[str]


# Default best-room-direction mapping: what category each functional room wants.
_ROOM_IDEAL: dict[str, list[str]] = {
    "main_door":   ["sheng_qi", "yan_nian", "tian_yi"],   # wealth / relationships / health entries
    "bed_head":    ["fu_wei", "tian_yi", "yan_nian"],      # stability / health / longevity
    "desk":        ["sheng_qi", "fu_wei"],                 # wealth + stability
    "stove":       ["jue_ming", "wu_gui", "liu_sha", "huo_hai"],  # stove SITS in bad direction & FACES good (burning off bad qi)
    "altar":       ["fu_wei", "tian_yi"],
    "living_room": ["sheng_qi", "yan_nian", "fu_wei"],
    "kids_room":   ["tian_yi", "yan_nian"],
}


def _lookup_direction(mans: dict, direction: str) -> tuple[str | None, str | None, str, str]:
    """Return (category_key, quality, cn, meaning) for a given direction in the mansions table."""
    lucky = mans["lucky"]
    unlucky = mans["unlucky"]
    if direction in lucky:
        info = lucky[direction]
        return info["category_key"], "lucky", info["cn"], info["meaning"]
    if direction in unlucky:
        info = unlucky[direction]
        return info["category_key"], "unlucky", info["cn"], info["meaning"]
    return None, "unknown", "", ""


def _room_recommendation(room: str, quality: str, lucky_directions: list[str]) -> str:
    if room == "stove":
        # Stove is the inverse exception — it wants to *sit* in bad directions.
        if quality == "unlucky":
            return "Stove is ideal — it sits in a bad-qi direction, burning off negative energy."
        return "Consider relocating stove to a less auspicious direction, where it transforms bad qi."
    if quality == "lucky":
        return f"{room.replace('_', ' ').title()} is well-placed — keep as is."
    if quality == "unlucky":
        ideal = _ROOM_IDEAL.get(room, ["sheng_qi", "tian_yi", "yan_nian", "fu_wei"])
        return (
            f"{room.replace('_', ' ').title()} sits in an unfavorable direction. "
            f"Relocate toward {', '.join(lucky_directions)} if possible; "
            "otherwise counter with corrective cures (mirror, crystal, or earth/metal objects depending on element)."
        )
    return f"Direction unrecognised for {room}."


def analyse_home(
    solar_year: int,
    gender: str,
    house_facing: str,
    rooms: dict[str, str] | None = None,
) -> FengShuiReading:
    """Evaluate a house against a person's Life Kua.

    Parameters
    ----------
    solar_year : int
        Person's Ba Zi solar year (for Life Kua computation).
    gender : str
        'male' or 'female'.
    house_facing : str
        Compass direction the front door faces; one of
        N, NE, E, SE, S, SW, W, NW.
    rooms : dict[str, str] | None
        Optional map of {room_key: compass_direction}. Keys recognised:
        main_door, bed_head, desk, stove, altar, living_room, kids_room.
    """
    if house_facing not in DIRECTION_DEGREES:
        raise ValueError(f"Invalid house facing: {house_facing}")

    kua = compute_life_kua(solar_year, gender)
    mans = mansions_for(kua.number)

    house_sitting = _OPPOSITE[house_facing]
    house_group = "East" if house_sitting in EAST_HOUSE_SITTINGS else "West"
    person_house_match = (kua.group == house_group)

    match_note = (
        f"Your Life Kua is {kua.group} group; this house sits to the {house_sitting} "
        f"({house_group} group). "
        + ("They MATCH — the house is structurally compatible with you."
           if person_house_match else
           "They DON'T match — major room placements must actively compensate.")
    )

    lucky_dirs_list: list[dict] = []
    unlucky_dirs_list: list[dict] = []
    for direction, info in mans["lucky"].items():
        lucky_dirs_list.append({"direction": direction, **info})
    for direction, info in mans["unlucky"].items():
        unlucky_dirs_list.append({"direction": direction, **info})

    lucky_dir_names = [d["direction"] for d in lucky_dirs_list]

    room_verdicts: list[RoomVerdict] = []
    if rooms:
        for room, direction in rooms.items():
            cat_key, quality, cn, meaning = _lookup_direction(mans, direction)
            en_cat = ""
            if quality == "lucky" and cat_key in LUCKY_CATEGORIES:
                en_cat = LUCKY_CATEGORIES[cat_key]["en"]
            elif quality == "unlucky" and cat_key in UNLUCKY_CATEGORIES:
                en_cat = UNLUCKY_CATEGORIES[cat_key]["en"]
            rec = _room_recommendation(room, quality, lucky_dir_names)
            room_verdicts.append(RoomVerdict(
                room=room,
                current_direction=direction,
                direction_name={"N":"North","NE":"Northeast","E":"East","SE":"Southeast",
                                 "S":"South","SW":"Southwest","W":"West","NW":"Northwest"}[direction],
                category_cn=cn or None,
                category_en=en_cat or None,
                quality=quality,
                meaning=meaning,
                recommendation=rec,
            ))

    # Overall score: 50 baseline + boosts for compatibility + room placements
    score = 50
    if person_house_match:
        score += 20
    for rv in room_verdicts:
        if rv.quality == "lucky":
            score += 6 if rv.room in {"bed_head", "desk", "main_door"} else 3
        elif rv.quality == "unlucky":
            score -= 6 if rv.room in {"bed_head", "desk", "main_door"} else 3
    score = max(0, min(100, score))

    if score >= 80:
        summary = "Excellent home-person match. Few changes needed."
    elif score >= 65:
        summary = "Good match with minor adjustments possible."
    elif score >= 50:
        summary = "Workable home; several room placements are suboptimal — correctable."
    else:
        summary = "Home is structurally misaligned for you; significant remediation required or consider moving."

    recommendations: list[str] = []
    if not person_house_match:
        recommendations.append(
            f"You are {kua.group} group but this house is {house_group} group. "
            f"Prioritise placing your bed and desk in your personal lucky directions ({', '.join(lucky_dir_names)})."
        )
    bad_rooms = [rv for rv in room_verdicts if rv.quality == "unlucky" and rv.room in {"bed_head", "main_door"}]
    if bad_rooms:
        recommendations.append(
            "Critical rooms (" + ", ".join(rv.room for rv in bad_rooms) + ") "
            "are in inauspicious directions — these cause the most persistent impact. Move them first."
        )
    if score >= 80:
        recommendations.append("Maintain what you have; light tuning only (colors, plants) needed.")
    recommendations.append(
        "Use colors and materials of your Useful-God element in bedroom and workspace for daily support."
    )

    return FengShuiReading(
        life_kua_number=kua.number,
        life_kua_group=kua.group,
        house_facing=house_facing,
        house_sitting=house_sitting,
        house_group=house_group,
        person_house_match=person_house_match,
        match_note=match_note,
        lucky_directions=lucky_dirs_list,
        unlucky_directions=unlucky_dirs_list,
        room_verdicts=room_verdicts,
        overall_score=score,
        summary=summary,
        recommendations=recommendations,
    )
