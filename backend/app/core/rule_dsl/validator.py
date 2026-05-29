from __future__ import annotations

from typing import Any

from app.core.rule_dsl.loader import load_rules, get_rule

REQUIRED_FIELDS = [
    "id",
    "title",
    "layer",
    "target",
    "priority",
    "enabled",
    "version",
    "when",
    "then",
    "score",
    "counter_rules",
    "explain",
    "evidence_query",
    "status",
]

ALLOWED_LAYERS = {"L1_FACT_RULE", "L2_PROPOSAL", "L3_COUNTER_RULE", "L4_FINALIZER"}
ALLOWED_TARGETS = {
    "core_disease_candidate",
    "derived_disease_candidate",
    "medicine_candidate",
    "yongshin_candidate",
    "gishin_candidate",
    "depth_signal",
    "delta_signal",
    "auxiliary_tag",
}

FORBIDDEN_DIRECT_SET_KEYS = {"set", "yongshin", "core_disease", "medicine", "depth"}
FORBIDDEN_DIRECT_CONCEPTS = ["신강", "신약", "강약", "身强", "身弱"]
AUXILIARY_ONLY_CONCEPTS = ["십신", "신살", "12운성", "십이운성"]
DISPLAY_SCORE_PATTERNS = ["HeatIndex", "MoistureIndex", "EWMIndex", "WaterSupplyIndex"]
RAW_SCORE_PATTERNS = ["HeatScore", "MoistureScore", "EWMScore", "WaterSupplyScore", "Depth"]


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for key, child in value.items():
            out.extend(_walk_strings(key))
            out.extend(_walk_strings(child))
        return out
    if isinstance(value, list):
        out: list[str] = []
        for child in value:
            out.extend(_walk_strings(child))
        return out
    return []


def _has_forbidden_then(rule: dict[str, Any]) -> bool:
    then = rule.get("then", {})
    if not isinstance(then, dict):
        return True
    if "propose" not in then:
        return True
    return any(key in then for key in FORBIDDEN_DIRECT_SET_KEYS)


def validate_rule(rule: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    missing = [field for field in REQUIRED_FIELDS if field not in rule]
    checks.append("required_fields")
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    checks.append("layer_allowed")
    if rule.get("layer") not in ALLOWED_LAYERS:
        errors.append(f"invalid layer: {rule.get('layer')}")

    checks.append("target_allowed")
    if rule.get("target") not in ALLOWED_TARGETS:
        errors.append(f"invalid target: {rule.get('target')}")

    checks.append("proposal_only")
    if _has_forbidden_then(rule):
        errors.append("then must use propose only; direct set/final yongshin/core_disease/medicine is forbidden")

    all_strings = _walk_strings(rule)
    joined = "\n".join(all_strings)

    checks.append("no_strength_weakness_direct_yongshin")
    if any(token in joined for token in FORBIDDEN_DIRECT_CONCEPTS):
        errors.append("신강·신약/강약 개념으로 핵심 병·약·용신을 직접 결정하는 룰은 금지")

    checks.append("auxiliary_tags_not_core_decision")
    if any(token in joined for token in AUXILIARY_ONLY_CONCEPTS) and rule.get("target") in {
        "core_disease_candidate",
        "medicine_candidate",
        "yongshin_candidate",
    }:
        warnings.append("십신/신살/12운성은 보조 태그로만 사용하고 핵심 결론 결정 근거로 쓰지 않는지 검토 필요")

    checks.append("raw_score_only")
    if any(pattern in joined for pattern in DISPLAY_SCORE_PATTERNS):
        errors.append("display index는 UI 전용이며 룰 조건에는 raw score를 사용해야 함")
    if any(pattern in joined for pattern in RAW_SCORE_PATTERNS):
        checks.append("raw_score_reference_found")

    checks.append("tests_declared")
    if "tests" not in rule:
        warnings.append("tests.positive_cases / tests.negative_cases가 없어서 impact 검증 연결이 약함")

    checks.append("evidence_query_declared")
    evidence_query = rule.get("evidence_query", {})
    if not isinstance(evidence_query, dict) or not evidence_query.get("tags"):
        warnings.append("evidence_query.tags가 비어 있어 RAG 근거 연결성이 낮음")

    return {
        "rule_id": rule.get("id"),
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }


def validate_rule_by_id(rule_id: str, version: str = "v1.0.0") -> dict[str, Any] | None:
    rule = get_rule(rule_id, version)
    if not rule:
        return None
    return validate_rule(rule)


def validate_all_rules(version: str = "v1.0.0") -> dict[str, Any]:
    results = [validate_rule(rule) for rule in load_rules(version)]
    return {
        "rule_version": version,
        "total": len(results),
        "valid": sum(1 for item in results if item["valid"]),
        "invalid": sum(1 for item in results if not item["valid"]),
        "results": results,
    }
