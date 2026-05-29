from __future__ import annotations

from typing import Any

from app.core.regression.runner import load_golden_cases, run_single_case


def rule_impact(rule_id: str) -> dict[str, Any]:
    cases = load_golden_cases()
    impacts: list[dict[str, Any]] = []
    for case in cases:
        run = run_single_case(case)
        actual_result = run.get("actual_result", {})
        trace = actual_result.get("decision_trace", [])
        proposal_sources = [p.get("source_rule") for p in actual_result.get("proposals", [])]
        evaluated = [event for event in trace if event.get("rule_id") == rule_id and event.get("type") == "RULE_EVALUATED"]
        fired = any(bool(event.get("fired")) for event in evaluated)
        produced_proposal = rule_id in proposal_sources
        linked_by_expected = rule_id in str(case.get("expected", {})) or rule_id in str(case.get("notes", []))
        if evaluated or produced_proposal or linked_by_expected:
            impacts.append(
                {
                    "case_id": case.get("id"),
                    "title": case.get("title"),
                    "passed": run.get("passed"),
                    "evaluated": bool(evaluated),
                    "fired": fired,
                    "produced_proposal": produced_proposal,
                    "linked_by_expected": linked_by_expected,
                    "final_result": actual_result.get("final_result", {}),
                    "checks": run.get("checks", []),
                }
            )
    return {
        "rule_id": rule_id,
        "total_cases": len(cases),
        "impacted_cases": len(impacts),
        "impacts": impacts,
    }
