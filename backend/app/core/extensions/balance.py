from __future__ import annotations

from app.core.structure_analyzer.constants import CONTROLLER_MAP, ELEMENT_BY_BRANCH, ELEMENTS, SUPPORT_MAP
from app.core.structure_analyzer.utils import clamp, dominant_element


def calculate_balance_extension(chart: dict[str, str], stems: list[str], branches: list[str], element_counts: dict[str, int], binding: dict, climate: dict, concentration: dict) -> dict:
    dominant = concentration.get("dominant_element") or dominant_element(element_counts, chart["month"][1])
    controller = CONTROLLER_MAP[dominant]
    month_element = ELEMENT_BY_BRANCH[chart["month"][1]]

    seasonal_weight = 3 if month_element == dominant else (2 if SUPPORT_MAP[dominant] == month_element else (1 if month_element in ELEMENTS else 0))
    total = sum(element_counts.values()) or 1
    dom_count = element_counts.get(dominant, 0) + element_counts.get(SUPPORT_MAP[dominant], 0) * 0.5
    distribution_weight = clamp(round((dom_count / total) * 4), 0, 4)
    bs = binding.get("BindingStrength", 0)
    binding_boost = 0 if bs == 0 else (1 if bs == 1 else 2)
    dominant_power = clamp(seasonal_weight + distribution_weight + binding_boost, 0, 10)

    exposure = 0
    if any(stem for stem in stems if _element_of_stem(stem) == controller):
        exposure += 2
    if any(branch for branch in branches if ELEMENT_BY_BRANCH[branch] == controller):
        exposure += 2
    support_element = SUPPORT_MAP[controller]
    support_weight = clamp(element_counts.get(support_element, 0), 0, 3)
    restriction = 0
    if binding.get("BindingStrength", 0) >= 2 and element_counts.get(controller, 0) <= 1:
        restriction -= 1
    if element_counts.get(dominant, 0) >= 4 and element_counts.get(controller, 0) <= 1:
        restriction -= 2
    controller_power = clamp(exposure + support_weight + restriction, 0, 10)

    diff = abs(dominant_power - controller_power)
    if diff <= 1:
        parity = "막상막하"
        control_score = 3
    elif diff <= 3:
        parity = "근접균형"
        control_score = 2
    elif diff <= 6:
        parity = "우세뚜렷"
        control_score = 1
    else:
        parity = "압도편향"
        control_score = 0

    return {
        "dominant_element": dominant,
        "controller_element": controller,
        "DominantPower": dominant_power,
        "ControllerPower": controller_power,
        "ParityIndex": parity,
        "ControlBalanceScore": control_score,
        "notes": "보조 지표. 병/용신 강제 금지.",
        "inputs": {
            "seasonal_weight": seasonal_weight,
            "distribution_weight": distribution_weight,
            "binding_boost": binding_boost,
            "exposure_weight": exposure,
            "support_weight": support_weight,
            "restriction_penalty": restriction,
        },
    }


def _element_of_stem(stem: str) -> str:
    from app.core.structure_analyzer.constants import ELEMENT_BY_STEM

    return ELEMENT_BY_STEM[stem]
