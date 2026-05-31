from app.core.rule_runner.service import execute_rule_runner
from app.schemas import RuleRunnerRequest


def test_rule_runner_logic_match_shape():
    result = execute_rule_runner(RuleRunnerRequest())
    assert "logic_matches" in result
    assert "logic_matches" in result["facts"]
    assert "logic_match_meta" in result["facts"]
    assert result["facts"]["logic_match_meta"]["model_version"] == "logic_match_v1.0.0"
    assert any(item.get("type") == "LOGIC_CARDS_MATCHED" for item in result["decision_trace"])
