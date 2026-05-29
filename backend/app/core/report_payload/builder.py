from __future__ import annotations

from app.core.rule_runner.service import execute_rule_runner
from app.schemas import RuleRunnerRequest


def _group_proposals(proposals: list[dict]) -> dict:
    return {
        "core_disease_candidates": [p for p in proposals if p.get("candidate_type") == "core_disease"],
        "medicine_candidates": [p for p in proposals if p.get("candidate_type") == "medicine"],
        "yongshin_candidates": [p for p in proposals if p.get("candidate_type") == "yongshin"],
    }


def build_report_payload(request: RuleRunnerRequest) -> dict:
    result = execute_rule_runner(request)
    facts = result["facts"]
    final_result = result["final_result"]
    proposal_summary = _group_proposals(result["proposals"])
    proposal_summary["counter_rules_applied"] = result["counter_rules_applied"]

    payload = {
        "chart": result["chart_result"]["chart"],
        "birth": result["birth"],
        "facts": facts,
        "climate_profile": {
            "raw": facts.get("raw", {}),
            "display": facts.get("display", {}),
            "season_profile": facts.get("season_profile", {}),
            "temperature_profile": facts.get("temperature_profile", {}),
            "moisture_profile": facts.get("moisture_profile", {}),
        },
        "binding_profile": facts.get("binding_profile", facts.get("binding", {})),
        "storage_profile": facts.get("storage_profile", facts.get("storage", {})),
        "flow_profile": facts.get("flow_profile", facts.get("flow", {})),
        "proposal_summary": proposal_summary,
        "disease_profile": {
            "core_disease": final_result.get("core_disease"),
            "core_disease_detail": final_result.get("core_disease_detail"),
            "derived_diseases": final_result.get("derived_diseases", []),
            "Depth": final_result.get("depth"),
        },
        "medicine_profile": final_result.get("medicine_detail", {"name": final_result.get("medicine")}),
        "yongshin": {
            "primary": final_result.get("yongshin"),
            "symbols": final_result.get("yongshin_symbols", []),
            "secondary": final_result.get("secondary_yongshin", []),
            "reason": final_result.get("selected_yongshin_reason"),
            "source_rule": final_result.get("selected_yongshin_source_rule"),
            "selected": final_result.get("selected_yongshin", {}),
            "candidates": final_result.get("yongshin_candidates", []),
            "gishin_candidates": final_result.get("gishin_candidates", []),
        },
        "confidence": final_result.get("confidence_detail", {"score": final_result.get("confidence")}),
        "delta_inputs": facts.get("delta_inputs", {}),
        "luck_delta": {
            "delta_1": 0,
            "delta_2": 0,
            "delta_3": 0,
            "auxiliary_delta": 0,
            "final_delta": 0,
        },
        "rag_evidence": [],
        "decision_trace_id": result["execution_id"],
        "decision_trace": result["decision_trace"],
        "rule_version": result["rule_version"],
        "renderer_guardrails": [
            "LLM은 core_disease, medicine, yongshin, depth를 새로 추론하거나 변경하지 않는다.",
            "RAG 근거는 판단을 덮어쓰지 않고 보조 근거로만 사용한다.",
            "신강·신약, 십신, 12운성·신살만으로 핵심 병·용신을 확정하지 않는다.",
            "엔진 JSON에 없는 극단적 사건 표현을 생성하지 않는다.",
        ],
        "final_interpretation": "",
    }

    return {"engine_result": result, "report_payload": payload}
