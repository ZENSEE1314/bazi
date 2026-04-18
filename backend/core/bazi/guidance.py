"""Prevention & Enhancement guidance keyed off Day Master + Useful God."""

from __future__ import annotations

# Full element-to-lifestyle mapping. Each element has colors, foods, activities,
# environments, numbers, directions, gemstones, careers, and relationship cues.
ELEMENT_GUIDANCE: dict[str, dict] = {
    "wood": {
        "colors": ["green", "teal", "emerald", "forest", "mint"],
        "foods_favor": ["green vegetables", "sprouts", "citrus", "sour flavors", "sprouted grains"],
        "foods_avoid": ["excessive sugar", "processed white flour", "deep-fried"],
        "activities_favor": ["gardening", "forest walks", "morning yoga", "learning a new language", "starting a project"],
        "activities_avoid": ["prolonged stillness", "over-controlling outcomes", "isolating from growth opportunities"],
        "environments_favor": ["open green spaces", "east-facing rooms", "libraries", "rooms with live plants"],
        "numbers": [3, 4],
        "direction": "East",
        "gemstones": ["emerald", "jade", "green aventurine"],
        "careers": ["education", "publishing", "wellness", "botany", "non-profit", "coaching"],
    },
    "fire": {
        "colors": ["red", "pink", "orange", "purple", "magenta"],
        "foods_favor": ["bitter greens", "coffee (moderate)", "red foods", "warming spices", "lamb"],
        "foods_avoid": ["excess raw cold foods", "ice water with meals", "chronic under-eating"],
        "activities_favor": ["cardio", "public speaking", "social gatherings", "dance", "sunlight"],
        "activities_avoid": ["isolation", "long indoor winters", "chronic under-stimulation"],
        "environments_favor": ["well-lit spaces", "south-facing rooms", "stages", "warm interiors"],
        "numbers": [9],
        "direction": "South",
        "gemstones": ["ruby", "garnet", "carnelian", "red jasper"],
        "careers": ["marketing", "performance", "hospitality", "beauty", "restaurants", "media"],
    },
    "earth": {
        "colors": ["yellow", "beige", "brown", "ochre", "camel", "terracotta"],
        "foods_favor": ["root vegetables", "whole grains", "slow-cooked stews", "naturally sweet foods"],
        "foods_avoid": ["excess spicy", "irregular meals", "over-indulgence in sweets"],
        "activities_favor": ["pottery", "cooking", "real-estate", "ceremonies", "long-term committments"],
        "activities_avoid": ["hyper-mobility without rest", "impulsive decisions"],
        "environments_favor": ["solid architecture", "SW/NE rooms", "earth materials (stone, clay)"],
        "numbers": [2, 5, 8],
        "direction": "Southwest / Northeast",
        "gemstones": ["citrine", "tiger's eye", "amber", "yellow topaz"],
        "careers": ["real estate", "construction", "agriculture", "HR / operations", "insurance"],
    },
    "metal": {
        "colors": ["white", "silver", "gold", "champagne", "gray"],
        "foods_favor": ["pungent foods (onion, garlic, ginger)", "crisp textures", "white foods (rice, cauliflower)", "lung-supporting foods"],
        "foods_avoid": ["overly processed", "cold-and-damp foods", "excess dairy"],
        "activities_favor": ["strength training", "precision crafts", "decluttering", "martial arts", "meditation"],
        "activities_avoid": ["excessive talking", "late nights", "clutter accumulation"],
        "environments_favor": ["minimalist interiors", "west-facing rooms", "high ceilings"],
        "numbers": [6, 7],
        "direction": "West / Northwest",
        "gemstones": ["clear quartz", "hematite", "pyrite", "moonstone"],
        "careers": ["finance", "law", "engineering", "surgery", "military / police", "precision tech"],
    },
    "water": {
        "colors": ["black", "navy", "midnight blue", "deep purple"],
        "foods_favor": ["seafood", "seaweed", "black beans", "salty (moderate)", "pork"],
        "foods_avoid": ["excessive dairy", "processed sugars", "overcooked foods"],
        "activities_favor": ["swimming", "meditation", "writing", "strategic planning", "deep research"],
        "activities_avoid": ["overthinking without action", "chronic emotional isolation"],
        "environments_favor": ["near water", "north-facing rooms", "quiet study spaces"],
        "numbers": [1, 0],
        "direction": "North",
        "gemstones": ["black tourmaline", "sapphire", "lapis lazuli", "obsidian"],
        "careers": ["transport / logistics", "maritime", "consulting", "research", "writing", "trading"],
    },
}

STRENGTH_GUIDANCE = {
    "strong": {
        "prevent": [
            "Overworking your own element — it's already abundant. Forcing more creates stagnation.",
            "Saying yes to everything out of capability; your bandwidth is finite.",
            "Rigid routines that refuse to bend; excess strength turns into inflexibility.",
        ],
        "enhance": [
            "Channel the excess through your Useful God — output, wealth pursuits, or disciplined leadership.",
            "Delegate generously; you have enough to give without emptying.",
            "Seek environments that challenge you gently (not your weak element).",
        ],
    },
    "balanced": {
        "prevent": [
            "Complacency — a balanced chart can coast, missing peak opportunities.",
            "Overcorrecting toward any one element; you thrive in gentle variety.",
        ],
        "enhance": [
            "Diversify: multiple skills, multiple income streams, multiple friend circles.",
            "Pick Useful God activities weekly for gentle stimulation without imbalance.",
        ],
    },
    "weak": {
        "prevent": [
            "Over-giving — your own element is scarce. Guard your energy like currency.",
            "Draining environments (toxic colleagues, loud spaces, chaotic schedules).",
            "Activities governed by the Avoid God element; they deplete faster than you refill.",
            "Chronic multi-tasking; single-focus conserves strength.",
        ],
        "enhance": [
            "Bring in Useful God + same-element support systematically.",
            "Choose partners whose Day Master nourishes yours (see Love Outlook).",
            "Rest as strategy, not reward — your chart reloads via downtime.",
            "Protect sleep, diet, and boundaries more strictly than peers.",
        ],
    },
}


def element_guidance(elem: str) -> dict:
    return ELEMENT_GUIDANCE.get(elem, {})


def build_prevention_enhancement(
    day_master: str,
    useful_god: str,
    avoid_god: str,
    strength_level: str,
    weakest_element: str,
) -> dict:
    """Produce prevention & enhancement lists for a chart."""
    ug = element_guidance(useful_god)
    ag = element_guidance(avoid_god)
    we = element_guidance(weakest_element)

    strength_bits = STRENGTH_GUIDANCE.get(strength_level, STRENGTH_GUIDANCE["balanced"])

    prevention: list[str] = []
    enhancement: list[str] = []

    # Strength-based
    prevention.extend(strength_bits["prevent"])
    enhancement.extend(strength_bits["enhance"])

    # Avoid-God specifics (what to minimize in daily life)
    if ag:
        prevention.append(
            f"Minimize concentration of {avoid_god} colors ({', '.join(ag['colors'][:3])}) "
            "in bedroom and workspace."
        )
        if ag.get("activities_avoid"):
            prevention.append(
                f"Watch out for {avoid_god}-amplifying habits: {'; '.join(ag['activities_avoid'][:2])}."
            )
        if ag.get("foods_avoid"):
            prevention.append(
                f"Reduce {avoid_god}-heavy diet patterns: {', '.join(ag['foods_avoid'][:2])}."
            )

    # Useful-God specifics (what to do more)
    if ug:
        enhancement.append(
            f"Fill wardrobe and environment with {useful_god} colors ({', '.join(ug['colors'][:3])})."
        )
        if ug.get("activities_favor"):
            enhancement.append(
                f"Add {useful_god} practices weekly: {', '.join(ug['activities_favor'][:3])}."
            )
        if ug.get("foods_favor"):
            enhancement.append(
                f"Favor {useful_god}-nourishing foods: {', '.join(ug['foods_favor'][:3])}."
            )
        if ug.get("gemstones"):
            enhancement.append(f"Wear {useful_god} gemstones: {', '.join(ug['gemstones'][:3])}.")
        if ug.get("direction"):
            enhancement.append(f"Sleep / work facing {ug['direction']} when possible.")

    # Weakest element supplementation
    if we and weakest_element != avoid_god:
        enhancement.append(
            f"Consciously supplement your weakest element ({weakest_element}): "
            f"{', '.join(we['activities_favor'][:2])}."
        )

    return {
        "prevention": prevention,
        "enhancement": enhancement,
        "color_palette_favor": ug.get("colors", []),
        "color_palette_avoid": ag.get("colors", []),
        "foods_favor": ug.get("foods_favor", []),
        "foods_avoid": ag.get("foods_avoid", []),
        "gemstones": ug.get("gemstones", []),
        "lucky_numbers": ug.get("numbers", []),
        "best_direction": ug.get("direction", ""),
        "best_careers": ug.get("careers", []),
    }
