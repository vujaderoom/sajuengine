from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SolarTermBoundary:
    name: str
    branch: str
    month_order: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0


# v0.1 fixed Korean civil-date scaffold.
# 다음 단계에서 Skyfield 기반 실제 절기 시각으로 교체한다.
MONTH_BOUNDARIES = [
    SolarTermBoundary("立春", "寅", 1, 2, 4),
    SolarTermBoundary("驚蟄", "卯", 2, 3, 6),
    SolarTermBoundary("淸明", "辰", 3, 4, 5),
    SolarTermBoundary("立夏", "巳", 4, 5, 6),
    SolarTermBoundary("芒種", "午", 5, 6, 6),
    SolarTermBoundary("小暑", "未", 6, 7, 7),
    SolarTermBoundary("立秋", "申", 7, 8, 8),
    SolarTermBoundary("白露", "酉", 8, 9, 8),
    SolarTermBoundary("寒露", "戌", 9, 10, 8),
    SolarTermBoundary("立冬", "亥", 10, 11, 7),
    SolarTermBoundary("大雪", "子", 11, 12, 7),
    SolarTermBoundary("小寒", "丑", 12, 1, 6),
]


def boundary_datetime(year: int, boundary: SolarTermBoundary) -> datetime:
    boundary_year = year
    if boundary.branch == "丑":
        boundary_year = year + 1
    return datetime(boundary_year, boundary.month, boundary.day, boundary.hour, boundary.minute)


def ipchun_datetime(year: int) -> datetime:
    return datetime(year, 2, 4)


def solar_year_for_pillar(dt: datetime) -> int:
    if dt < ipchun_datetime(dt.year):
        return dt.year - 1
    return dt.year


def month_boundary_for_datetime(dt: datetime) -> SolarTermBoundary:
    solar_year = solar_year_for_pillar(dt)
    selected = MONTH_BOUNDARIES[0]
    for boundary in MONTH_BOUNDARIES:
        if dt >= boundary_datetime(solar_year, boundary):
            selected = boundary
    return selected
