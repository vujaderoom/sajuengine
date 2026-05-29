from __future__ import annotations

from datetime import datetime

from app.core.calendar.ganzhi import ganzhi
from app.core.calendar.solar_terms import solar_year_for_pillar


def year_pillar(dt: datetime) -> str:
    year = solar_year_for_pillar(dt)
    return ganzhi(year - 1984)
