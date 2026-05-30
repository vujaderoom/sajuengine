from __future__ import annotations

from datetime import datetime

from app.core.calendar.day_pillar import day_pillar
from app.core.calendar.display_labels import localize_chart_tables
from app.core.calendar.hidden_stems import hidden_stems_for_chart
from app.core.calendar.month_pillar import month_pillar
from app.core.calendar.precise_solar_terms import precise_mode_summary
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
    precise_summary = precise_mode_summary(dt.year, birth.timezone)
    payload = {
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
            "calendar_engine_version": "v1.2.0",
            "solar_year_for_pillar": solar_year_for_pillar(dt),
            "month_boundary": month_boundary.name,
            "month_boundary_ko": month_boundary.ko,
            "month_branch": month_boundary.branch,
            "month_order": month_boundary.month_order,
            "late_zi_next_day": False,
            "solar_term_mode": precise_summary["mode"],
            "precise_solar_terms": precise_summary,
            "solar_terms": precise_summary["terms"] or solar_terms_for_year(dt.year),
        },
        "engine_notes": [
            "calendar engine v1.2.0",
            "년주는 입춘 기준",
            "월주는 12절입 기준 fixed Korean civil baseline, precise hook 준비",
            "일주는 1991-05-29 己亥 anchor 기반 60갑자 계산",
            "시주는 일간 기준 시천간 계산",
            "십성은 일간 기준 천간 십성",
            "지장간은 사용자 기준 여기/중기/정기 순서로 표시",
            "십이운성은 일간 기준 지지별 계산",
            "십이신살은 year_base/day_base/month_base를 함께 산출하되 기본 해석은 year_base 우선",
            "Skyfield 의존성은 추가했으며 ephemeris 구현은 precise_solar_terms hook으로 분리",
        ],
    }
    payload["display_ko"] = localize_chart_tables(payload)
    return payload
