from __future__ import annotations

from app.core.calendar.hidden_stems import HIDDEN_STEMS

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


def build_fact(chart_payload: dict) -> dict:
    chart = chart_payload["chart"]
    year_pillar = chart["year"]
    month_pillar = chart["month"]
    day_pillar = chart["day"]
    hour_pillar = chart["hour"]

    stems = [year_pillar[0], month_pillar[0], day_pillar[0], hour_pillar[0]]
    branches = [year_pillar[1], month_pillar[1], day_pillar[1], hour_pillar[1]]
    month_branch = month_pillar[1]
    day_stem = day_pillar[0]

    heat_score = 2 if month_branch in ["巳", "午", "未"] else (-2 if month_branch in ["亥", "子", "丑"] else 0)
    moisture_score = 2 if month_branch in ["亥", "子", "丑"] else (-1 if month_branch in ["巳", "午"] else 0)
    ewm_score = 1 if "亥" in branches else 0

    element_counts = _count_elements(stems, branches)
    hidden_stems = {branch: HIDDEN_STEMS[branch] for branch in branches}

    ren_present = "壬" in stems
    gui_present = "癸" in stems
    hai_present = "亥" in branches
    shen_present = "申" in branches
    wei_present = "未" in branches
    si_present = "巳" in branches
    ren_on_shen_changsheng = hour_pillar == "壬申"
    si_month = month_branch == "巳"
    warm_season = month_branch in ["巳", "午", "未"]

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
        "state": "waterlogged" if is_waterlogged else "balanced_or_unknown",
        "water_supply_score": water_supply_score,
        "continuous_water_supply": ren_on_shen_changsheng or (ren_present and shen_present),
        "needs_drying": needs_drying,
        "image": water_image if is_waterlogged else "",
    }
    soil_profile = {
        "day_stem": day_stem,
        "soil_type": "field_soil" if day_stem == "己" else "unknown",
        "field_condition": "flooded_field" if is_waterlogged else "undetermined",
        "has_wei_soil": wei_present,
    }
    source_profile = {
        "water_sources": {
            "癸": gui_present,
            "壬": ren_present,
            "亥": hai_present,
            "申": shen_present,
            "壬申_장생수원": ren_on_shen_changsheng,
        },
        "fire_sources": {
            "巳": si_present,
            "午": "午" in branches,
            "丙": "丙" in stems,
            "丁": "丁" in stems,
        },
    }
    root_profile = {
        "root_support": 1,
        "base_stability": "weak",
        "hidden_stems": hidden_stems,
    }
    flow_profile = {
        "blocked": True,
        "support_path": "weak_or_broken",
        "main_issue": "water_accumulation" if is_waterlogged else "flow_blocked",
    }
    binding_profile = {
        "CI": 2,
        "BindingStrength": 3,
        "bindings": ["巳亥沖", "巳申合"] if si_month else [],
    }
    storage_profile = {
        "root_support": root_profile["root_support"],
        "base_stability": root_profile["base_stability"],
        "storage_risk": "waterlogged_storage" if is_waterlogged else "unknown",
    }
    disease_profile = {
        "core_disease_hint": "기후형 병" if is_waterlogged else "유통 차단형 병",
        "disease_image": "수습 과다·침수형" if is_waterlogged else "유통 차단형",
        "depth_hint": 2 if is_waterlogged else 1,
    }
    medicine_need_profile = {
        "primary_action": "drying_evaporation" if needs_drying else "opening",
        "preferred_element": "火" if needs_drying else "金",
        "preferred_symbols": ["巳火", "午火", "丙火", "丁火"] if needs_drying else ["庚金"],
        "medicine_type": "기후 복원형" if needs_drying else "유통 개통형",
        "not_about": ["cold_recovery", "temperature_recovery"] if needs_drying else [],
    }

    return {
        "chart": chart,
        "stems": stems,
        "branches": branches,
        "elements": element_counts,
        "hidden_stems": hidden_stems,
        "raw": {
            "HeatScore": heat_score,
            "MoistureScore": moisture_score,
            "EWMScore": ewm_score,
            "WaterSupplyScore": water_supply_score,
            "Depth": disease_profile["depth_hint"],
        },
        "display": {
            "HeatIndex": min(100, max(0, 50 + heat_score * 16)),
            "MoistureIndex": min(100, max(0, 50 + moisture_score * 17)),
            "EWMIndex": min(100, max(0, ewm_score * 25)),
            "WaterSupplyIndex": min(100, max(0, water_supply_score * 14)),
        },
        "season_profile": season_profile,
        "temperature_profile": temperature_profile,
        "moisture_profile": moisture_profile,
        "soil_profile": soil_profile,
        "root_profile": root_profile,
        "source_profile": source_profile,
        "flow_profile": flow_profile,
        "binding_profile": binding_profile,
        "storage_profile": storage_profile,
        "disease_profile": disease_profile,
        "medicine_need_profile": medicine_need_profile,
        "flow": flow_profile,
        "binding": binding_profile,
        "storage": storage_profile,
        "climate": {
            "season": month_pillar,
            "month_branch": month_branch,
            "warm_season": warm_season,
            "temperature_state": temperature_profile["state"],
            "humidity": moisture_profile["state"],
            "needs_drying": needs_drying,
            "needs_temperature_recovery": False,
        },
        "water": {
            "ren_present": ren_present,
            "gui_present": gui_present,
            "hai_present": hai_present,
            "shen_present": shen_present,
            "ren_on_shen_changsheng": ren_on_shen_changsheng,
            "water_supply_score": water_supply_score,
            "is_waterlogged": is_waterlogged,
            "needs_drying": needs_drying,
            "image": water_image if is_waterlogged else "",
        },
        "medicine_need": medicine_need_profile,
        "delta_inputs": {
            "climate": {"HeatScore": heat_score, "MoistureScore": moisture_score, "EWMScore": ewm_score},
            "storage": storage_profile,
            "medicine_freedom": {"freedom": "작동" if needs_drying else "제한"},
            "extension": {},
        },
        "notes": [
            "fact_builder v2.0.0",
            "raw score는 내부 룰용이며 display index는 UI 표시 전용",
            "巳月의 기본 온기는 인정하되, 火는 온도 회복이 아니라 말림·건조·증발로 작동",
        ],
    }
