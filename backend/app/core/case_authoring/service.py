from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from app.core.calendar.service import calculate_chart
from app.core.regression.runner import run_case_by_id, run_regressions
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


class NaturalLogicRequest(BaseModel):
    case_id: str = "GC-DRAFT-001"
    title: str = "새 해석 케이스 초안"
    birth: BirthInput = Field(default_factory=BirthInput)
    natural_logic_text: str = ""


class CaseSaveRequest(BaseModel):
    authoring: CaseAuthoringRequest
    overwrite: bool = False
    run_regression_after_save: bool = True


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _golden_case_path(case_id: str) -> Path:
    safe_id = case_id.replace("/", "_").replace("..", "_")
    return _repo_root() / "golden_cases" / f"{safe_id}.yaml"


def _split_logic(text: str) -> list[str]:
    return [line.strip(" -\t") for line in text.splitlines() if line.strip(" -\t")]


def _has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def structure_natural_logic(request: NaturalLogicRequest) -> dict[str, Any]:
    text = request.natural_logic_text
    lines = _split_logic(text)

    disease_core = "기후형 병" if _has_any(text, ["습", "침수", "비", "물", "수기", "한랭", "조후"]) else "미정"
    disease_subtype = "수습 과다·침수형" if _has_any(text, ["침수", "물에 잠", "수습", "습이 과", "질척", "비가"] ) else "미정"
    medicine_type = "기후 복원형" if disease_core == "기후형 병" else "미정"

    if _has_any(text, ["말림", "건조", "증발", "말려", "말려야", "화로"]):
        medicine_action = "말림·건조·증발"
    elif _has_any(text, ["개통", "소통", "뚫", "절단"]):
        medicine_action = "유통 개통"
    else:
        medicine_action = ""

    if _has_any(text, ["火", "화", "병화", "정화", "사화", "오화", "丙", "丁", "巳", "午"]):
        yongshin_primary = "火"
        yongshin_symbols = ["巳火", "午火", "丙火", "丁火"]
    elif _has_any(text, ["庚", "경금", "금"]):
        yongshin_primary = "金"
        yongshin_symbols = ["庚金"]
    else:
        yongshin_primary = ""
        yongshin_symbols = []

    excluded_candidates = []
    if _has_any(text, ["경금", "庚"] ) and _has_any(text, ["아니", "보조", "조건부", "탈락"]):
        excluded_candidates.append({"value": "庚金", "reason": "입력 논리상 주용신이 아니라 조건부 보조 후보로 설명됨"})

    authoring = CaseAuthoringRequest(
        case_id=request.case_id,
        title=request.title,
        birth=request.birth,
        image_logic_text="\n".join(lines),
        disease_core=disease_core,
        disease_subtype=disease_subtype,
        disease_reason="자연어 물상 논리에서 추출된 병 구조 후보입니다.",
        medicine_type=medicine_type,
        medicine_action=medicine_action,
        medicine_reason="자연어 물상 논리에서 추출된 약 작용 후보입니다.",
        yongshin_primary=yongshin_primary,
        yongshin_symbols=yongshin_symbols,
        excluded_candidates=excluded_candidates,
        notes=["자연어 구조화 초안: 저장 전 해석자 검토 필요"],
    )
    preview = generate_case_preview(authoring)
    return {
        "structured_authoring": authoring.model_dump(),
        "confidence": "scaffold",
        "extraction_notes": ["현재는 규칙 기반 구조화 scaffold입니다.", "외부 LLM 또는 내부 LLM을 붙이면 이 함수만 교체할 수 있습니다.", "저장 전 disease/yongshin/medicine 필드는 반드시 검토하세요."],
        "preview": preview,
    }


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
        candidates.append({"type": "yongshin_mismatch", "expected": request.yongshin_primary, "actual": final.get("yongshin"), "suggestion": "새 yongshin proposal rule 또는 counter rule 보강 필요"})
    if request.medicine_action and request.medicine_action not in str(final.get("medicine")):
        candidates.append({"type": "medicine_mismatch", "expected_action": request.medicine_action, "actual": final.get("medicine"), "suggestion": "medicine proposal 또는 finalizer mapping 보강 필요"})
    if not candidates:
        candidates.append({"type": "no_major_gap", "suggestion": "현재 룰로 초안 케이스의 핵심 기대값을 대체로 설명 가능"})
    return candidates


def _rule_candidate_from_case(request: CaseAuthoringRequest, chart: dict[str, str], engine_result: dict[str, Any]) -> dict[str, Any]:
    safe_case_id = request.case_id.lower().replace("_", "-")
    disease_subtype = request.disease_subtype or "미정"
    medicine_action = request.medicine_action or engine_result.get("final_result", {}).get("medicine", "")
    yongshin_primary = request.yongshin_primary or engine_result.get("final_result", {}).get("yongshin", "")
    symbols = request.yongshin_symbols or engine_result.get("final_result", {}).get("yongshin_symbols", [])
    conditions = []
    if chart.get("day", "")[0]:
        conditions.append({"path": "chart.day", "op": "contains", "value": chart["day"][0]})
    if chart.get("month", "")[1]:
        conditions.append({"path": "chart.month", "op": "contains", "value": chart["month"][1]})
    if disease_subtype != "미정":
        conditions.append({"path": "fact.disease_profile.disease_image", "op": "contains", "value": disease_subtype.split("·")[0]})

    candidate = {
        "id": f"case_rule_candidate_{safe_case_id}",
        "title": f"{request.title} 기반 룰 후보",
        "status": "candidate_review_required",
        "layer": "YONGSHIN_PROPOSAL",
        "target": "selected_yongshin",
        "priority": 50,
        "enabled": False,
        "source_case_id": request.case_id,
        "when": {"all": conditions or [{"path": "chart.day", "op": "exists"}]},
        "then": {
            "propose": {
                "proposal_id": f"prop_{safe_case_id}_yongshin",
                "candidate_type": "yongshin",
                "value": yongshin_primary,
                "symbols": symbols,
                "action": medicine_action,
                "score_delta": 1.0,
                "confidence_signal": "case_candidate",
                "reason": "케이스 물상 논리에서 자동 생성된 룰 후보입니다. 승인 전 조건을 반드시 검토하세요.",
            }
        },
        "evidence_query": {"case_id": request.case_id, "tags": ["case-derived", disease_subtype, yongshin_primary]},
    }
    return candidate


def generate_case_preview(request: CaseAuthoringRequest) -> dict[str, Any]:
    chart_payload = calculate_chart(request.birth)
    engine_result = execute_rule_runner(RuleRunnerRequest(rule_version="v1.0.0", birth=request.birth))
    chart = chart_payload["chart"]
    linked_rules = _recommend_linked_rules(engine_result, request.yongshin_primary)

    image_logic = _split_logic(request.image_logic_text)
    yongshin_symbols = request.yongshin_symbols or engine_result.get("final_result", {}).get("yongshin_symbols", [])
    yongshin_primary = request.yongshin_primary or engine_result.get("final_result", {}).get("yongshin", "")
    medicine_action = request.medicine_action or engine_result.get("final_result", {}).get("medicine", "")
    rule_candidate = _rule_candidate_from_case(request, chart, engine_result)

    case_yaml = {
        "id": request.case_id,
        "title": request.title,
        "status": request.status,
        "version": request.version,
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "birth": request.birth.model_dump(),
        "interpretation": {
            "image_logic": image_logic,
            "disease_logic": {"core": request.disease_core, "subtype": request.disease_subtype, "reason": request.disease_reason},
            "medicine_logic": {"type": request.medicine_type, "action": medicine_action, "reason": request.medicine_reason},
            "yongshin_logic": {"primary": yongshin_primary, "symbols": yongshin_symbols, "excluded": request.excluded_candidates},
            "linked_rules": linked_rules,
        },
        "expected": {"chart": chart, "final_result": {"yongshin": yongshin_primary, "yongshin_symbols": yongshin_symbols, "medicine": medicine_action, "selected_yongshin_source_rule": engine_result.get("final_result", {}).get("selected_yongshin_source_rule")}},
        "rule_candidate": rule_candidate,
        "notes": request.notes or image_logic[:2],
    }

    raw_yaml = yaml.safe_dump(case_yaml, allow_unicode=True, sort_keys=False)
    rule_candidate_yaml = yaml.safe_dump(rule_candidate, allow_unicode=True, sort_keys=False)
    return {
        "case_id": request.case_id,
        "chart_result": chart_payload,
        "engine_result": engine_result,
        "linked_rules": linked_rules,
        "rule_improvement_candidates": _rule_improvement_candidates(engine_result, request),
        "rule_candidate": rule_candidate,
        "rule_candidate_yaml": rule_candidate_yaml,
        "case_yaml": case_yaml,
        "raw_yaml": raw_yaml,
        "save_instruction": f"저장 시 golden_cases/{request.case_id}.yaml 파일로 추가",
    }


def save_case(request: CaseSaveRequest) -> dict[str, Any]:
    preview = generate_case_preview(request.authoring)
    path = _golden_case_path(request.authoring.case_id)
    if path.exists() and not request.overwrite:
        return {"saved": False, "reason": "case_already_exists", "path": str(path.relative_to(_repo_root())), "preview": preview}

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(preview["raw_yaml"], encoding="utf-8")

    single_case_result = run_case_by_id(request.authoring.case_id)
    regression_result = run_regressions() if request.run_regression_after_save else None
    return {"saved": True, "path": str(path.relative_to(_repo_root())), "case_id": request.authoring.case_id, "single_case_result": single_case_result, "regression_result": regression_result, "preview": preview}
