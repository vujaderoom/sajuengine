from __future__ import annotations

from datetime import datetime

from app.core.calendar.day_pillar import day_pillar
from app.core.calendar.month_pillar import month_pillar
from app.core.calendar.solar_terms import month_boundary_for_datetime, solar_year_for_pillar
from app.core.calendar.time_pillar import hour_pillar
from app.core.calendar.year_pillar import year_pillar
from app.schemas import BirthInput


def calculate_chart(birth: BirthInput) -> dict:
    dt = datetime.fromisoformat(birth.birth_datetime)
    year = year_pillar(dt)
    month = month_pillar(dt, year[0])
    day = day_pillar(dt)
    hour = hour_pillar(dt)
    month_boundary = month_boundary_for_datetime(dt)

    return {
        "birth": birth.model_dump(),
        "chart": {"year": year, "month": month, "day": day, "hour": hour},
        "calendar_meta": {
            "calendar_engine_version": "v0.1.0",
            "solar_year_for_pillar": solar_year_for_pillar(dt),
            "month_boundary": month_boundary.name,
            "month_branch": month_boundary.branch,
            "month_order": month_boundary.month_order,
            "late_zi_next_day": False,
        },
        "engine_notes": [
            "calendar engine v0.1.0",
            "년주는 입춘 기준 scaffold로 계산",
            "월주는 고정 절입일 테이블 기반 scaffold로 계산",
            "일주는 1991-05-29 己亥 anchor 기반 60갑자 계산",
            "시주는 일간 기준 시천간 계산, 야자시 옵션 hook 준비",
            "절기 시각은 다음 단계에서 Skyfield 기반으로 교체 예정",
        ],
    }
