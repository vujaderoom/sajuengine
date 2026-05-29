from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.calendar.service import calculate_chart
from app.core.fact_builder.service import build_fact
from app.core.rule_runner.service import execute_rule_runner
from app.schemas import BirthInput, RuleRunnerRequest

app = FastAPI(title="Saju Engine", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "sajuengine",
        "version": "0.3.0",
        "docs": "/docs",
        "health": "/api/health",
        "sample": "/api/v1/rule-runner/sample",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "sajuengine", "version": "0.3.0"}


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
