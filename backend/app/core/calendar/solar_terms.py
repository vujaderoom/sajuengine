from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SolarTermBoundary:
    name: str
    ko: str
    branch: str
    month_order: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0


MONTH_BOUNDARIES = [
    SolarTermBoundary("立春", "입춘", "寅", 1, 2, 4),
    SolarTermBoundary("驚蟄", "경칩", "卯", 2, 3, 6),
    SolarTermBoundary("淸明", "청명", "辰", 3, 4, 5),
    SolarTermBoundary("立夏", "입하", "巳", 4, 5, 6),
    SolarTermBoundary("芒種", "망종", "午", 5, 6, 6),
    SolarTermBoundary("小暑", "소서", "未", 6, 7, 7),
    SolarTermBoundary("立秋", "입추", "申", 7, 8, 8),
    SolarTermBoundary("白露", "백로", "酉", 8, 9, 8),
    SolarTermBoundary("寒露", "한로", "戌", 9, 10, 8),
    SolarTermBoundary("立冬", "입동", "亥", 10, 11, 7),
    SolarTermBoundary("大雪", "대설", "子", 11, 12, 7),
    SolarTermBoundary("小寒", "소한", "丑", 12, 1, 6),
]

ALL_24_SOLAR_TERMS = [
    ("小寒", "소한", 1, 6), ("大寒", "대한", 1, 20),
    ("立春", "입춘", 2, 4), ("雨水", "우수", 2, 19),
    ("驚蟄", "경칩", 3, 6), ("春分", "춘분", 3, 21),
    ("淸明", "청명", 4, 5), ("穀雨", "곡우", 4, 20),
    ("立夏", "입하", 5, 6), ("小滿", "소만", 5, 21),
    ("芒種", "망종", 6, 6), ("夏至", "하지", 6, 21),
    ("小暑", "소서", 7, 7), ("大暑", "대서", 7, 23),
    ("立秋", "입추", 8, 8), ("處暑", "처서", 8, 23),
    ("白露", "백로", 9, 8), ("秋分", "추분", 9, 23),
    ("寒露", "한로", 10, 8), ("霜降", "상강", 10, 23),
    ("立冬", "입동", 11, 7), ("小雪", "소설", 11, 22),
    ("大雪", "대설", 12, 7), ("冬至", "동지", 12, 22),
]


def _boundaries_for_year(year: int) -> list[SolarTermBoundary]:
    try:
        from app.core.calendar.solar_term_table import month_boundaries_lookup
        return month_boundaries_lookup(year)
    except Exception:
        return MONTH_BOUNDARIES


def boundary_datetime(year: int, boundary: SolarTermBoundary) -> datetime:
    boundary_year = year + 1 if boundary.branch == "丑" else year
    return datetime(boundary_year, boundary.month, boundary.day, boundary.hour, boundary.minute)


def ipchun_datetime(year: int) -> datetime:
    boundaries = _boundaries_for_year(year)
    ipchun = next((item for item in boundaries if item.name == "立春"), MONTH_BOUNDARIES[0])
    return datetime(year, ipchun.month, ipchun.day, ipchun.hour, ipchun.minute)


def solar_year_for_pillar(dt: datetime) -> int:
    return dt.year - 1 if dt < ipchun_datetime(dt.year) else dt.year


def month_boundary_for_datetime(dt: datetime) -> SolarTermBoundary:
    solar_year = solar_year_for_pillar(dt)
    selected = _boundaries_for_year(solar_year)[0]
    for boundary in _boundaries_for_year(solar_year):
        if dt >= boundary_datetime(solar_year, boundary):
            selected = boundary
    return selected


def next_month_boundary_after(dt: datetime) -> datetime:
    solar_year = solar_year_for_pillar(dt)
    candidates: list[datetime] = []
    for year in [solar_year - 1, solar_year, solar_year + 1]:
        for boundary in _boundaries_for_year(year):
            bdt = boundary_datetime(year, boundary)
            if bdt > dt:
                candidates.append(bdt)
    return min(candidates)


def previous_month_boundary_before(dt: datetime) -> datetime:
    solar_year = solar_year_for_pillar(dt)
    candidates: list[datetime] = []
    for year in [solar_year - 1, solar_year, solar_year + 1]:
        for boundary in _boundaries_for_year(year):
            bdt = boundary_datetime(year, boundary)
            if bdt < dt:
                candidates.append(bdt)
    return max(candidates)


def solar_terms_for_year(year: int) -> list[dict]:
    try:
        from app.core.calendar.solar_term_table import solar_terms_lookup
        return solar_terms_lookup(year).terms
    except Exception:
        return [{"name": name, "ko": ko, "datetime": datetime(year, month, day).isoformat()} for name, ko, month, day in ALL_24_SOLAR_TERMS]


def solar_term_mode_for_year(year: int) -> str:
    try:
        from app.core.calendar.solar_term_table import solar_terms_lookup
        return solar_terms_lookup(year).mode
    except Exception:
        return "fixed_korean_civil_baseline"
