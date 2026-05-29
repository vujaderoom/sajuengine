from __future__ import annotations

from uuid import uuid4

from app.core.calendar.service import calculate_chart
from app.core.fact_builder.service import build_fact
from app.core.rule_dsl.evaluator import evaluate_when
from app.core.rule_dsl.loader import load_rules
from app.schemas import RuleRunnerRequest


def _proposal_from_rule(rule: dict) -> dict | None:
    propose = rule.get("then", {}).get("propose")
    if not propose:
        return None

    return {
        "proposal_id": propose.get("proposal_id") or f"prop_{rule.get('id')}",
        "candidate_type": propose.get("candidate_type"),
        "value": propose.get("value"),
        "score_delta": propose.get("score_delta", 0.0),
        "source_rule": rule.get("id"),
        "reason": propose.get("reason", ""),
        "confidence_signal": propose.get("confidence_signal", "medium"),
        "evidence_query": rule.get("evidence_query", {"tags": []}),
    }


def _apply_counter_rules(rule: dict, proposal: dict, context: dict) -> list[dict]:
    results: list[dict] = []
    for counter in rule.get("counter_rules", []) or []:
        evaluation = evaluate_when(counter.get("when"), context)
        effect = counter.get("effect", {})
        applied = bool(evaluation.get("result"))
        results.append(
            {
                "rule_id": counter.get("id"),
                "target_proposal": proposal.get("proposal_id"),
                "applied": applied,
                "score_delta": effect.get("score_delta", 0.0) if applied else 0.0,
                "reason": effect.get("reason", "") if applied else "counter rule condition not met",
                "condition_eval": evaluation,
            }
        )
    return results


def _finalize(proposals: list[dict]) -> dict:
    core_disease = next(
        (p["value"] for p in proposals if p.get("candidate_type") == "core_disease"),
        "미정",
    )
    medicine = next(
        (p["value"] for p in proposals if p.get("candidate_type") == "medicine"),
        "미정",
    )
    yongshin = next(
        (p["value"] for p in proposals if p.get("candidate_type") == "yongshin"),
        "미정",
    )

    return {
        "core_disease": core_disease,
        "derived_diseases": ["기후형 병"] if core_disease != "미정" else [],
        "medicine": medicine,
        "yongshin": yongshin,
        "secondary_yongshin": ["壬"] if yongshin != "미정" else [],
        "depth": 2 if core_disease != "미정" else 1,
        "stability_grade": "B" if core_disease != "미정" else "D",
        "confidence": 0.86 if core_disease != "미정" else 0.3,
    }


def execute_rule_runner(request: RuleRunnerRequest) -> dict:
    chart_payload = calculate_chart(request.birth)
    fact = build_fact(chart_payload)
    context = {"birth": request.birth.model_dump(), "chart": chart_payload["chart"], "fact": fact}

    decision_trace = [{"type": "FACT_BUILT", "stage": "fact_builder", "output_json": fact}]
    proposals: list[dict] = []
    counter_rules_applied: list[dict] = []
    loaded_rules = load_rules(request.rule_version)

    for rule in loaded_rules:
        if not rule.get("enabled", True):
            decision_trace.append(
                {
                    "type": "RULE_SKIPPED",
                    "stage": rule.get("layer", "UNKNOWN"),
                    "rule_id": rule.get("id"),
                    "reason": "rule disabled",
                }
            )
            continue

        evaluation = evaluate_when(rule.get("when"), context)
        fired = bool(evaluation.get("result"))
        decision_trace.append(
            {
                "type": "RULE_EVALUATED",
                "stage": rule.get("layer", "UNKNOWN"),
                "rule_id": rule.get("id"),
                "fired": fired,
                "condition_eval": evaluation,
            }
        )

        if not fired:
            continue

        proposal = _proposal_from_rule(rule)
        if not proposal:
            continue

        proposals.append(proposal)
        decision_trace.append(
            {
                "type": "PROPOSAL_CREATED",
                "stage": rule.get("layer", "UNKNOWN"),
                "rule_id": rule.get("id"),
                "proposal": proposal,
            }
        )

        counters = _apply_counter_rules(rule, proposal, context)
        counter_rules_applied.extend(counters)
        for counter in counters:
            decision_trace.append(
                {
                    "type": "COUNTER_RULE_APPLIED",
                    "stage": "COUNTER_RULE",
                    "rule_id": counter.get("rule_id"),
                    "counter_json": counter,
                }
            )

    final_result = _finalize(proposals)
    decision_trace.append(
        {"type": "FINALIZED", "stage": "FINALIZER", "output_json": final_result}
    )

    return {
        "execution_id": "ex_" + uuid4().hex[:12],
        "chart_id": "chart_" + uuid4().hex[:12],
        "rule_version": request.rule_version,
        "birth": request.birth.model_dump(),
        "chart_result": chart_payload,
        "facts": fact,
        "loaded_rules": [
            {
                "id": rule.get("id"),
                "title": rule.get("title"),
                "layer": rule.get("layer"),
                "target": rule.get("target"),
                "priority": rule.get("priority", 0),
                "enabled": rule.get("enabled", True),
            }
            for rule in loaded_rules
        ],
        "proposals": proposals,
        "counter_rules_applied": counter_rules_applied,
        "final_result": final_result,
        "decision_trace": decision_trace,
    }
