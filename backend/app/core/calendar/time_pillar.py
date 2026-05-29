from __future__ import annotations

from datetime import datetime, timedelta

from app.core.calendar.day_pillar import day_pillar
from app.core.calendar.ganzhi import EARTHLY_BRANCHES, HEAVENLY_STEMS, branch_index, stem_index

HOUR_STEM_START_BY_DAY_STEM = {
    "甲": "甲",
    "己": "甲",
    "乙": "丙",
    "庚": "丙",
    "丙": "戊",
    "辛": "戊",
    "丁": "庚",
    "壬": "庚",
    "戊": "壬",
    "癸": "壬",
}


def effective_day_datetime(dt: datetime, use_late_zi_next_day: bool = False) -> datetime:
    # v0.1 option hook: 한국식 야자시/자정 경계 처리는 다음 단계에서 23:30 기준으로 확장한다.
    if use_late_zi_next_day and dt.hour == 23 and dt.minute >= 30:
        return dt + timedelta(days=1)
    return dt


def hour_branch(dt: datetime) -> str:
    hour = dt.hour
    if hour in [23, 0]:
        return "子"
    if 1 <= hour < 3:
        return "丑"
    if 3 <= hour < 5:
        return "寅"
    if 5 <= hour < 7:
        return "卯"
    if 7 <= hour < 9:
        return "辰"
    if 9 <= hour < 11:
        return "巳"
    if 11 <= hour < 13:
        return "午"
    if 13 <= hour < 15:
        return "未"
    if 15 <= hour < 17:
        return "申"
    if 17 <= hour < 19:
        return "酉"
    if 19 <= hour < 21:
        return "戌"
    return "亥"


def hour_pillar(dt: datetime, use_late_zi_next_day: bool = False) -> str:
    effective_dt = effective_day_datetime(dt, use_late_zi_next_day)
    day_stem = day_pillar(effective_dt)[0]
    branch = hour_branch(dt)
    start_stem = HOUR_STEM_START_BY_DAY_STEM[day_stem]
    stem = HEAVENLY_STEMS[(stem_index(start_stem) + branch_index(branch)) % 10]
    return stem + branch
