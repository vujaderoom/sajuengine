from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Saju Engine", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BirthInput(BaseModel):
    name: str = "sample"
    sex: Literal["male", "female", "unknown"] = "male"
    birth_datetime: str = "1991-05-29T16:36:00"
    calendar_type: Literal["solar", "lunar"] = "solar"
    timezone: str = "Asia/Seoul"
    location: str = "Seoul"


class RuleRunnerRequest(BaseModel):
    birth: BirthInput = Field(default_factory=BirthInput)
    rule_version: str = "v1.0.0"


HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

HOUR_BRANCHES = [
    (23, "子"),
    (1, "丑"),
    (3, "寅"),
    (5, "卯"),
    (7, "辰"),
    (9, "巳"),
    (11, "午"),
    (13, "未"),
    (15, "申"),
    (17, "酉"),
    (19, "戌"),
    (21, "亥"),
]

HOUR_STEM_START_BY_DAY_STEM = {
    "甲": "甲",
    "己": "甲",
    "乙": "丙",
    "庚": "丙",
    "丙": "戊",
    "辛": "戊",
    "丁": "庚",
    "壬": "庚",
    "戊": "壬",
    "癸": "壬",
}


def _ganzhi(index: int) -> str:
    return HEAVENLY_STEMS[index % 10] + EARTHLY_BRANCHES[index % 12]


def _year_pillar(dt: datetime) -> str:
    # Scaffold: 입춘 전후 보정은 다음 단계에서 solar-term engine으로 교체한다.
    return _ganzhi(dt.year - 1984)


def _month_pillar(dt: datetime, year_stem: str) -> str:
    # Scaffold: 월지는 양력 월 기준 임시값이다. 다음 단계에서 절입 기준으로 교체한다.
    month_branch_by_solar_month = {
        1: "丑",
        2: "寅",
        3: "卯",
        4: "辰",
        5: "巳",
        6: "午",
        7: "未",
        8: "申",
        9: "酉",
        10: "戌",
        11: "亥",
        12: "子",
    }
    month_branch = month_branch_by_solar_month[dt.month]

    # 甲己年 丙寅월 시작 규칙을 간단화한 scaffold.
    start_stem_by_year_stem = {
        "甲": "丙",
        "己": "丙",
        "乙": "戊",
        "庚": "戊",
        "丙": "庚",
        "辛": "庚",
        "丁": "壬",
        "壬": "壬",
        "戊": "甲",
        "癸": "甲",
    }
    start_stem = start_stem_by_year_stem[year_stem]
    branch_index = EARTHLY_BRANCHES.index(month_branch)
    tiger_index = EARTHLY_BRANCHES.index("寅")
    offset = (branch_index - tiger_index) % 12
    stem_index = (HEAVENLY_STEMS.index(start_stem) + offset) % 10
    return HEAVENLY_STEMS[stem_index] + month_branch


def _day_pillar(dt: datetime) -> str:
    # Scaffold: 1991-05-29 = 己亥를 anchor로 둔다. 다음 단계에서 정확한 일진 계산으로 교체한다.
    anchor = datetime(1991, 5, 29)
    anchor_index = 35  # 己亥
    return _ganzhi(anchor_index + (dt.date() - anchor.date()).days)


def _hour_branch(hour: int) -> str:
    if hour == 23 or hour == 0:
        return "子"
    for start_hour, branch in reversed(HOUR_BRANCHES[1:]):
        if hour >= start_hour:
            return branch
    return "子"


def _hour_pillar(dt: datetime, day_stem: str) -> str:
    branch = _hour_branch(dt.hour)
    start_stem = HOUR_STEM_START_BY_DAY_STEM[day_stem]
    offset = EARTHLY_BRANCHES.index(branch)
    stem = HEAVENLY_STEMS[(HEAVENLY_STEMS.index(start_stem) + offset) % 10]
    return stem + branch


def calculate_chart(birth: BirthInput) -> dict:
    dt = datetime.fromisoformat(birth.birth_datetime)
    year = _year_pillar(dt)
    month = _month_pillar(dt, year[0])
    day = _day_pillar(dt)
    hour = _hour_pillar(dt, day[0])

    return {
        "birth": birth.model_dump(),
        "chart": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
        },
        "engine_notes": [
            "calendar scaffold v0.2.0",
            "월주는 현재 양력 월 기준 scaffold이며 다음 단계에서 절입 기준으로 교체 예정",
            "일주는 1991-05-29 己亥 anchor 기반 scaffold",
        ],
    }


def build_fact(chart_payload: dict) -> dict:
    chart = chart_payload["chart"]
    month_branch = chart["month"][1]

    heat_score = 2 if month_branch in ["巳", "午", "未"] else 0
    moisture_score = -1 if month_branch in ["巳", "午"] else 0
    ewm_score = 1 if "亥" in chart["day"] else 0

    return {
        "chart": chart,
        "raw": {
            "HeatScore": heat_score,
            "MoistureScore": moisture_score,
            "EWMScore": ewm_score,
        },
        "display": {
            "HeatIndex": min(100, max(0, 50 + heat_score * 16)),
            "MoistureIndex": min(100, max(0, 50 + moisture_score * 17)),
            "EWMIndex": min(100, max(0, ewm_score * 25)),
        },
        "flow": {"blocked": True, "support_path": "weak_or_broken"},
        "binding": {"CI": 2, "BindingStrength": 3, "bindings": ["巳亥沖", "巳申合"]},
        "storage": {"root_support": 1, "base_stability": "weak"},
        "climate": {"season": chart["month"], "temperature": "hot", "humidity": "dry"},
        "notes": [
            "fact_builder scaffold v0.2.0",
            "raw score는 내부 룰용이며 display index는 UI 표시 전용",
        ],
    }


def execute_rule_runner(request: RuleRunnerRequest):
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


@app.get("/")
def root():
    return {
        "service": "sajuengine",
        "docs": "/docs",
        "health": "/api/health",
        "sample": "/api/v1/rule-runner/sample",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "sajuengine", "version": "0.2.0"}


@app.post("/api/v1/charts/calculate")
def calculate(birth: BirthInput):
    return calculate_chart(birth)


@app.post("/api/v1/charts/analyze")
def analyze(birth: BirthInput):
    chart_payload = calculate_chart(birth)
    return {"chart_result": chart_payload, "facts": build_fact(chart_payload)}


@app.get("/api/v1/rule-runner/sample")
def sample():
    return execute_rule_runner(RuleRunnerRequest())


@app.post("/api/v1/rule-runner/execute")
def execute(request: RuleRunnerRequest):
    return execute_rule_runner(request)
