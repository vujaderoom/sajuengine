from __future__ import annotations


def build_fact(chart_payload: dict) -> dict:
    chart = chart_payload["chart"]
    year_pillar = chart["year"]
    month_pillar = chart["month"]
    day_pillar = chart["day"]
    hour_pillar = chart["hour"]

    stems = [year_pillar[0], month_pillar[0], day_pillar[0], hour_pillar[0]]
    branches = [year_pillar[1], month_pillar[1], day_pillar[1], hour_pillar[1]]
    month_branch = month_pillar[1]

    heat_score = 2 if month_branch in ["巳", "午", "未"] else 0
    moisture_score = -1 if month_branch in ["巳", "午"] else 0
    ewm_score = 1 if "亥" in branches else 0

    ren_present = "壬" in stems
    gui_present = "癸" in stems
    hai_present = "亥" in branches
    shen_present = "申" in branches
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

    is_waterlogged = si_month and water_supply_score >= 5
    needs_drying = is_waterlogged

    return {
        "chart": chart,
        "raw": {
            "HeatScore": heat_score,
            "MoistureScore": moisture_score,
            "EWMScore": ewm_score,
            "WaterSupplyScore": water_supply_score,
        },
        "display": {
            "HeatIndex": min(100, max(0, 50 + heat_score * 16)),
            "MoistureIndex": min(100, max(0, 50 + moisture_score * 17)),
            "EWMIndex": min(100, max(0, ewm_score * 25)),
            "WaterSupplyIndex": min(100, max(0, water_supply_score * 14)),
        },
        "flow": {"blocked": True, "support_path": "weak_or_broken"},
        "binding": {"CI": 2, "BindingStrength": 3, "bindings": ["巳亥沖", "巳申合"]},
        "storage": {"root_support": 1, "base_stability": "weak"},
        "climate": {
            "season": month_pillar,
            "month_branch": month_branch,
            "warm_season": warm_season,
            "temperature_state": "warm_rain" if is_waterlogged else ("warm" if warm_season else "neutral"),
            "humidity": "waterlogged" if is_waterlogged else "dry",
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
            "image": "巳月의 따뜻한 계절에 癸水·壬水·亥水·申金 수원이 이어져 여름비가 논을 잠기게 하는 물상",
        },
        "medicine_need": {
            "primary_action": "drying_evaporation" if needs_drying else "opening",
            "preferred_element": "火" if needs_drying else "金",
            "preferred_symbols": ["巳火", "午火", "丙火", "丁火"] if needs_drying else ["庚金"],
            "not_about": ["cold_recovery", "temperature_recovery"] if needs_drying else [],
        },
        "notes": [
            "fact_builder scaffold v0.4.1",
            "raw score는 내부 룰용이며 display index는 UI 표시 전용",
            "巳月의 기본 온기는 인정하되, 火는 온도 회복이 아니라 말림·건조·증발로 작동",
        ],
    }
