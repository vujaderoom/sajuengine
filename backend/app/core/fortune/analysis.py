from __future__ import annotations

from app.core.fortune.overlay import analyze_fortune_overlays
from app.core.fortune.timeline import build_fortune_timeline
from app.core.luck_delta.service import build_luck_delta_analysis

ELEMENT_BY_STEM = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
ELEMENT_BY_BRANCH = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}
ELEMENT_KO = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}


def _elements_for_pillar(pillar: str) -> list[str]:
    return [ELEMENT_BY_STEM[pillar[0]], ELEMENT_BY_BRANCH[pillar[1]]]


def _score_pillar(pillar: str, facts: dict) -> dict:
    elements = _elements_for_pillar(pillar)
    delta_inputs = facts.get("DeltaInputs") or facts.get("delta_inputs", {})
    humidity = delta_inputs.get("climate", {}).get("humidity")
    temperature = delta_inputs.get("climate", {}).get("temperature")
    needs_drying = facts.get("water", {}).get("needs_drying") or facts.get("moisture_profile", {}).get("needs_drying") or humidity == "과습"
    waterlogged = facts.get("water", {}).get("is_waterlogged") or facts.get("moisture_profile", {}).get("state") == "waterlogged" or humidity == "과습"
    score = 0
    effects: list[str] = []
    risks: list[str] = []

    for element in elements:
        if element == "火":
            if needs_drying:
                score += 3
                effects.append("화 운: 말림·건조·증발 작용")
            elif temperature == "조열":
                score -= 2
                risks.append("화 운: 조열 강화 가능")
            else:
                score += 1
                effects.append("화 운: 발산 작용")
        elif element == "水":
            if waterlogged:
                score -= 3
                risks.append("수 운: 수습 과다 리스크")
            elif temperature == "조열":
                score += 2
                effects.append("수 운: 조열 완화")
            else:
                score -= 1
                risks.append("수 운: 습도 상승 가능")
        elif element == "金":
            score -= 1 if waterlogged else 1
            effects.append("금 운: 개통·절제 작용")
            if waterlogged:
                risks.append("금 운: 수원 공급 가능")
        elif element == "木":
            score -= 1 if waterlogged else 1
            effects.append("목 운: 방향성 부여")
            if waterlogged:
                risks.append("목 운: 젖은 토 흔들림")
        elif element == "土":
            effects.append("토 운: 제방·저장 작용")
            if waterlogged:
                risks.append("토 운: 수습 정체 가능")

    if score >= 3:
        grade, grade_ko = "supportive", "우호"
    elif score <= -3:
        grade, grade_ko = "risky", "주의"
    else:
        grade, grade_ko = "mixed", "혼합"
    return {"score": score, "grade": grade, "grade_ko": grade_ko, "elements": elements, "elements_ko": [ELEMENT_KO[e] for e in elements], "effects": effects, "risks": risks}


def analyze_fortune(chart_result: dict, facts: dict) -> dict:
    daewoon = chart_result.get("daewoon", {})
    sewoon = chart_result.get("sewoon", {})
    daewoon_items = [{**cycle, "evaluation": _score_pillar(cycle["pillar"], facts)} for cycle in daewoon.get("cycles", [])]
    sewoon_items = [{**year, "evaluation": _score_pillar(year["pillar"], facts)} for year in sewoon.get("years", [])]
    current_daewoon = next((item for item in daewoon_items if item.get("is_current")), None)
    current_sewoon = next((item for item in sewoon_items if item.get("is_current")), None)
    combined_score = (current_daewoon or {}).get("evaluation", {}).get("score", 0) + (current_sewoon or {}).get("evaluation", {}).get("score", 0)
    if combined_score >= 4:
        current_grade, current_grade_ko = "supportive", "현재 운은 용신 작용이 비교적 강함"
    elif combined_score <= -4:
        current_grade, current_grade_ko = "risky", "현재 운은 병을 자극할 수 있어 주의"
    else:
        current_grade, current_grade_ko = "mixed", "현재 운은 길흉이 섞인 혼합 흐름"

    overlay_result = analyze_fortune_overlays(chart_result, facts)
    timeline = build_fortune_timeline(overlay_result)
    delta_inputs = facts.get("DeltaInputs") or facts.get("delta_inputs", {})
    luck_delta = build_luck_delta_analysis(chart_result, delta_inputs, overlay_result) if delta_inputs else {"model_version": "luck_delta_unavailable"}

    return {
        "model_version": "fortune_analysis_v1.3.0",
        "current": {"combined_score": combined_score, "grade": current_grade, "grade_ko": current_grade_ko, "daewoon": current_daewoon, "sewoon": current_sewoon},
        "overlay_result": overlay_result,
        "timeline": timeline,
        "luck_delta": luck_delta,
        "daewoon": daewoon_items,
        "sewoon": sewoon_items,
        "principles": ["DeltaInputs의 climate 점수를 우선 참조", "overlay_result는 관계 자극 평가", "luck_delta는 Δ1/Δ2/Δ3(+보조가중) 구조"],
    }
