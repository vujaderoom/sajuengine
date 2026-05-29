from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.calendar.service import calculate_chart
from app.core.cases.loader import get_case, summarize_cases
from app.core.fact_builder.service import build_fact
from app.core.regression.runner import run_case_by_id, run_regressions
from app.core.report_payload.builder import build_report_payload
from app.core.rule_dsl.loader import detail_rule, summarize_rules
from app.core.rule_dsl.simulator import simulate_rule
from app.core.rule_runner.service import execute_rule_runner
from app.schemas import BirthInput, RuleRunnerRequest

app = FastAPI(title="Saju Engine", version="0.9.0")

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
        "version": "0.9.0",
        "docs": "/docs",
        "health": "/api/health",
        "sample": "/api/v1/rule-runner/sample",
        "rules": "/api/v1/rules",
        "cases": "/api/v1/cases",
        "regressions": "/api/v1/regressions/run",
        "report_preview": "/api/v1/reports/preview",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "sajuengine", "version": "0.9.0"}


@app.get("/api/v1/cases")
def cases():
    return {"cases": summarize_cases()}


@app.get("/api/v1/cases/{case_id}")
def case_detail(case_id: str):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.get("/api/v1/cases/{case_id}/run")
def case_run(case_id: str):
    result = run_case_by_id(case_id)
    if not result:
        raise HTTPException(status_code=404, detail="Case not found")
    return result


@app.get("/api/v1/rules")
def rules(version: str = "v1.0.0"):
    return {"rule_version": version, "rules": summarize_rules(version)}


@app.get("/api/v1/rules/{rule_id}")
def rule_detail(rule_id: str, version: str = "v1.0.0"):
    rule = detail_rule(rule_id, version)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@app.post("/api/v1/rules/{rule_id}/simulate")
def rule_simulate(rule_id: str, birth: BirthInput | None = None, version: str = "v1.0.0"):
    result = simulate_rule(rule_id, birth, version)
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    return result


@app.get("/api/v1/regressions/run")
def regression_run():
    return run_regressions()


@app.post("/api/v1/reports/preview")
def report_preview(request: RuleRunnerRequest):
    return build_report_payload(request)


@app.get("/api/v1/reports/preview/sample")
def report_preview_sample():
    return build_report_payload(RuleRunnerRequest())


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
