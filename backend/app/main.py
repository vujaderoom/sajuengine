from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(title="Saju Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RuleRunnerRequest(BaseModel):
    rule_version: str = "v1.0.0"

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "sajuengine"}

@app.get("/api/v1/rule-runner/sample")
def sample():
    return execute_rule_runner()

@app.post("/api/v1/rule-runner/execute")
def execute(_: RuleRunnerRequest):
    return execute_rule_runner()

def execute_rule_runner():
    fact = {
        "chart": {"year": "辛未", "month": "癸巳", "day": "己亥", "hour": "壬申"},
        "raw": {"HeatScore": 2, "MoistureScore": -1, "EWMScore": 1},
        "display": {"HeatIndex": 83, "MoistureIndex": 33, "EWMIndex": 25},
        "flow": {"blocked": True, "support_path": "weak_or_broken"},
        "binding": {"CI": 2, "BindingStrength": 3, "bindings": ["巳亥沖", "巳申合"]},
        "storage": {"root_support": 1, "base_stability": "weak"},
        "climate": {"season": "巳月", "temperature": "hot", "humidity": "dry"}
    }

    proposals = [
        {
            "proposal_id": "prop_flow_001",
            "candidate_type": "core_disease",
            "value": "유통 차단형 병",
            "score_delta": 2.0,
            "source_rule": "disease.flow.blocked.001",
            "reason": "생극 흐름이 결속이나 고립으로 막혀 유통 차단형 병 후보가 됩니다.",
            "evidence_query": {"tags": ["유통", "차단", "생극", "합충", "결속"]}
        },
        {
            "proposal_id": "prop_medicine_001",
            "candidate_type": "medicine",
            "value": "유통 개통형",
            "score_delta": 2.0,
            "source_rule": "medicine.flow.opening.001",
            "reason": "흐름이 막힌 구조를 여는 약 후보입니다.",
            "evidence_query": {"tags": ["약", "유통", "개통"]}
        },
        {
            "proposal_id": "prop_yongshin_001",
            "candidate_type": "yongshin",
            "value": "庚",
            "score_delta": 2.0,
            "source_rule": "yongshin.flow.metal.001",
            "reason": "유통 개통형 약의 실행 상징으로 庚을 용신 후보로 제안합니다.",
            "evidence_query": {"tags": ["용신", "庚", "금", "유통"]}
        }
    ]

    counter = {
        "rule_id": "counter.flow.open_path.001",
        "target_proposal": "prop_flow_001",
        "applied": False,
        "score_delta": 0.0,
        "reason": "support_path가 open이 아니므로 감점하지 않습니다."
    }

    final_result = {
        "core_disease": "유통 차단형 병",
        "derived_diseases": ["기후형 병"],
        "medicine": "유통 개통형",
        "yongshin": "庚",
        "secondary_yongshin": ["壬"],
        "depth": 2,
        "stability_grade": "B",
        "confidence": 0.86
    }

    decision_trace = [
        {"type": "FACT_BUILT", "stage": "fact_builder", "output_json": fact},
        {"type": "RULE_EVALUATED", "stage": "L2_PROPOSAL", "rule_id": "disease.flow.blocked.001", "fired": True},
        {"type": "PROPOSAL_CREATED", "stage": "L2_PROPOSAL", "proposal": proposals[0]},
        {"type": "COUNTER_RULE_APPLIED", "stage": "COUNTER_RULE", "counter_json": counter},
        {"type": "FINALIZED", "stage": "FINALIZER", "output_json": final_result}
    ]

    return {
        "execution_id": "ex_" + uuid4().hex[:12],
        "chart_id": "chart_" + uuid4().hex[:12],
        "rule_version": "v1.0.0",
        "facts": fact,
        "proposals": proposals,
        "counter_rules_applied": [counter],
        "final_result": final_result,
        "decision_trace": decision_trace
    }
