from __future__ import annotations

from typing import Any


def render_report(engine_result_json: dict[str, Any], user_question: str = "") -> dict[str, Any]:
    chart = engine_result_json.get("chart", {})
    disease = engine_result_json.get("disease_profile", {})
    medicine = engine_result_json.get("medicine_profile", {})
    yongshin = engine_result_json.get("yongshin", {})
    confidence = engine_result_json.get("confidence", {})
    climate = engine_result_json.get("climate_profile", {})

    pillars = " ".join(str(chart.get(key, "")) for key in ["year", "month", "day", "hour"]).strip()
    primary_yongshin = yongshin.get("primary", "미정")
    symbols = ", ".join(yongshin.get("symbols", []) or [])
    confidence_level = confidence.get("level", "")

    sections = [
        "1. 핵심 요약",
        f"이 원국({pillars})은 엔진 기준으로 핵심 병이 '{disease.get('core_disease', '미정')}'로 정리됩니다. 약은 '{medicine.get('name', '미정')}', 용신은 '{primary_yongshin}'입니다.",
        "",
        "2. 원국의 환경 구조",
        f"기후/수분 프로필은 다음 구조로 요약됩니다: {climate.get('temperature_profile', {})} / {climate.get('moisture_profile', {})}.",
        "",
        "3. 핵심 병과 기능 단절 지점",
        f"핵심 병 상세: {disease.get('core_disease_detail', disease)}",
        "",
        "4. 약과 용신의 작동 방식",
        f"약의 작동은 {medicine.get('action', '미정')}이며, 세부 후보는 {symbols or '미정'}입니다.",
        "",
        "5. 현실적 조언",
        "이 리포트 초안은 엔진 결과를 설명하는 렌더링이며, 병·약·용신을 새로 판단하지 않습니다.",
        "",
        "6. 근거 요약",
        f"decision_trace_id={engine_result_json.get('decision_trace_id')}, rule_version={engine_result_json.get('rule_version')}, confidence={confidence.get('score')} ({confidence_level})",
    ]
    if user_question:
        sections.extend(["", "7. 사용자 질문 반영", user_question])

    return {
        "report_text": "\n".join(sections),
        "renderer_input_json": engine_result_json,
    }
