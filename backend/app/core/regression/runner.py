from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.core.rule_runner.service import execute_rule_runner
from app.schemas import BirthInput, RuleRunnerRequest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def golden_cases_dir() -> Path:
    return _repo_root() / "golden_cases"


def _get_path(data: dict[str, Any], dotted_path: str) -> Any:
    current: Any = data
    for part in dotted_path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _flatten_expected(prefix: str, value: Any) -> list[tuple[str, Any]]:
    if isinstance(value, dict):
        items: list[tuple[str, Any]] = []
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            items.extend(_flatten_expected(child_prefix, child))
        return items
    return [(prefix, value)]


def load_golden_cases() -> list[dict[str, Any]]:
    base = golden_cases_dir()
    if not base.exists():
        return []

    cases: list[dict[str, Any]] = []
    for path in sorted(base.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        data["_path"] = str(path.relative_to(_repo_root()))
        cases.append(data)
    return cases


def run_single_case(case: dict[str, Any]) -> dict[str, Any]:
    birth = BirthInput(**case["birth"])
    result = execute_rule_runner(RuleRunnerRequest(birth=birth))

    expected_checks = _flatten_expected("", case.get("expected", {}))
    checks = []
    for path, expected in expected_checks:
        actual = _get_path(result, path)
        passed = actual == expected
        checks.append(
            {
                "path": path,
                "expected": expected,
                "actual": actual,
                "passed": passed,
            }
        )

    passed = all(check["passed"] for check in checks)
    return {
        "id": case.get("id"),
        "title": case.get("title"),
        "status": case.get("status"),
        "path": case.get("_path"),
        "passed": passed,
        "checks": checks,
        "actual_result": result,
    }


def run_regressions() -> dict[str, Any]:
    cases = load_golden_cases()
    results = [run_single_case(case) for case in cases]
    passed_count = sum(1 for result in results if result["passed"])
    return {
        "total": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "results": results,
    }
