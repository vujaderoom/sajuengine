from __future__ import annotations

from datetime import datetime

from app.core.calendar.day_pillar import day_pillar
from app.core.calendar.hidden_stems import hidden_stems_for_chart
from app.core.calendar.month_pillar import month_pillar
from app.core.calendar.solar_terms import month_boundary_for_datetime, solar_terms_for_year, solar_year_for_pillar
from app.core.calendar.ten_gods import ten_gods_for_chart
from app.core.calendar.time_pillar import hour_pillar
from app.core.calendar.twelve_shinsal import twelve_shinsal_multi_base_for_chart
from app.core.calendar.twelve_unseong import twelve_unseong_for_chart
from app.core.calendar.year_pillar import year_pillar
from app.schemas import BirthInput


def calculate_chart(birth: BirthInput) -> dict:
    dt = datetime.fromisoformat(birth.birth_datetime)
    year = year_pillar(dt)
    month = month_pillar(dt, year[0])
    day = day_pillar(dt)
    hour = hour_pillar(dt)
    chart = {"year": year, "month": month, "day": day, "hour": hour}
    month_boundary = month_boundary_for_datetime(dt)

    return {
        "birth": birth.model_dump(),
        "chart": chart,
        "pillars": {
            "year": {"stem": year[0], "branch": year[1]},
            "month": {"stem": month[0], "branch": month[1]},
            "day": {"stem": day[0], "branch": day[1]},
            "hour": {"stem": hour[0], "branch": hour[1]},
        },
        "ten_gods": ten_gods_for_chart(chart),
        "hidden_stems": hidden_stems_for_chart(chart),
        "twelve_unseong": twelve_unseong_for_chart(chart),
        "twelve_shinsal": twelve_shinsal_multi_base_for_chart(chart),
        "calendar_meta": {
            "calendar_engine_version": "v1.0.0",
            "solar_year_for_pillar": solar_year_for_pillar(dt),
            "month_boundary": month_boundary.name,
            "month_boundary_ko": month_boundary.ko,
            "month_branch": month_boundary.branch,
            "month_order": month_boundary.month_order,
            "late_zi_next_day": False,
            "solar_term_mode": "fixed_korean_civil_baseline",
            "solar_terms": solar_terms_for_year(dt.year),
        },
        "engine_notes": [
            "calendar engine v1.0.0",
            "년주는 입춘 기준",
            "월주는 12절입 기준 fixed Korean civil baseline",
            "일주는 1991-05-29 己亥 anchor 기반 60갑자 계산",
            "시주는 일간 기준 시천간 계산",
            "십성은 일간 기준 천간 십성",
            "십이운성은 일간 기준 지지별 계산",
            "십이신살은 year_base/day_base/month_base를 함께 산출하되 기본 해석은 year_base 우선",
            "절기 시각의 실제 분 단위 일치는 다음 단계에서 Skyfield/ephemeris 테이블로 교체 필요",
        ],
    }
