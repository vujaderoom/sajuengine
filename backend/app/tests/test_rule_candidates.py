from app.core.rule_candidates.service import list_rule_candidates, get_rule_candidate, preview_candidate_impact, normalize_candidate_rule


def test_rule_candidates_list_shape():
    result = list_rule_candidates()
    assert "total" in result
    assert "candidates" in result
    assert isinstance(result["candidates"], list)


def test_rule_candidate_detail_if_available():
    listed = list_rule_candidates()["candidates"]
    if not listed:
        return
    candidate_id = listed[0]["id"]
    detail = get_rule_candidate(candidate_id)
    assert detail is not None
    assert "normalized_rule" in detail
    assert "validation" in detail
    assert "normalized_rule_yaml" in detail


def test_rule_candidate_impact_if_available():
    listed = list_rule_candidates()["candidates"]
    if not listed:
        return
    candidate_id = listed[0]["id"]
    impact = preview_candidate_impact(candidate_id)
    assert impact is not None
    assert "validation" in impact
    assert "normalized_rule" in impact


def test_normalize_candidate_rule_minimal():
    source_case = {"id": "GC-TEST", "title": "테스트 케이스"}
    candidate = {
        "id": "case_rule_candidate_gc-test",
        "title": "테스트 룰 후보",
        "priority": 50,
        "when": {"all": [{"path": "chart.day", "op": "contains", "value": "己"}]},
        "then": {"propose": {"candidate_type": "yongshin", "value": "火", "symbols": ["巳火", "午火"], "score_delta": 1.0}},
    }
    rule = normalize_candidate_rule(candidate, source_case, enable=False)
    assert rule["id"] == "case_rule_candidate_gc-test"
    assert rule["layer"] == "L2_PROPOSAL"
    assert rule["target"] == "yongshin_candidate"
    assert rule["enabled"] is False
    assert rule["then"]["propose"]["value"] == "火"
