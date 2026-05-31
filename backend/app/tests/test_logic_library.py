from app.core.logic_library.service import LogicStructureRequest, structure_logic_text


def test_structure_muto_fire_sentence():
    result = structure_logic_text(LogicStructureRequest(original_text="무토일간이 화가 많으면 술, 여자를 좋아한다."))
    structured = result["structured"]
    assert structured["category"] == "일간별 성향"
    conditions = structured["conditions"]["all"]
    assert any(c.get("value") == "戊" for c in conditions)
    assert any(c.get("value") == "火" for c in conditions)
    tags = structured["effect"]["tags"]
    assert "향락성" in tags
    assert "이성관심" in tags
    assert structured["caution"]["risk_level"] == "high"


def test_structure_general_logic_sentence():
    result = structure_logic_text(LogicStructureRequest(original_text="기토가 수습에 잠기면 화로 말려야 한다."))
    structured = result["structured"]
    assert structured["category"] in ["병약용신", "일간별 성향", "일반 명리 문장"]
    assert "말림" in structured["effect"]["tags"] or "수습" in structured["effect"]["tags"]
