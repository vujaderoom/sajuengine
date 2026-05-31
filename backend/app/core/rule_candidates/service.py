from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from app.core.cases.loader import load_cases
from app.core.regression.runner import run_regressions
from app.core.rule_dsl.validator import validate_rule


class PublishCandidateRequest(BaseModel):
    version: str = "v1.0.0"
    enable: bool = False
    overwrite: bool = False
    run_regression_after_publish: bool = True


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _candidate_id_from_case(case: dict[str, Any], candidate: dict[str, Any]) -> str:
    return candidate.get("id") or f"case_rule_candidate_{case.get('id')}"


def _candidate_summary(case: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_id = _candidate_id_from_case(case, candidate)
    return {
        "id": candidate_id,
        "title": candidate.get("title") or f"{case.get('title')} 룰 후보",
        "status": candidate.get("status", "candidate_review_required"),
        "enabled": candidate.get("enabled", False),
        "source_case_id": candidate.get("source_case_id") or case.get("id"),
        "source_case_title": case.get("title"),
        "source_case_path": case.get("_path"),
        "layer": candidate.get("layer"),
        "target": candidate.get("target"),
        "priority": candidate.get("priority", 0),
        "propose": (candidate.get("then") or {}).get("propose", {}),
        "expected": (case.get("expected") or {}).get("final_result", {}),
    }


def list_rule_candidates() -> dict[str, Any]:
    candidates = []
    for case in load_cases():
        candidate = case.get("rule_candidate")
        if not isinstance(candidate, dict):
            continue
        candidates.append(_candidate_summary(case, candidate))
    return {"total": len(candidates), "candidates": sorted(candidates, key=lambda x: x.get("id", ""))}


def get_rule_candidate(candidate_id: str) -> dict[str, Any] | None:
    for case in load_cases():
        candidate = case.get("rule_candidate")
        if not isinstance(candidate, dict):
            continue
        if _candidate_id_from_case(case, candidate) == candidate_id:
            normalized = normalize_candidate_rule(candidate, source_case=case, enable=False)
            return {
                "candidate": _candidate_summary(case, candidate),
                "source_case": {
                    "id": case.get("id"),
                    "title": case.get("title"),
                    "path": case.get("_path"),
                    "interpretation": case.get("interpretation", {}),
                    "expected": case.get("expected", {}),
                },
                "raw_candidate": candidate,
                "raw_candidate_yaml": yaml.safe_dump(candidate, allow_unicode=True, sort_keys=False),
                "normalized_rule": normalized,
                "normalized_rule_yaml": yaml.safe_dump(normalized, allow_unicode=True, sort_keys=False),
                "validation": validate_rule(normalized),
            }
    return None


def normalize_candidate_rule(candidate: dict[str, Any], source_case: dict[str, Any], enable: bool = False) -> dict[str, Any]:
    propose = (candidate.get("then") or {}).get("propose", {})
    candidate_id = _candidate_id_from_case(source_case, candidate)
    tags = ["case-derived", source_case.get("id"), propose.get("value")]
    tags.extend((candidate.get("evidence_query") or {}).get("tags", []))
    tags = [str(tag) for tag in dict.fromkeys([tag for tag in tags if tag])]

    normalized = {
        "id": candidate_id,
        "title": candidate.get("title") or f"{source_case.get('title')} 기반 룰 후보",
        "version": "1.0.0",
        "status": "published_review" if enable else "review_candidate",
        "layer": "L2_PROPOSAL",
        "target": "yongshin_candidate" if propose.get("candidate_type") == "yongshin" else f"{propose.get('candidate_type', 'auxiliary')}_candidate",
        "priority": int(candidate.get("priority", 50)),
        "enabled": bool(enable),
        "source_case_id": candidate.get("source_case_id") or source_case.get("id"),
        "when": candidate.get("when") or {"all": [{"path": "chart.day", "op": "exists"}]},
        "then": {
            "propose": {
                "proposal_id": propose.get("proposal_id") or f"prop_{candidate_id}",
                "candidate_type": propose.get("candidate_type", "yongshin"),
                "value": propose.get("value", "미정"),
                "symbols": propose.get("symbols", []),
                "action": propose.get("action"),
                "score_delta": float(propose.get("score_delta", 1.0)),
                "confidence_signal": propose.get("confidence_signal", "case_candidate"),
                "reason": propose.get("reason") or "케이스 기반 후보 룰입니다. 운영 적용 전 검토가 필요합니다.",
            }
        },
        "score": {"base": float(propose.get("score_delta", 1.0)), "source": "case_candidate"},
        "counter_rules": candidate.get("counter_rules", []),
        "explain": {
            "summary": "케이스에서 생성된 후보 룰을 DSL 규격에 맞게 정규화했습니다.",
            "source_case_title": source_case.get("title"),
            "review_required": True,
        },
        "evidence_query": {"case_id": source_case.get("id"), "tags": tags},
        "tests": {"positive_cases": [source_case.get("id")], "negative_cases": []},
        "published_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    return normalized


def preview_candidate_impact(candidate_id: str) -> dict[str, Any] | None:
    detail = get_rule_candidate(candidate_id)
    if not detail:
        return None
    normalized = detail["normalized_rule"]
    validation = validate_rule(normalized)
    source_case = detail["source_case"]
    return {
        "candidate_id": candidate_id,
        "source_case_id": source_case.get("id"),
        "validation": validation,
        "expected": (source_case.get("expected") or {}).get("final_result", {}),
        "normalized_rule": normalized,
        "impact_notes": [
            "현재 preview는 publish 전 정적 검증 중심입니다.",
            "publish 후 regression을 실행해 실제 엔진 결과 변화를 확인합니다.",
            "enabled=false로 publish하면 룰 파일은 저장되지만 엔진 결과에는 즉시 영향이 없습니다.",
        ],
    }


def _publish_path(version: str, candidate_id: str) -> Path:
    safe = candidate_id.replace("/", "_").replace("..", "_")
    return _repo_root() / "rules" / version / "case_derived" / f"{safe}.yaml"


def publish_candidate(candidate_id: str, request: PublishCandidateRequest) -> dict[str, Any] | None:
    detail = get_rule_candidate(candidate_id)
    if not detail:
        return None
    source_case_full = None
    for case in load_cases():
        candidate = case.get("rule_candidate")
        if isinstance(candidate, dict) and _candidate_id_from_case(case, candidate) == candidate_id:
            source_case_full = case
            break
    if not source_case_full:
        return None

    normalized = normalize_candidate_rule(detail["raw_candidate"], source_case_full, enable=request.enable)
    validation = validate_rule(normalized)
    path = _publish_path(request.version, candidate_id)
    if path.exists() and not request.overwrite:
        return {
            "published": False,
            "reason": "rule_already_exists",
            "path": str(path.relative_to(_repo_root())),
            "validation": validation,
            "normalized_rule": normalized,
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_yaml = yaml.safe_dump(normalized, allow_unicode=True, sort_keys=False)
    path.write_text(raw_yaml, encoding="utf-8")
    regression = run_regressions() if request.run_regression_after_publish else None
    return {
        "published": True,
        "candidate_id": candidate_id,
        "enabled": request.enable,
        "path": str(path.relative_to(_repo_root())),
        "validation": validation,
        "raw_yaml": raw_yaml,
        "regression_result": regression,
        "notes": ["후보 룰을 case_derived 디렉터리에 저장했습니다.", "loader가 하위 디렉터리를 읽도록 설정되어 있어 enabled=true인 경우 엔진에 반영됩니다."],
    }
