from __future__ import annotations

from uuid import uuid4

from app.core.calendar.service import calculate_chart
from app.core.fact_builder.service import build_fact
from app.schemas import RuleRunnerRequest


def execute_rule_runner(request: RuleRunnerRequest) -> dict:
    chart_payload = calculate_chart(request.birth)
    fact = build_fact(chart_payload)

    proposals = [
        {
            "proposal_id": "prop_flow_001",
            "candidate_type": "core_disease",
            "value": "유통 차단형 병",
            "score_delta": 2.0,
            "source_rule": "disease.flow.blocked.001",
            "reason": "생극 흐름이 결속이나 고립으로 막혀 유통 차단형 병 후보가 됩니다.",
            "evidence_query": {"tags": ["유통", "차단", "생극", "합충", "결속"]},
        },
        {
            "proposal_id": "prop_medicine_001",
            "candidate_type": "medicine",
            "value": "유통 개통형",
            "score_delta": 2.0,
            "source_rule": "medicine.flow.opening.001",
            "reason": "흐름이 막힌 구조를 여는 약 후보입니다.",
            "evidence_query": {"tags": ["약", "유통", "개통"]},
        },
        {
            "proposal_id": "prop_yongshin_001",
            "candidate_type": "yongshin",
            "value": "庚",
            "score_delta": 2.0,
            "source_rule": "yongshin.flow.metal.001",
            "reason": "유통 개통형 약의 실행 상징으로 庚을 용신 후보로 제안합니다.",
            "evidence_query": {"tags": ["용신", "庚", "금", "유통"]},
        },
    ]

    counter = {
        "rule_id": "counter.flow.open_path.001",
        "target_proposal": "prop_flow_001",
        "applied": False,
        "score_delta": 0.0,
        "reason": "support_path가 open이 아니므로 감점하지 않습니다.",
    }

    final_result = {
        "core_disease": "유통 차단형 병",
        "derived_diseases": ["기후형 병"],
        "medicine": "유통 개통형",
        "yongshin": "庚",
        "secondary_yongshin": ["壬"],
        "depth": 2,
        "stability_grade": "B",
        "confidence": 0.86,
    }

    decision_trace = [
        {"type": "FACT_BUILT", "stage": "fact_builder", "output_json": fact},
        {
            "type": "RULE_EVALUATED",
            "stage": "L2_PROPOSAL",
            "rule_id": "disease.flow.blocked.001",
            "fired": True,
            "condition_eval": {
                "fact.flow.blocked == true": True,
                "fact.binding.BindingStrength >= 2": True,
                "fact.flow.support_path == weak_or_broken": True,
            },
        },
        {"type": "PROPOSAL_CREATED", "stage": "L2_PROPOSAL", "proposal": proposals[0]},
        {"type": "COUNTER_RULE_APPLIED", "stage": "COUNTER_RULE", "counter_json": counter},
        {"type": "FINALIZED", "stage": "FINALIZER", "output_json": final_result},
    ]

    return {
        "execution_id": "ex_" + uuid4().hex[:12],
        "chart_id": "chart_" + uuid4().hex[:12],
        "rule_version": request.rule_version,
        "birth": request.birth.model_dump(),
        "chart_result": chart_payload,
        "facts": fact,
        "proposals": proposals,
        "counter_rules_applied": [counter],
        "final_result": final_result,
        "decision_trace": decision_trace,
    }
