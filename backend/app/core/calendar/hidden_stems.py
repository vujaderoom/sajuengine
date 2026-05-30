from __future__ import annotations

HIDDEN_STEMS = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}


def hidden_stems_for_branch(branch: str) -> list[str]:
    return HIDDEN_STEMS[branch]


def hidden_stems_for_chart(chart: dict[str, str]) -> dict[str, list[str]]:
    return {
        "year": hidden_stems_for_branch(chart["year"][1]),
        "month": hidden_stems_for_branch(chart["month"][1]),
        "day": hidden_stems_for_branch(chart["day"][1]),
        "hour": hidden_stems_for_branch(chart["hour"][1]),
    }
