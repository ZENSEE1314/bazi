"""Numerology constants and digit interpretations.

This module encodes a simplified scoring model based on common Chinese
numerology conventions. It is NOT a full implementation of the He Luo Li Shu
(河洛理数) or Xuan Kong (玄空) 81-number systems. Those involve pair
interpretations tied to the Eight Trigrams and are a future enhancement.
"""

from __future__ import annotations

# Lo-Shu style digit-to-element mapping. Follows common Feng Shui numerology.
DIGIT_ELEMENT: dict[int, str] = {
    0: "water",
    1: "water",
    2: "earth",
    3: "wood",
    4: "wood",
    5: "earth",
    6: "metal",
    7: "metal",
    8: "earth",
    9: "fire",
}

# Cantonese/Mandarin homophony-driven cultural associations.
WEALTH_DIGITS: frozenset[int] = frozenset({6, 8, 9})   # 8=發, 6=順, 9=長/久
SAFETY_DIGITS: frozenset[int] = frozenset({1, 6, 8})   # stable/solid
HEALTH_DIGITS: frozenset[int] = frozenset({2, 5, 7})   # balanced/grounding

INAUSPICIOUS_DIGITS: frozenset[int] = frozenset({4})   # 四=死 homophone

ELEMENTS_GENERATIVE = ("wood", "fire", "earth", "metal", "water")
