from __future__ import annotations

from app.core.structure_analyzer.constants import ELEMENT_BY_BRANCH, ELEMENT_BY_STEM
from app.core.structure_analyzer.utils import clamp


def _pillar_elements(pillar: str) -> list[str]:
    return [ELEMENT_BY_STEM[pillar[0]], ELEMENT_BY_BRANCH[pillar[1]]]


def _climate_delta(pillar: str, delta_inputs: dict) -> dict:
    elements = _pillar_elements(pillar)
    humidity = delta_inputs.get("climate", {}).get("humidity")
    temperature = delta_inputs.get("climate", {}).get("temperature")
    delta = 0
    notes: list[str] = []
    if humidity == "과습" and "火" in elements:
        delta -= 1
        notes.append("과습 구조에 火 운: 말림·증발로 병 깊이 완화")
    if humidity == "과습" and "水" in elements:
        delta += 1
        notes.append("과습 구조에 水 운: 수습 추가로 병 깊이 증가")
    if temperature == "조열" and "水" in elements:
        delta -= 1
        notes.append("조열 구조에 水 운: 기후 완화")
    if temperature == "조열" and "火" in elements:
        delta += 1
        notes.append("조열 구조에 火 운: 과열 강화")
    return {"delta": clamp(delta, -2, 2), "notes": notes}


def _storage_delta(pillar: str, delta_inputs: dict, overlay: dict | None = None) -> dict:
    binding_strength = delta_inputs.get("binding", {}).get("BindingStrength", 0)
    relations = (overlay or {}).get("relations", [])
    delta = 0
    notes: list[str] = []
    disruptive = [r for r in relations if r.get("kind") in ["branch_clash", "branch_harm", "branch_break", "wonjin", "gwimun"]]
    supportive = [r for r in relations if r.get("kind") in ["branch_liuhe", "trine_full", "directional_full", "trine_half", "directional_half"]]
    if disruptive:
        delta += 1
        notes.append("운이 충·해·파·원진·귀문 등 저장/관계 자극을 만듦")
    if supportive and binding_strength <= 1:
        delta -= 1
        notes.append("운이 결속을 만들어 구조를 보강")
    elif supportive and binding_strength >= 2:
        delta += 0
        notes.append("운의 결속은 이미 높은 결속 구조에서는 보조지표로만 기록")
    return {"delta": clamp(delta, -2, 2), "notes": notes}


def _medicine_delta(pillar: str, delta_inputs: dict) -> dict:
    yongshin = delta_inputs.get("yongshin", {}).get("element")
    elements = _pillar_elements(pillar)
    delta = 0
    notes: list[str] = []
    if yongshin in elements:
        delta -= 1
        notes.append(f"운에 용신 {yongshin} 작동: 약·용신 자유도 개선")
    core = delta_inputs.get("diseases", {}).get("core_detail", "")
    if "수습" in core and "水" in elements:
        delta += 1
        notes.append("수습 과다 병에 水 운: 약·용신 작동을 방해")
    if "조열" in core and "火" in elements:
        delta += 1
        notes.append("조열 병에 火 운: 약·용신 작동을 방해")
    return {"delta": clamp(delta, -2, 2), "notes": notes}


def calculate_luck_delta_for_pillar(pillar: str, delta_inputs: dict, overlay: dict | None = None, scope: str = "sewoon") -> dict:
    d1 = _climate_delta(pillar, delta_inputs)
    d2 = _storage_delta(pillar, delta_inputs, overlay)
    d3 = _medicine_delta(pillar, delta_inputs)
    auxiliary = 0
    if overlay:
        scores = overlay.get("scores", {})
        if scores.get("grade") == "supportive":
            auxiliary -= 1
        elif scores.get("grade") == "risky":
            auxiliary += 1
    total = d1["delta"] + d2["delta"] + d3["delta"] + auxiliary
    if scope == "sewoon":
        total = clamp(total, -2, 2)
    base_depth = delta_inputs.get("base_depth", 1)
    final_depth = clamp(base_depth + total, 1, 4)
    return {
        "pillar": pillar,
        "scope": scope,
        "delta_1_climate": d1,
        "delta_2_storage": d2,
        "delta_3_medicine_yongshin_freedom": d3,
        "auxiliary_delta": auxiliary,
        "total_delta": total,
        "base_depth": base_depth,
        "final_depth": final_depth,
        "notes": [*d1["notes"], *d2["notes"], *d3["notes"]],
    }


def build_luck_delta_analysis(chart_result: dict, delta_inputs: dict, overlay_result: dict | None = None) -> dict:
    overlay_result = overlay_result or {}
    overlay_by_daewoon = {item.get("pillar"): item.get("overlay") for item in overlay_result.get("daewoon", [])}
    overlay_by_sewoon = {item.get("pillar"): item.get("overlay") for item in overlay_result.get("sewoon", [])}
    daewoon = [
        {**item, "luck_delta": calculate_luck_delta_for_pillar(item["pillar"], delta_inputs, overlay_by_daewoon.get(item["pillar"]), scope="daewoon")}
        for item in chart_result.get("daewoon", {}).get("cycles", [])
    ]
    sewoon = [
        {**item, "luck_delta": calculate_luck_delta_for_pillar(item["pillar"], delta_inputs, overlay_by_sewoon.get(item["pillar"]), scope="sewoon")}
        for item in chart_result.get("sewoon", {}).get("years", [])
    ]
    current_daewoon = next((item for item in daewoon if item.get("is_current")), None)
    current_sewoon = next((item for item in sewoon if item.get("is_current")), None)
    return {
        "model_version": "luck_delta_v1.0.0",
        "current": {"daewoon": current_daewoon, "sewoon": current_sewoon},
        "daewoon": daewoon,
        "sewoon": sewoon,
        "rules": ["Δ = Δ1 + Δ2 + Δ3 (+보조가중)", "세운 일반 범위는 -1~+1, 사건성 강할 경우 ±2까지 허용", "최종 병 깊이는 1~4로 클램프"],
    }
