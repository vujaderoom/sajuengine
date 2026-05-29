from app.core.calendar.service import calculate_chart
from app.core.fact_builder.service import build_fact
from app.core.rule_runner.service import execute_rule_runner
from app.schemas import BirthInput, RuleRunnerRequest


def test_chart_scaffold_sample_case():
    birth = BirthInput(birth_datetime="1991-05-29T16:36:00")
    result = calculate_chart(birth)

    assert result["chart"]["year"] == "辛未"
    assert result["chart"]["month"] == "癸巳"
    assert result["chart"]["day"] == "己亥"
    assert result["chart"]["hour"] == "壬申"


def test_fact_builder_keeps_raw_and_display_scores_separate():
    chart_payload = calculate_chart(BirthInput())
    fact = build_fact(chart_payload)

    assert "raw" in fact
    assert "display" in fact
    assert -3 <= fact["raw"]["HeatScore"] <= 3
    assert 0 <= fact["display"]["HeatIndex"] <= 100


def test_rule_runner_returns_trace_and_final_result():
    result = execute_rule_runner(RuleRunnerRequest())

    assert result["final_result"]["core_disease"] == "유통 차단형 병"
    assert result["final_result"]["medicine"] == "유통 개통형"
    assert result["final_result"]["yongshin"] == "庚"
    assert len(result["decision_trace"]) >= 5
