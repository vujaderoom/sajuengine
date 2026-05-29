from __future__ import annotations

from datetime import datetime

from app.schemas import BirthInput

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

HOUR_BRANCHES = [
    (23, "子"),
    (1, "丑"),
    (3, "寅"),
    (5, "卯"),
    (7, "辰"),
    (9, "巳"),
    (11, "午"),
    (13, "未"),
    (15, "申"),
    (17, "酉"),
    (19, "戌"),
    (21, "亥"),
]

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


def ganzhi(index: int) -> str:
    return HEAVENLY_STEMS[index % 10] + EARTHLY_BRANCHES[index % 12]


def year_pillar(dt: datetime) -> str:
    # Scaffold: 입춘 전후 보정은 solar-term engine에서 교체한다.
    return ganzhi(dt.year - 1984)


def month_pillar(dt: datetime, year_stem: str) -> str:
    # Scaffold: 월지는 양력 월 기준 임시값이다. 다음 단계에서 절입 기준으로 교체한다.
    month_branch_by_solar_month = {
        1: "丑",
        2: "寅",
        3: "卯",
        4: "辰",
        5: "巳",
        6: "午",
        7: "未",
        8: "申",
        9: "酉",
        10: "戌",
        11: "亥",
        12: "子",
    }
    month_branch = month_branch_by_solar_month[dt.month]
    start_stem_by_year_stem = {
        "甲": "丙",
        "己": "丙",
        "乙": "戊",
        "庚": "戊",
        "丙": "庚",
        "辛": "庚",
        "丁": "壬",
        "壬": "壬",
        "戊": "甲",
        "癸": "甲",
    }
    start_stem = start_stem_by_year_stem[year_stem]
    offset = (EARTHLY_BRANCHES.index(month_branch) - EARTHLY_BRANCHES.index("寅")) % 12
    stem = HEAVENLY_STEMS[(HEAVENLY_STEMS.index(start_stem) + offset) % 10]
    return stem + month_branch


def day_pillar(dt: datetime) -> str:
    # Scaffold anchor: 1991-05-29 = 己亥. 다음 단계에서 정밀 일진으로 교체한다.
    anchor = datetime(1991, 5, 29)
    anchor_index = 35
    return ganzhi(anchor_index + (dt.date() - anchor.date()).days)


def hour_branch(hour: int) -> str:
    if hour == 23 or hour == 0:
        return "子"
    for start_hour, branch in reversed(HOUR_BRANCHES[1:]):
        if hour >= start_hour:
            return branch
    return "子"


def hour_pillar(dt: datetime, day_stem: str) -> str:
    branch = hour_branch(dt.hour)
    start_stem = HOUR_STEM_START_BY_DAY_STEM[day_stem]
    offset = EARTHLY_BRANCHES.index(branch)
    stem = HEAVENLY_STEMS[(HEAVENLY_STEMS.index(start_stem) + offset) % 10]
    return stem + branch


def calculate_chart(birth: BirthInput) -> dict:
    dt = datetime.fromisoformat(birth.birth_datetime)
    year = year_pillar(dt)
    month = month_pillar(dt, year[0])
    day = day_pillar(dt)
    hour = hour_pillar(dt, day[0])

    return {
        "birth": birth.model_dump(),
        "chart": {"year": year, "month": month, "day": day, "hour": hour},
        "engine_notes": [
            "calendar scaffold v0.3.0",
            "월주는 현재 양력 월 기준 scaffold이며 다음 단계에서 절입 기준으로 교체 예정",
            "일주는 1991-05-29 己亥 anchor 기반 scaffold",
        ],
    }
