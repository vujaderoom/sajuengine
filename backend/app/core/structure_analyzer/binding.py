from __future__ import annotations


def calculate_binding(relations: dict, element_counts: dict[str, int]) -> dict:
    binding_kinds = {"branch_liuhe", "trine_half", "trine_full", "directional_half", "directional_full", "self_penalty"}
    relation_items = relations.get("items", [])
    bindings = [item for item in relation_items if item.get("kind") in binding_kinds]
    disruptive = [item for item in relation_items if item.get("kind") in ["branch_clash", "branch_harm", "branch_break", "wonjin", "gwimun"]]
    max_count = max(element_counts.values()) if element_counts else 0
    metal_absent = element_counts.get("金", 0) == 0

    strength = 0
    if bindings:
        strength = 1
    if len(bindings) >= 2 or (bindings and (max_count >= 3 or metal_absent)):
        strength = 2
    if len(bindings) >= 3 or (strength >= 2 and metal_absent and max_count >= 3):
        strength = 3

    transformation_items = []
    for item in bindings:
        # full 삼합/방합은 transformation candidate로만 기록. 실제 성립은 별도 조건이 필요하다.
        transformation_items.append({
            "name": item.get("name"),
            "name_ko": item.get("name_ko"),
            "element": item.get("element"),
            "transformation": False,
            "reason": "합화 4조건 검증 미완료 또는 미충족: 결속만 인정",
        })

    return {
        "bindings": [item.get("name") for item in bindings],
        "binding_items": bindings,
        "disruptive_items": disruptive,
        "transformation": False,
        "transformation_items": transformation_items,
        "BindingStrength": max(0, min(3, strength)),
        "notes": ["합화와 결속을 구분함", "현재 transformation은 보수적으로 false 처리"],
    }
