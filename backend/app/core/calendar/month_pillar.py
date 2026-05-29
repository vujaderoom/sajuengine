from __future__ import annotations

from datetime import datetime

from app.core.calendar.ganzhi import EARTHLY_BRANCHES, HEAVENLY_STEMS, branch_index, stem_index
from app.core.calendar.solar_terms import month_boundary_for_datetime

MONTH_STEM_START_BY_YEAR_STEM = {
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


def month_pillar(dt: datetime, year_stem: str) -> str:
    boundary = month_boundary_for_datetime(dt)
    month_branch = boundary.branch
    start_stem = MONTH_STEM_START_BY_YEAR_STEM[year_stem]
    offset = (branch_index(month_branch) - branch_index("寅")) % 12
    stem = HEAVENLY_STEMS[(stem_index(start_stem) + offset) % 10]
    return stem + month_branch
