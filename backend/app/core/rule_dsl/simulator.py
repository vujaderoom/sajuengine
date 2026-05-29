from __future__ import annotations

from typing import Any

from app.core.calendar.service import calculate_chart
from app.core.fact_builder.service import build_fact
from app.core.rule_dsl.evaluator import evaluate_when
from app.core.rule_dsl.loader import detail_rule, get_rule
from app.schemas import BirthInput


def simulate_rule(rule_id: str, birth: BirthInput | None = None, version: str = "v1.0.0") -> dict[str, Any] | None:
    rule = get_rule(rule_id, version)
    if not rule:
        return None

    birth_input = birth or BirthInput()
    chart_payload = calculate_chart(birth_input)
    fact = build_fact(chart_payload)
    context = {"birth": birth_input.model_dump(), "chart": chart_payload["chart"], "fact": fact}
    evaluation = evaluate_when(rule.get("when"), context)
    proposal = rule.get("then", {}).get("propose") if evaluation.get("result") else None

    return {
        "rule_version": version,
        "rule": detail_rule(rule_id, version),
        "birth": birth_input.model_dump(),
        "chart_result": chart_payload,
        "facts": fact,
        "fired": bool(evaluation.get("result")),
        "condition_eval": evaluation,
        "proposal_preview": proposal,
    }
