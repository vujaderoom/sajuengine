from __future__ import annotations

from app.core.calendar.hidden_stems import HIDDEN_STEMS
from app.core.structure_analyzer.service import analyze_structure

ELEMENT_BY_STEM = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}

ELEMENT_BY_BRANCH = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}


def _count_elements(stems: list[str], branches: list[str]) -> dict[str, int]:
    counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for stem in stems:
        counts[ELEMENT_BY_STEM[stem]] += 1
    for branch in branches:
        counts[ELEMENT_BY_BRANCH[branch]] += 1
    return counts


def _legacy_waterlogged_overlay(chart: dict, stems: list[str], branches: list[str], relations: dict, structure: dict) -> dict:
    month_pillar = chart["month"]
    day_pillar = chart["day"]
    hour_pillar = chart["hour"]
    month_branch = month_pillar[1]
    day_stem = day_pillar[0]
    warm_season = month_branch in ["巳", "午", "未"]
    ren_present = "壬" in stems
    gui_present = "癸" in stems
    hai_present = "亥" in branches
    shen_present = "申" in branches
    wei_present = "未" in branches
    si_present = "巳" in branches
    ren_on_shen_changsheng = hour_pillar == "壬申"
    si_month = month_branch == "巳"

    relation_names = [item.get("name", "") for item in relations.get("items", [])]
    has_si_hai_clash = "巳亥沖" in relation_names
    has_si_shen_liuhe = "巳申合" in relation_names
    has_shen_hai_harm = "申亥害" in relation_names

    water_supply_score = 0
    if ren_present:
        water_supply_score += 2
    if gui_present:
        water_supply_score += 1
    if hai_present:
        water_supply_score += 2
    if shen_present:
        water_supply_score += 1
    if ren_on_shen_changsheng:
        water_supply_score += 2

    is_waterlogged = si_month and day_stem == "己" and water_supply_score >= 5
    needs_drying = is_waterlogged
    water_image = "巳月의 따뜻한 계절에 癸水·壬水·亥水·申金 수원이 이어져 여름비가 논을 잠기게 하는 물상"
    hidden_stems = {branch: HIDDEN_STEMS[branch] for branch in branches}
    element_counts = _count_elements(stems, branches)

    season_profile = {
        "month_pillar": month_pillar,
        "month_branch": month_branch,
        "season_group": "summer" if warm_season else "other",
        "warm_season": warm_season,
        "monthly_command_element": ELEMENT_BY_BRANCH[month_branch],
    }
    temperature_profile = {
        "state": "warm_rain" if is_waterlogged else ("warm" if warm_season else "neutral"),
        "needs_temperature_recovery": False,
        "heat_is_present": warm_season,
        "notes": ["巳月·未土의 온기는 인정", "문제는 한랭이 아니라 따뜻한 비로 인한 침수"] if is_waterlogged else [],
    }
    moisture_profile = {
        "state": "waterlogged" if is_waterlogged else ("waterlogged_by_l2" if structure["climate"]["MoistureScore"] >= 2 else "balanced_or_unknown"),
        "water_supply_score": water_supply_score,
        "continuous_water_supply": ren_on_shen_changsheng or (ren_present and shen_present),
        "needs_drying": needs_drying or structure["DeltaInputs"]["yongshin"].get("element") == "火",
        "image": water_image if is_waterlogged else "",
    }
    relation_binding_names = [item.get("name") for item in relations.get("items", []) if item.get("kind") in ["branch_clash", "branch_liuhe", "branch_harm", "branch_break", "wonjin", "gwimun", "trine_half", "trine_full", "directional_half", "directional_full"]]
    binding_profile = {
        "CI": structure["concentration"]["CI"],
        "BindingStrength": structure["binding"]["BindingStrength"],
        "bindings": structure["binding"]["bindings"],
        "legacy_relation_bindings": relation_binding_names,
        "has_si_hai_clash": has_si_hai_clash,
        "has_si_shen_liuhe": has_si_shen_liuhe,
        "has_shen_hai_harm": has_shen_hai_harm,
    }
    storage_profile = {
        "root_support": 1,
        "base_stability": "weak",
        "storage_risk": "waterlogged_storage" if is_waterlogged else "unknown",
        "BindingStrength": structure["binding"]["BindingStrength"],
    }
    disease_profile = {
        "core_disease_hint": "기후형 병" if is_waterlogged else structure["disease"]["core_detail"],
        "disease_image": "수습 과다·침수형" if is_waterlogged else structure["disease"]["core_detail"],
        "depth_hint": structure["disease"]["Depth"],
        "DepthScore": structure["disease"]["DepthScore"],
    }
    medicine_need_profile = {
        "primary_action": "drying_evaporation" if needs_drying else structure["DeltaInputs"]["medicines"][0].get("action"),
        "preferred_element": "火" if needs_drying else structure["DeltaInputs"]["yongshin"].get("element"),
        "preferred_symbols": ["巳火", "午火", "丙火", "丁火"] if needs_drying else structure["DeltaInputs"]["yongshin"].get("secondary", []),
        "medicine_type": "기후 복원형" if needs_drying else structure["DeltaInputs"]["medicines"][0].get("type"),
        "not_about": ["cold_recovery", "temperature_recovery"] if needs_drying else [],
    }

    return {
        "element_counts": element_counts,
        "hidden_stems": hidden_stems,
        "water_supply_score": water_supply_score,
        "is_waterlogged": is_waterlogged,
        "needs_drying": needs_drying,
        "water_image": water_image,
        "season_profile": season_profile,
        "temperature_profile": temperature_profile,
        "moisture_profile": moisture_profile,
        "soil_profile": {"day_stem": day_stem, "soil_type": "field_soil" if day_stem == "己" else "unknown", "field_condition": "flooded_field" if is_waterlogged else "undetermined", "has_wei_soil": wei_present},
        "source_profile": {
            "water_sources": {"癸": gui_present, "壬": ren_present, "亥": hai_present, "申": shen_present, "壬申_장생수원": ren_on_shen_changsheng},
            "fire_sources": {"巳": si_present, "午": "午" in branches, "丙": "丙" in stems, "丁": "丁" in stems},
        },
        "root_profile": {"root_support": 1, "base_stability": "weak", "hidden_stems": hidden_stems},
        "flow_profile": {"blocked": relations.get("summary", {}).get("has_clash", False), "support_path": "weak_or_broken" if relations.get("summary", {}).get("has_clash", False) else "unknown", "main_issue": "water_accumulation" if is_waterlogged else "flow_blocked", "relations": relations},
        "binding_profile": binding_profile,
        "storage_profile": storage_profile,
        "disease_profile": disease_profile,
        "medicine_need_profile": medicine_need_profile,
    }


def build_fact(chart_payload: dict) -> dict:
    chart = chart_payload["chart"]
    relations = chart_payload.get("relations", {"items": [], "summary": {}, "by_kind": {}})
    year_pillar = chart["year"]
    month_pillar = chart["month"]
    day_pillar = chart["day"]
    hour_pillar = chart["hour"]
    stems = [year_pillar[0], month_pillar[0], day_pillar[0], hour_pillar[0]]
    branches = [year_pillar[1], month_pillar[1], day_pillar[1], hour_pillar[1]]
    structure = analyze_structure(chart_payload)
    legacy = _legacy_waterlogged_overlay(chart, stems, branches, relations, structure)
    delta_inputs = structure["DeltaInputs"]

    if legacy["is_waterlogged"]:
        delta_inputs = {
            **delta_inputs,
            "base_depth": max(delta_inputs["base_depth"], 2),
            "climate": {**delta_inputs["climate"], "MoistureScore": max(delta_inputs["climate"]["MoistureScore"], 2), "humidity": "과습", "tags": list(dict.fromkeys(delta_inputs["climate"].get("tags", []) + ["warm_rain_waterlogged"]))},
            "diseases": {**delta_inputs["diseases"], "core": "기후형", "core_detail": "기후형(수습 과다·침수)", "derived": list(dict.fromkeys(delta_inputs["diseases"].get("derived", []) + ["유통 차단형"]))},
            "medicines": [{"type": "기후 복원형", "grade": "A", "freedom": "작동", "name": "말림·건조·증발", "action": "drying_evaporation"}],
            "yongshin": {"element": "火", "validation_passed": True, "secondary": ["巳火", "午火", "丙火", "丁火"]},
        }
        structure["DeltaInputs"] = delta_inputs

    heat_score = delta_inputs["climate"]["HeatScore"]
    moisture_score = delta_inputs["climate"]["MoistureScore"]
    ewm_score = delta_inputs["climate"]["EWMScore"]
    water_supply_score = legacy["water_supply_score"]

    return {
        "chart": chart,
        "stems": stems,
        "branches": branches,
        "elements": legacy["element_counts"],
        "element_balance": legacy["element_counts"],
        "hidden_stems": legacy["hidden_stems"],
        "relations": relations,
        "structure_analyzer": structure,
        "DeltaInputs": delta_inputs,
        "raw": {"HeatScore": heat_score, "MoistureScore": moisture_score, "EWMScore": ewm_score, "WaterSupplyScore": water_supply_score, "Depth": delta_inputs["base_depth"], "DepthScore": delta_inputs["diseases"].get("DepthScore")},
        "display": {"HeatIndex": min(100, max(0, 50 + heat_score * 16)), "MoistureIndex": min(100, max(0, 50 + moisture_score * 17)), "EWMIndex": min(100, max(0, ewm_score * 25)), "WaterSupplyIndex": min(100, max(0, water_supply_score * 14)), "CIIndex": min(100, max(0, delta_inputs["concentration"]["CI"] * 20))},
        "season_profile": legacy["season_profile"],
        "temperature_profile": legacy["temperature_profile"],
        "moisture_profile": legacy["moisture_profile"],
        "soil_profile": legacy["soil_profile"],
        "root_profile": legacy["root_profile"],
        "source_profile": legacy["source_profile"],
        "flow_profile": legacy["flow_profile"],
        "binding_profile": legacy["binding_profile"],
        "concentration_profile": delta_inputs["concentration"],
        "storage_profile": legacy["storage_profile"],
        "disease_profile": legacy["disease_profile"],
        "medicine_need_profile": legacy["medicine_need_profile"],
        "flow": legacy["flow_profile"],
        "binding": legacy["binding_profile"],
        "storage": legacy["storage_profile"],
        "climate": {"season": month_pillar, "month_branch": month_pillar[1], "warm_season": month_pillar[1] in ["巳", "午", "未"], "temperature_state": legacy["temperature_profile"]["state"], "humidity": legacy["moisture_profile"]["state"], "needs_drying": legacy["needs_drying"], "needs_temperature_recovery": False},
        "water": {"ren_present": "壬" in stems, "gui_present": "癸" in stems, "hai_present": "亥" in branches, "shen_present": "申" in branches, "ren_on_shen_changsheng": hour_pillar == "壬申", "water_supply_score": water_supply_score, "is_waterlogged": legacy["is_waterlogged"], "needs_drying": legacy["needs_drying"], "image": legacy["water_image"] if legacy["is_waterlogged"] else ""},
        "medicine_need": legacy["medicine_need_profile"],
        "delta_inputs": delta_inputs,
        "notes": ["fact_builder v3.0.0", "L2 structure_analyzer 기반 DeltaInputs 표준화", "ext_balance는 DeltaInputs.extension.balance 하위 보조 지표", "巳月의 기본 온기는 인정하되, 火는 온도 회복이 아니라 말림·건조·증발로 작동"],
    }
