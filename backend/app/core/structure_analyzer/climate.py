from __future__ import annotations

from app.core.structure_analyzer.constants import ELEMENT_BY_BRANCH, MONTH_BASE_CLIMATE
from app.core.structure_analyzer.utils import clamp, humidity_label, temperature_label


def calculate_ewm(stems: list[str], branches: list[str], relations: dict) -> dict:
    score = 0
    reasons: list[str] = []
    if any(stem in ["壬", "癸"] for stem in stems):
        score += 1
        reasons.append("천간 수 투출")
    if any(stem in ["庚", "辛"] for stem in stems) and any(branch in ["亥", "子"] for branch in branches):
        score += 1
        reasons.append("금 생수 유통")
    water_bound = any(item.get("element") in ["木", "火"] and any(x in ["亥", "子"] for x in item.get("items", [])) for item in relations.get("items", []))
    if not water_bound and any(branch in ["亥", "子"] for branch in branches):
        score += 1
        reasons.append("수가 강하게 묶이지 않음")
    fire_soil_surround = len([b for b in branches if b in ["巳", "午", "未", "戌"]]) >= 3
    if not fire_soil_surround:
        score += 1
        reasons.append("화토 포위 증발이 지배적이지 않음")
    return {"EWMScore": clamp(score, 0, 4), "reasons": reasons, "water_bound": water_bound, "fire_soil_surround": fire_soil_surround}


def calculate_climate(chart: dict[str, str], stems: list[str], branches: list[str], relations: dict, element_counts: dict[str, int]) -> dict:
    month_branch = chart["month"][1]
    base = MONTH_BASE_CLIMATE.get(month_branch, {"HeatScore": 0, "MoistureScore": 0})
    heat = base["HeatScore"]
    moisture = base["MoistureScore"]
    heat_reasons = [f"월령 {month_branch} 기본 HeatScore {heat}"]
    moisture_reasons = [f"월령 {month_branch} 기본 MoistureScore {moisture}"]

    if any(stem in ["丙", "丁"] for stem in stems):
        heat += 1
        heat_reasons.append("천간 화 투출 +1")
    if any(branch in ["巳", "午"] for branch in branches):
        heat += 1
        heat_reasons.append("지지 巳/午 존재 +1")
    if any(item.get("element") == "火" for item in relations.get("items", [])):
        heat += 1
        heat_reasons.append("火 결속/합 구조 +1")
    if element_counts.get("火", 0) + element_counts.get("土", 0) >= 5:
        heat += 1
        heat_reasons.append("화토 편중 건조화 +1")

    if any(stem in ["壬", "癸"] for stem in stems):
        heat -= 1
        heat_reasons.append("천간 수 투출 -1")
    if any(stem in ["庚", "辛"] for stem in stems) and any(branch in ["亥", "子"] for branch in branches):
        heat -= 1
        heat_reasons.append("금 생수 유통 -1")
    if month_branch in ["亥", "子"] and len([x for x in stems + branches if x in ["壬", "癸", "亥", "子"]]) >= 2:
        heat -= 1
        heat_reasons.append("수 월령+추가 수 -1")

    if month_branch in ["亥", "子"]:
        moisture += 1
        moisture_reasons.append("월지 수왕 +1")
    if any(x in stems + branches for x in ["壬", "癸", "亥", "子"]):
        moisture += 1
        moisture_reasons.append("수 추가 존재 +1")
    if any(branch in ["辰", "丑"] for branch in branches):
        moisture += 1
        moisture_reasons.append("습토 저장고 辰/丑 +1")
    if element_counts.get("火", 0) + element_counts.get("土", 0) >= 5:
        moisture -= 1
        moisture_reasons.append("화토 결집 증발/건조 -1")

    ewm = calculate_ewm(stems, branches, relations)
    if ewm["EWMScore"] <= 1:
        moisture -= 1
        moisture_reasons.append("EWM 0~1 유효 수분 부재 -1")
    elif ewm["EWMScore"] >= 3:
        heat -= 1
        heat_reasons.append("EWM 3~4 냉각 능력 -1")

    tags: list[str] = []
    dry_winter = False
    if month_branch in ["亥", "子", "丑"]:
        heat_boost = any(branch in ["巳", "午"] for branch in branches) or any(stem in ["丙", "丁"] for stem in stems)
        evap = any(item.get("element") == "火" for item in relations.get("items", [])) or element_counts.get("火", 0) + element_counts.get("土", 0) >= 5 or element_counts.get("金", 0) == 0
        if heat_boost and evap and ewm["EWMScore"] <= 1:
            dry_winter = True
            moisture = min(moisture, -2)
            tags += ["dry_winter", "effective_moisture_absent"]
            moisture_reasons.append("DryWinter override: 증발형 건조 우선")

    heat = clamp(heat, -3, 3)
    moisture = clamp(moisture, -3, 3)
    return {
        "HeatScore": heat,
        "MoistureScore": moisture,
        "EWMScore": ewm["EWMScore"],
        "temperature": temperature_label(heat),
        "humidity": humidity_label(moisture),
        "tags": tags,
        "base": base,
        "ewm": ewm,
        "dry_winter": dry_winter,
        "reasons": {"heat": heat_reasons, "moisture": moisture_reasons, "ewm": ewm["reasons"]},
    }
