from __future__ import annotations

from datetime import datetime

from app.core.calendar.ganzhi import ganzhi, ganzhi_index

ANCHOR_DATE = datetime(1991, 5, 29).date()
ANCHOR_PILLAR = "己亥"
ANCHOR_INDEX = ganzhi_index(ANCHOR_PILLAR)


def day_pillar(dt: datetime) -> str:
    delta_days = (dt.date() - ANCHOR_DATE).days
    return ganzhi(ANCHOR_INDEX + delta_days)
