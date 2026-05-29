from __future__ import annotations

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

JIAZI = [HEAVENLY_STEMS[i % 10] + EARTHLY_BRANCHES[i % 12] for i in range(60)]


def ganzhi(index: int) -> str:
    return JIAZI[index % 60]


def ganzhi_index(pillar: str) -> int:
    if pillar not in JIAZI:
        raise ValueError(f"unknown ganzhi pillar: {pillar}")
    return JIAZI.index(pillar)


def stem_index(stem: str) -> int:
    if stem not in HEAVENLY_STEMS:
        raise ValueError(f"unknown heavenly stem: {stem}")
    return HEAVENLY_STEMS.index(stem)


def branch_index(branch: str) -> int:
    if branch not in EARTHLY_BRANCHES:
        raise ValueError(f"unknown earthly branch: {branch}")
    return EARTHLY_BRANCHES.index(branch)
