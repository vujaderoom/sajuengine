from __future__ import annotations

from datetime import date, datetime

from app.core.calendar.ganzhi import JIAZI, ganzhi_index
from app.core.calendar.solar_terms import next_month_boundary_after, previous_month_boundary_before

YANG_STEMS = {"甲", "丙", "戊", "庚", "壬"}
YIN_STEMS = {"乙", "丁", "己", "辛", "癸"}


def daewoon_direction(sex: str, year_stem: str) -> dict:
    is_yang_year = year_stem in YANG_STEMS
    normalized_sex = (sex or "unknown").lower()
    forward = (normalized_sex == "male" and is_yang_year) or (normalized_sex == "female" and not is_yang_year)
    if normalized_sex not in ["male", "female"]:
        forward = True
    return {
        "direction": "forward" if forward else "backward",
        "direction_ko": "순행" if forward else "역행",
        "year_stem_yinyang": "yang" if is_yang_year else "yin",
        "year_stem_yinyang_ko": "양" if is_yang_year else "음",
        "rule": "남양여음 순행, 남음여양 역행",
    }


def _age_from_days(days: float) -> dict:
    # 전통 대운: 3일 = 1년, 1일 = 4개월, 1시간 ≒ 5일로 환산되는 구조.
    years_float = days / 3.0
    full_years = int(years_float)
    months = round((years_float - full_years) * 12)
    if months == 12:
        full_years += 1
        months = 0
    return {
        "days_to_boundary": round(days, 6),
        "start_age_years": full_years,
        "start_age_months": months,
        "start_age_decimal": round(years_float, 3),
        "method": "3일=1년, 1일=4개월",
    }


def _add_age_to_birth(birth_dt: datetime, years: int, months: int) -> str:
    year = birth_dt.year + years
    month = birth_dt.month + months
    while month > 12:
        year += 1
        month -= 12
    day = min(birth_dt.day, 28)
    return date(year, month, day).isoformat()


def build_daewoon(birth_dt: datetime, sex: str, chart: dict[str, str], count: int = 10) -> dict:
    year_stem = chart["year"][0]
    month_pillar = chart["month"]
    direction_info = daewoon_direction(sex, year_stem)
    forward = direction_info["direction"] == "forward"
    target_boundary = next_month_boundary_after(birth_dt) if forward else previous_month_boundary_before(birth_dt)
    delta_days = abs((target_boundary - birth_dt).total_seconds()) / 86400
    start_age = _age_from_days(delta_days)
    start_date = _add_age_to_birth(birth_dt, start_age["start_age_years"], start_age["start_age_months"])

    month_idx = ganzhi_index(month_pillar)
    direction_delta = 1 if forward else -1
    cycles = []
    today = date.today()
    current = None
    for i in range(count):
        pillar = JIAZI[(month_idx + direction_delta * (i + 1)) % 60]
        age_start = start_age["start_age_decimal"] + i * 10
        age_end = age_start + 9.999
        year_start = birth_dt.year + int(age_start)
        year_end = birth_dt.year + int(age_start + 10) - 1
        item = {
            "index": i + 1,
            "pillar": pillar,
            "stem": pillar[0],
            "branch": pillar[1],
            "age_start": round(age_start, 3),
            "age_end": round(age_end, 3),
            "year_start": year_start,
            "year_end": year_end,
            "is_current": year_start <= today.year <= year_end,
        }
        if item["is_current"]:
            current = item
        cycles.append(item)

    return {
        "direction": direction_info,
        "start": {
            **start_age,
            "birth_datetime": birth_dt.isoformat(),
            "target_boundary_datetime": target_boundary.isoformat(),
            "estimated_start_date": start_date,
            "precision": "solar_term_table_or_fixed_baseline",
        },
        "base_month_pillar": month_pillar,
        "cycles": cycles,
        "current": current,
        "notes": [
            "대운 방향은 연간 음양과 성별 기준",
            "첫 대운은 월주에서 순/역행으로 1칸 이동",
            "대운 시작 나이는 절기 경계까지의 거리 기준 3일=1년 방식",
            "절기 시각 테이블이 추가되면 target_boundary_datetime과 시작 나이가 더 정밀해짐",
        ],
    }
