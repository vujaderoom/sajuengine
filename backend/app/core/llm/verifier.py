from __future__ import annotations

from typing import Any

FORBIDDEN_EXTREME_TERMS = ["무조건", "반드시", "평생", "망한다", "죽는다", "파산한다", "이혼한다"]
SENSITIVE_EVENT_TERMS = ["사망", "이혼", "파산", "암", "중병", "사고사"]


def _flatten_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for child in value.values():
            out.extend(_flatten_values(child))
        return out
    if isinstance(value, list):
        out: list[str] = []
        for child in value:
            out.extend(_flatten_values(child))
        return out
    return []


def _engine_allowed_terms(engine_result_json: dict[str, Any]) -> set[str]:
    terms = set()
    for text in _flatten_values(engine_result_json.get("disease_profile", {})):
        if text:
            terms.add(text)
    for text in _flatten_values(engine_result_json.get("medicine_profile", {})):
        if text:
            terms.add(text)
    for text in _flatten_values(engine_result_json.get("yongshin", {})):
        if text:
            terms.add(text)
    return terms


def verify_output(engine_result_json: dict[str, Any], report_text: str) -> dict[str, Any]:
    failed_reasons: list[str] = []
    warnings: list[str] = []
    allowed_terms = _engine_allowed_terms(engine_result_json)

    yongshin = str(engine_result_json.get("yongshin", {}).get("primary", ""))
    if yongshin and yongshin not in report_text:
        warnings.append("엔진이 확정한 용신이 리포트에 명확히 반영되지 않음")

    for term in FORBIDDEN_EXTREME_TERMS:
        if term in report_text:
            failed_reasons.append(f"근거 없는 극단 표현 가능성: {term}")

    for term in SENSITIVE_EVENT_TERMS:
        if term in report_text:
            confidence = float(engine_result_json.get("confidence", {}).get("score", 0) or 0)
            if confidence < 0.8:
                failed_reasons.append(f"고위험 사건 표현은 confidence 0.8 이상 근거가 필요: {term}")
            else:
                warnings.append(f"민감 사건 표현 수동 검토 필요: {term}")

    if "庚" in report_text and yongshin == "火" and "주용신" in report_text:
        failed_reasons.append("엔진 결과와 다르게 庚金을 주용신으로 표현했을 가능성")

    if not allowed_terms:
        warnings.append("엔진 허용 용어 집합이 비어 있음")

    return {
        "report_status": "failed" if failed_reasons else "passed",
        "passed": len(failed_reasons) == 0,
        "failed_reasons": failed_reasons,
        "warnings": warnings,
        "checked_terms": sorted(list(allowed_terms))[:50],
    }
