from __future__ import annotations

from datetime import date, datetime

from app.core.calendar.relations import analyze_relations
from app.core.calendar.year_pillar import year_pillar


def build_sewoon(birth_dt: datetime, chart: dict[str, str], start_year: int | None = None, span: int = 11) -> dict:
    today = date.today()
    if start_year is None:
        start_year = today.year - 5
    years = []
    for year in range(start_year, start_year + span):
        # 세운 간지는 절입 경계와 무관하게 해당 태양년의 대표값으로 7월 1일을 사용한다.
        # 실제 연초 세운 경계 판단은 입춘 시각 테이블이 들어오면 별도 API에서 분기 가능하다.
        pillar = year_pillar(datetime(year, 7, 1))
        overlay_chart = {**chart, "sewoon": pillar}
        years.append(
            {
                "year": year,
                "pillar": pillar,
                "stem": pillar[0],
                "branch": pillar[1],
                "is_current": year == today.year,
                "relations_with_origin": analyze_relations({
                    "year": chart["year"],
                    "month": chart["month"],
                    "day": chart["day"],
                    "hour": pillar,
                }),
            }
        )
    current = next((item for item in years if item["is_current"]), None)
    return {
        "range": {"start_year": start_year, "end_year": start_year + span - 1, "span": span},
        "current": current,
        "years": years,
        "notes": [
            "세운은 현재 연도 전후 기본 11년을 생성",
            "세운 간지는 해당 연도의 대표 날짜 7월 1일 기준",
            "입춘 전후 세운 전환은 추후 solar term table 기반으로 정밀화 가능",
            "relations_with_origin은 원국+세운 지지를 간단 overlay한 관계 후보",
        ],
    }
