from __future__ import annotations

from app.core.calendar.ganzhi import ganzhi_index

XUNKONG_TABLE = {
    0: ["戌", "亥"],   # 甲子旬
    10: ["申", "酉"],  # 甲戌旬
    20: ["午", "未"],  # 甲申旬
    30: ["辰", "巳"],  # 甲午旬
    40: ["寅", "卯"],  # 甲辰旬
    50: ["子", "丑"],  # 甲寅旬
}


def xunkong_for_pillar(pillar: str) -> list[str]:
    idx = ganzhi_index(pillar)
    xun_start = (idx // 10) * 10
    return XUNKONG_TABLE[xun_start]


def xunkong_for_chart(chart: dict[str, str]) -> dict[str, list[str]]:
    return {
        "year": xunkong_for_pillar(chart["year"]),
        "month": xunkong_for_pillar(chart["month"]),
        "day": xunkong_for_pillar(chart["day"]),
        "hour": xunkong_for_pillar(chart["hour"]),
    }
