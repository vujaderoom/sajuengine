from app.core.logic_library.service import LogicMatchRequest, LogicStructureRequest, _match_card, structure_logic_text
from app.core.calendar.service import calculate_chart
from app.core.fact_builder.service import build_fact
from app.schemas import BirthInput


def test_structure_muto_fire_sentence():
    result = structure_logic_text(LogicStructureRequest(original_text="무토일간이 화가 많으면 술, 여자를 좋아한다."))
    structured = result["structured"]
    assert structured["category"] == "일간별 성향"
    conditions = structured["conditions"]["all"]
    assert any(c.get("value") == "戊" for c in conditions)
    assert any(c.get("value") == "火" for c in conditions)
    assert any(c.get("path", "").startswith("DeltaInputs") for c in conditions)
    tags = structured["effect"]["tags"]
    assert "향락성" in tags
    assert "이성관심" in tags
    assert structured["caution"]["risk_level"] == "high"


def test_structure_general_logic_sentence():
    result = structure_logic_text(LogicStructureRequest(original_text="기토가 수습에 잠기면 화로 말려야 한다."))
    structured = result["structured"]
    assert structured["category"] in ["병약용신", "일간별 성향", "일반 명리 문장"]
    assert "말림" in structured["effect"]["tags"] or "수습" in structured["effect"]["tags"]
    assert any(c.get("path") == "DeltaInputs.climate.MoistureScore" for c in structured["conditions"]["all"])


def test_logic_match_delta_inputs_condition():
    chart_payload = calculate_chart(BirthInput(birth_datetime="1991-05-29T16:36:00", sex="male"))
    facts = build_fact(chart_payload)
    card = {
        "structured": {
            "conditions": {"all": [{"path": "DeltaInputs.climate.MoistureScore", "op": "gte", "value": 2, "label": "과습"}]},
            "effect": {"tags": ["수습"]},
        }
    }
    score, reasons = _match_card(card, chart_payload["chart"], facts)
    assert score > 0
    assert reasons
