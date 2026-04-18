"""Nayin (纳音) — the 'sound element' name of each pillar in the 60-cycle.

Every two consecutive pillars share one Nayin poetic name, e.g.
甲子乙丑 → 海中金 (Gold in the Sea).
"""

from __future__ import annotations

from .calculator import Pillar

# Indexed 0..29; each entry covers sex index 2*i and 2*i+1 in the 60 cycle.
_NAYIN: tuple[tuple[str, str, str], ...] = (
    ("海中金", "Hai Zhong Jin",  "Gold in the Sea"),
    ("炉中火", "Lu Zhong Huo",   "Fire in the Stove"),
    ("大林木", "Da Lin Mu",      "Wood of the Great Forest"),
    ("路旁土", "Lu Pang Tu",     "Earth by the Roadside"),
    ("剑锋金", "Jian Feng Jin",  "Metal of the Sword"),
    ("山头火", "Shan Tou Huo",   "Fire over the Hill"),
    ("涧下水", "Jian Xia Shui",  "Water under the Stream"),
    ("城头土", "Cheng Tou Tu",   "Earth of the City Wall"),
    ("白蜡金", "Bai La Jin",     "White Wax Metal"),
    ("杨柳木", "Yang Liu Mu",    "Willow Wood"),
    ("泉中水", "Quan Zhong Shui","Water in the Spring"),
    ("屋上土", "Wu Shang Tu",    "Earth on the Roof"),
    ("霹雳火", "Pi Li Huo",      "Thunder Fire"),
    ("松柏木", "Song Bai Mu",    "Pine and Cypress Wood"),
    ("长流水", "Chang Liu Shui", "Long Flowing Water"),
    ("沙中金", "Sha Zhong Jin",  "Gold in the Sand"),
    ("山下火", "Shan Xia Huo",   "Fire at the Foot of the Mountain"),
    ("平地木", "Ping Di Mu",     "Plain Wood"),
    ("壁上土", "Bi Shang Tu",    "Earth on the Wall"),
    ("金箔金", "Jin Bo Jin",     "Gold Foil Metal"),
    ("覆灯火", "Fu Deng Huo",    "Lamp Fire"),
    ("天河水", "Tian He Shui",   "Water of the Heavenly River"),
    ("大驿土", "Da Yi Tu",       "Earth of the Great Road"),
    ("钗钏金", "Chai Chuan Jin", "Hairpin Metal"),
    ("桑柘木", "Sang Zhe Mu",    "Mulberry Wood"),
    ("大溪水", "Da Xi Shui",     "Water of the Great Stream"),
    ("沙中土", "Sha Zhong Tu",   "Earth in the Sand"),
    ("天上火", "Tian Shang Huo", "Heavenly Fire"),
    ("石榴木", "Shi Liu Mu",     "Pomegranate Wood"),
    ("大海水", "Da Hai Shui",    "Water of the Great Sea"),
)


def nayin_for(pillar: Pillar) -> tuple[str, str, str]:
    """Return (cn, pinyin, en) nayin name for a pillar."""
    return _NAYIN[pillar.sexagenary_index // 2]
