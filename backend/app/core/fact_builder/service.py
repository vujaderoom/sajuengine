from __future__ import annotations


def build_fact(chart_payload: dict) -> dict:
    chart = chart_payload["chart"]
    month_branch = chart["month"][1]

    heat_score = 2 if month_branch in ["巳", "午", "未"] else 0
    moisture_score = -1 if month_branch in ["巳", "午"] else 0
    ewm_score = 1 if "亥" in chart["day"] else 0

    return {
        "chart": chart,
        "raw": {
            "HeatScore": heat_score,
            "MoistureScore": moisture_score,
            "EWMScore": ewm_score,
        },
        "display": {
            "HeatIndex": min(100, max(0, 50 + heat_score * 16)),
            "MoistureIndex": min(100, max(0, 50 + moisture_score * 17)),
            "EWMIndex": min(100, max(0, ewm_score * 25)),
        },
        "flow": {"blocked": True, "support_path": "weak_or_broken"},
        "binding": {"CI": 2, "BindingStrength": 3, "bindings": ["巳亥沖", "巳申合"]},
        "storage": {"root_support": 1, "base_stability": "weak"},
        "climate": {"season": chart["month"], "temperature": "hot", "humidity": "dry"},
        "notes": [
            "fact_builder scaffold v0.3.0",
            "raw score는 내부 룰용이며 display index는 UI 표시 전용",
        ],
    }
