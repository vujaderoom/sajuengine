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


# Calendar Engine v1.0 baseline.
# 실제 만세력 앱과의 완전 일치를 위해 다음 단계에서 Skyfield 기반 절기 시각 테이블로 교체한다.
# 이 테이블은 12절입의 한국 민간력 평균일 baseline이며, 월주 경계 구조 검증용이다.
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


def boundary_datetime(year: int, boundary: SolarTermBoundary) -> datetime:
    boundary_year = year + 1 if boundary.branch == "丑" else year
    return datetime(boundary_year, boundary.month, boundary.day, boundary.hour, boundary.minute)


def ipchun_datetime(year: int) -> datetime:
    return datetime(year, 2, 4)


def solar_year_for_pillar(dt: datetime) -> int:
    return dt.year - 1 if dt < ipchun_datetime(dt.year) else dt.year


def month_boundary_for_datetime(dt: datetime) -> SolarTermBoundary:
    solar_year = solar_year_for_pillar(dt)
    selected = MONTH_BOUNDARIES[0]
    for boundary in MONTH_BOUNDARIES:
        if dt >= boundary_datetime(solar_year, boundary):
            selected = boundary
    return selected


def solar_terms_for_year(year: int) -> list[dict]:
    return [
        {"name": name, "ko": ko, "datetime": datetime(year, month, day).isoformat()} 
        for name, ko, month, day in ALL_24_SOLAR_TERMS
    ]
