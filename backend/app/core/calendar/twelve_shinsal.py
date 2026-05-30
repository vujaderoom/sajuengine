from __future__ import annotations

from app.core.calendar.ganzhi import EARTHLY_BRANCHES, branch_index

SHINSAL_ORDER = ["劫殺", "災殺", "天殺", "地殺", "年殺", "月殺", "亡身殺", "將星殺", "攀鞍殺", "驛馬殺", "六害殺", "華蓋殺"]

# 삼합국 기준 12신살 시작점. 기준지지에서 해당 그룹을 잡고 target과의 거리로 산출한다.
# 寅午戌(火局) -> 亥부터 劫殺
# 申子辰(水局) -> 巳부터 劫殺
# 巳酉丑(金局) -> 寅부터 劫殺
# 亥卯未(木局) -> 申부터 劫殺
GROUP_START = {
    "寅": "亥", "午": "亥", "戌": "亥",
    "申": "巳", "子": "巳", "辰": "巳",
    "巳": "寅", "酉": "寅", "丑": "寅",
    "亥": "申", "卯": "申", "未": "申",
}


def twelve_shinsal(base_branch: str, target_branch: str) -> str:
    start_branch = GROUP_START[base_branch]
    offset = (branch_index(target_branch) - branch_index(start_branch)) % 12
    return SHINSAL_ORDER[offset]


def twelve_shinsal_for_chart(chart: dict[str, str], base: str = "year") -> dict[str, str]:
    base_branch = chart[base][1]
    return {
        "year": twelve_shinsal(base_branch, chart["year"][1]),
        "month": twelve_shinsal(base_branch, chart["month"][1]),
        "day": twelve_shinsal(base_branch, chart["day"][1]),
        "hour": twelve_shinsal(base_branch, chart["hour"][1]),
    }


def twelve_shinsal_multi_base_for_chart(chart: dict[str, str]) -> dict[str, dict[str, str]]:
    return {
        "year_base": twelve_shinsal_for_chart(chart, "year"),
        "day_base": twelve_shinsal_for_chart(chart, "day"),
        "month_base": twelve_shinsal_for_chart(chart, "month"),
    }
