from __future__ import annotations

from app.core.fortune.overlay import analyze_fortune_overlays

ELEMENT_BY_STEM = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
ELEMENT_BY_BRANCH = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}
ELEMENT_KO = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}


def _elements_for_pillar(pillar: str) -> list[str]:
    return [ELEMENT_BY_STEM[pillar[0]], ELEMENT_BY_BRANCH[pillar[1]]]


def _score_pillar(pillar: str, facts: dict) -> dict:
    elements = _elements_for_pillar(pillar)
    needs_drying = facts.get("water", {}).get("needs_drying") or facts.get("moisture_profile", {}).get("needs_drying")
    waterlogged = facts.get("water", {}).get("is_waterlogged") or facts.get("moisture_profile", {}).get("state") == "waterlogged"
    score = 0
    effects: list[str] = []
    risks: list[str] = []

    for element in elements:
        if element == "火":
            score += 3 if needs_drying else 1
            effects.append("화 운: 말림·건조·증발 작용으로 용신 후보를 강화")
        elif element == "水":
            score -= 3 if waterlogged else -1
            risks.append("수 운: 수습 과다·침수 리스크를 키움")
        elif element == "金":
            score -= 1 if waterlogged else 1
            effects.append("금 운: 개통·절제 작용")
            if waterlogged:
                risks.append("금 운: 수원을 생해 물 공급을 늘릴 수 있음")
        elif element == "木":
            score -= 1 if waterlogged else 1
            effects.append("목 운: 토를 제어하고 방향성을 부여")
            if waterlogged:
                risks.append("목 운: 젖은 토를 더 흔들어 부담이 될 수 있음")
        elif element == "土":
            score += 0
            effects.append("토 운: 제방·저장·현실화 작용")
            if waterlogged:
                risks.append("토 운: 수습을 가두어 정체를 만들 수 있음")

    if score >= 3:
        grade = "supportive"
        grade_ko = "우호"
    elif score <= -3:
        grade = "risky"
        grade_ko = "주의"
    else:
        grade = "mixed"
        grade_ko = "혼합"
    return {"score": score, "grade": grade, "grade_ko": grade_ko, "elements": elements, "elements_ko": [ELEMENT_KO[e] for e in elements], "effects": effects, "risks": risks}


def analyze_fortune(chart_result: dict, facts: dict) -> dict:
    daewoon = chart_result.get("daewoon", {})
    sewoon = chart_result.get("sewoon", {})
    daewoon_items = []
    for cycle in daewoon.get("cycles", []):
        evaluation = _score_pillar(cycle["pillar"], facts)
        daewoon_items.append({**cycle, "evaluation": evaluation})

    sewoon_items = []
    for year in sewoon.get("years", []):
        evaluation = _score_pillar(year["pillar"], facts)
        sewoon_items.append({**year, "evaluation": evaluation})

    current_daewoon = next((item for item in daewoon_items if item.get("is_current")), None)
    current_sewoon = next((item for item in sewoon_items if item.get("is_current")), None)
    combined_score = (current_daewoon or {}).get("evaluation", {}).get("score", 0) + (current_sewoon or {}).get("evaluation", {}).get("score", 0)
    if combined_score >= 4:
        current_grade = "supportive"
        current_grade_ko = "현재 운은 용신 작용이 비교적 강함"
    elif combined_score <= -4:
        current_grade = "risky"
        current_grade_ko = "현재 운은 병을 자극할 수 있어 주의"
    else:
        current_grade = "mixed"
        current_grade_ko = "현재 운은 길흉이 섞인 혼합 흐름"

    overlay_result = analyze_fortune_overlays(chart_result, facts)

    return {
        "model_version": "fortune_analysis_v1.1.0",
        "current": {
            "combined_score": combined_score,
            "grade": current_grade,
            "grade_ko": current_grade_ko,
            "daewoon": current_daewoon,
            "sewoon": current_sewoon,
        },
        "overlay_result": overlay_result,
        "daewoon": daewoon_items,
        "sewoon": sewoon_items,
        "principles": [
            "수습 과다·침수형에서는 火 운을 말림·건조·증발 작용으로 우선 평가",
            "水 운은 침수 리스크를 키우는 방향으로 평가",
            "金 운은 개통성과 수원 공급성을 함께 평가",
            "木 운은 토 제어와 젖은 토 부담을 함께 평가",
            "土 운은 제방·저장과 정체를 함께 평가",
            "overlay_result는 원국+운이 새로 만드는 관계 자극을 별도 평가",
        ],
    }
