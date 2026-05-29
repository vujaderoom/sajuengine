from __future__ import annotations

from app.core.schemas.engine import (
    Confidence,
    CoreDisease,
    DerivedDisease,
    FinalEngineResult,
    GishinCandidate,
    Medicine,
    SelectedYongshin,
    YongshinCandidate,
)


def best_proposal(proposals: list[dict], candidate_type: str) -> dict | None:
    filtered = [p for p in proposals if p.get("candidate_type") == candidate_type]
    if not filtered:
        return None
    return sorted(
        filtered,
        key=lambda p: (p.get("score_delta", 0.0), p.get("rule_priority", 0)),
        reverse=True,
    )[0]


def _confidence_level(score: float) -> str:
    if score >= 0.8:
        return "강한 판정"
    if score >= 0.6:
        return "경향성 판정"
    if score >= 0.4:
        return "가능성 판정"
    return "판단 보류"


def finalize(proposals: list[dict], facts: dict) -> FinalEngineResult:
    core_p = best_proposal(proposals, "core_disease")
    medicine_p = best_proposal(proposals, "medicine")
    yongshin_p = best_proposal(proposals, "yongshin")

    yongshin_candidates = [
        YongshinCandidate(
            value=p.get("value", "미정"),
            symbols=p.get("symbols", []),
            score=p.get("score_delta", 0.0),
            source_rule=p.get("source_rule"),
            reason=p.get("reason", ""),
            action=p.get("action"),
        )
        for p in proposals
        if p.get("candidate_type") == "yongshin"
    ]

    waterlogged = bool(facts.get("water", {}).get("is_waterlogged"))
    selected_primary = yongshin_p.get("value") if yongshin_p else "미정"
    selected_symbols = yongshin_p.get("symbols", []) if yongshin_p else []
    medicine_name = "말림·건조·증발" if selected_primary == "火" else (medicine_p.get("value") if medicine_p else "미정")
    medicine_action = "drying_evaporation" if selected_primary == "火" else (medicine_p.get("action") or "unknown" if medicine_p else "unknown")
    core_name = core_p.get("value") if core_p else "미정"
    core_type = "climate_waterlogged" if waterlogged else "flow_blocked"
    core_depth = int(facts.get("raw", {}).get("Depth", 2 if core_p else 1))

    confidence_score = 0.9 if selected_primary == "火" else (0.86 if core_p else 0.3)
    excluded = []
    if waterlogged:
        excluded.append(
            {
                "value": "庚金",
                "reason": "침수형에서는 절단·개통의 庚金보다 말림·건조·증발의 火가 주약이다.",
            }
        )

    return FinalEngineResult(
        core_disease=CoreDisease(
            type=core_type,
            name=core_name,
            depth=core_depth,
            reason=core_p.get("reason", "") if core_p else "핵심 병 후보가 충분하지 않음",
            source_rule=core_p.get("source_rule") if core_p else None,
        ),
        derived_diseases=[
            DerivedDisease(
                type="water_excess",
                name="수습 과다·침수형 병",
                reason="따뜻한 계절의 수원 지속으로 토지가 잠기는 파생 병",
            )
        ] if selected_primary == "火" else ([] if core_name == "미정" else [DerivedDisease(type="climate", name="기후형 병", reason="구조상 기후 불균형 신호")]),
        medicine=Medicine(
            type="기후 복원형" if selected_primary == "火" else (medicine_p.get("value") if medicine_p else "미정"),
            name=medicine_name,
            action=medicine_action,
            execution_grade="A" if selected_primary == "火" else "B",
            freedom="작동" if selected_primary != "미정" else "미정",
            reason=yongshin_p.get("reason", "") if yongshin_p else "",
        ),
        yongshin_candidates=yongshin_candidates,
        selected_yongshin=SelectedYongshin(
            primary=selected_primary,
            symbols=selected_symbols,
            secondary=selected_symbols,
            source_rule=yongshin_p.get("source_rule") if yongshin_p else None,
            reason=yongshin_p.get("reason", "") if yongshin_p else "",
            excluded=excluded,
        ),
        gishin_candidates=[
            GishinCandidate(value="水", reason="침수형에서는 추가 수원이 병을 깊게 할 수 있음", source="waterlogged_profile")
        ] if waterlogged else [],
        stability_grade="B" if core_p else "D",
        confidence=Confidence(score=confidence_score, level=_confidence_level(confidence_score)),
    )


def to_legacy_final_result(result: FinalEngineResult) -> dict:
    data = result.model_dump()
    return {
        "core_disease": result.core_disease.name,
        "core_disease_detail": data["core_disease"],
        "derived_diseases": [item.name for item in result.derived_diseases],
        "derived_disease_details": data["derived_diseases"],
        "medicine": result.medicine.name,
        "medicine_detail": data["medicine"],
        "yongshin": result.selected_yongshin.primary,
        "yongshin_symbols": result.selected_yongshin.symbols,
        "secondary_yongshin": result.selected_yongshin.secondary,
        "selected_yongshin": data["selected_yongshin"],
        "yongshin_candidates": data["yongshin_candidates"],
        "gishin_candidates": data["gishin_candidates"],
        "depth": result.core_disease.depth,
        "stability_grade": result.stability_grade,
        "confidence": result.confidence.score,
        "confidence_detail": data["confidence"],
        "selected_yongshin_source_rule": result.selected_yongshin.source_rule,
        "selected_yongshin_reason": result.selected_yongshin.reason,
    }
