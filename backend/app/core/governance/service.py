from __future__ import annotations

from typing import Any

from app.core.regression.runner import run_regressions
from app.core.rule_dsl.validator import validate_all_rules
from app.core.rule_release.workflow import release_readiness


def governance_dashboard(version: str = "v1.0.0") -> dict[str, Any]:
    validation = validate_all_rules(version)
    regression = run_regressions()
    release = release_readiness(version)
    invalid_rules = [item for item in validation["results"] if not item["valid"]]
    warning_rules = [item for item in validation["results"] if item.get("warnings")]
    return {
        "rule_version": version,
        "validation_summary": {
            "total": validation["total"],
            "valid": validation["valid"],
            "invalid": validation["invalid"],
            "warning_rules": len(warning_rules),
        },
        "regression_summary": {
            "total": regression["total"],
            "passed": regression["passed"],
            "failed": regression["failed"],
        },
        "release_readiness": release,
        "invalid_rules": invalid_rules,
        "warning_rules": warning_rules,
        "recommendations": [
            "invalid_rules가 0이어야 release 가능",
            "regression failed가 0이어야 release 가능",
            "warnings는 release blocker는 아니지만 룰 품질 관리 대상으로 검토",
        ],
    }
