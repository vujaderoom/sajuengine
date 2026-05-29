from __future__ import annotations

from datetime import datetime
from typing import Any

import yaml
from pydantic import BaseModel, Field

from app.core.calendar.service import calculate_chart
from app.core.rule_dsl.loader import load_rules
from app.core.rule_runner.service import execute_rule_runner
from app.schemas import BirthInput, RuleRunnerRequest


class CaseAuthoringRequest(BaseModel):
    case_id: str = "GC-DRAFT-001"
    title: str = "새 해석 케이스 초안"
    status: str = "draft"
    version: str = "1.0.0"
    birth: BirthInput = Field(default_factory=BirthInput)
    image_logic_text: str = ""
    disease_core: str = ""
    disease_subtype: str = ""
    disease_reason: str = ""
    medicine_type: str = ""
    medicine_action: str = ""
    medicine_reason: str = ""
    yongshin_primary: str = ""
    yongshin_symbols: list[str] = Field(default_factory=list)
    excluded_candidates: list[dict[str, str]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


def _split_logic(text: str) -> list[str]:
    return [line.strip(" -\t") for line in text.splitlines() if line.strip(" -\t")]


def _recommend_linked_rules(engine_result: dict[str, Any], requested_primary: str) -> list[str]:
    proposal_rules = [p.get("source_rule") for p in engine_result.get("proposals", []) if p.get("source_rule")]
    rules = load_rules(engine_result.get("rule_version", "v1.0.0"))
    recommended = list(dict.fromkeys(proposal_rules))
    for rule in rules:
        text = yaml.safe_dump(rule, allow_unicode=True, sort_keys=False)
        if requested_primary and requested_primary in text and rule.get("id") not in recommended:
            recommended.append(rule.get("id"))
    return recommended


def _rule_improvement_candidates(engine_result: dict[str, Any], request: CaseAuthoringRequest) -> list[dict[str, Any]]:
    final = engine_result.get("final_result", {})
    candidates: list[dict[str, Any]] = []
    if request.yongshin_primary and final.get("yongshin") != request.yongshin_primary:
        candidates.append(
            {
                "type": "yongshin_mismatch",
                "expected": request.yongshin_primary,
                "actual": final.get("yongshin"),
                "suggestion": "새 yongshin proposal rule 또는 counter rule 보강 필요",
            }
        )
    if request.medicine_action and request.medicine_action not in str(final.get("medicine")):
        candidates.append(
            {
                "type": "medicine_mismatch",
                "expected_action": request.medicine_action,
                "actual": final.get("medicine"),
                "suggestion": "medicine proposal 또는 finalizer mapping 보강 필요",
            }
        )
    if not candidates:
        candidates.append(
            {
                "type": "no_major_gap",
                "suggestion": "현재 룰로 초안 케이스의 핵심 기대값을 대체로 설명 가능",
            }
        )
    return candidates


def generate_case_preview(request: CaseAuthoringRequest) -> dict[str, Any]:
    chart_payload = calculate_chart(request.birth)
    engine_result = execute_rule_runner(RuleRunnerRequest(rule_version="v1.0.0", birth=request.birth))
    chart = chart_payload["chart"]
    linked_rules = _recommend_linked_rules(engine_result, request.yongshin_primary)

    image_logic = _split_logic(request.image_logic_text)
    yongshin_symbols = request.yongshin_symbols or engine_result.get("final_result", {}).get("yongshin_symbols", [])
    yongshin_primary = request.yongshin_primary or engine_result.get("final_result", {}).get("yongshin", "")
    medicine_action = request.medicine_action or engine_result.get("final_result", {}).get("medicine", "")

    case_yaml = {
        "id": request.case_id,
        "title": request.title,
        "status": request.status,
        "version": request.version,
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "birth": request.birth.model_dump(),
        "interpretation": {
            "image_logic": image_logic,
            "disease_logic": {
                "core": request.disease_core,
                "subtype": request.disease_subtype,
                "reason": request.disease_reason,
            },
            "medicine_logic": {
                "type": request.medicine_type,
                "action": medicine_action,
                "reason": request.medicine_reason,
            },
            "yongshin_logic": {
                "primary": yongshin_primary,
                "symbols": yongshin_symbols,
                "excluded": request.excluded_candidates,
            },
            "linked_rules": linked_rules,
        },
        "expected": {
            "chart": chart,
            "final_result": {
                "yongshin": yongshin_primary,
                "yongshin_symbols": yongshin_symbols,
                "medicine": medicine_action,
                "selected_yongshin_source_rule": engine_result.get("final_result", {}).get("selected_yongshin_source_rule"),
            },
        },
        "notes": request.notes or image_logic[:2],
    }

    raw_yaml = yaml.safe_dump(case_yaml, allow_unicode=True, sort_keys=False)
    return {
        "case_id": request.case_id,
        "chart_result": chart_payload,
        "engine_result": engine_result,
        "linked_rules": linked_rules,
        "rule_improvement_candidates": _rule_improvement_candidates(engine_result, request),
        "case_yaml": case_yaml,
        "raw_yaml": raw_yaml,
        "save_instruction": f"저장 시 golden_cases/{request.case_id}.yaml 파일로 추가",
    }
