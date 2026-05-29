from __future__ import annotations

from typing import Any

from app.core.regression.runner import run_regressions
from app.core.rule_dsl.validator import validate_all_rules, validate_rule_by_id


def release_readiness(version: str = "v1.0.0") -> dict[str, Any]:
    validation = validate_all_rules(version)
    regression = run_regressions()
    ready = validation["invalid"] == 0 and regression["failed"] == 0
    blockers: list[str] = []
    if validation["invalid"] > 0:
        blockers.append("invalid_rules")
    if regression["failed"] > 0:
        blockers.append("regression_failed")
    return {
        "rule_version": version,
        "ready_to_release": ready,
        "status": "ready" if ready else "blocked",
        "blockers": blockers,
        "validation_summary": {
            "total": validation["total"],
            "valid": validation["valid"],
            "invalid": validation["invalid"],
        },
        "regression_summary": {
            "total": regression["total"],
            "passed": regression["passed"],
            "failed": regression["failed"],
        },
        "required_steps": [
            "Rule DSL validation must pass",
            "Golden Case regression must pass",
            "Reviewer approval is required before activation",
        ],
    }


def rule_release_preview(rule_id: str, version: str = "v1.0.0") -> dict[str, Any] | None:
    validation = validate_rule_by_id(rule_id, version)
    if not validation:
        return None
    readiness = release_readiness(version)
    return {
        "rule_id": rule_id,
        "rule_version": version,
        "validation": validation,
        "workflow": {
            "current_status": "yaml_saved",
            "next_status": "ready_for_review" if validation["valid"] else "needs_fix",
            "can_request_release": validation["valid"],
            "global_release_readiness": readiness,
        },
    }
