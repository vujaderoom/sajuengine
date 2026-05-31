from __future__ import annotations

from app.core.structure_analyzer.constants import ELEMENT_BY_BRANCH
from app.core.structure_analyzer.utils import clamp, dominant_element


def calculate_concentration(chart: dict[str, str], element_counts: dict[str, int], binding: dict) -> dict:
    month_branch = chart["month"][1]
    dominant = dominant_element(element_counts, month_branch)
    max_count = element_counts.get(dominant, 0)
    score = 0
    reasons: list[str] = []
    if max_count >= 4:
        score += 3
        reasons.append("최다 오행 4개 이상 +3")
    elif max_count == 3:
        score += 2
        reasons.append("최다 오행 3개 +2")
    elif max_count == 2:
        score += 1
        reasons.append("최다 오행 2개 +1")

    metal_absent = element_counts.get("金", 0) == 0
    if metal_absent:
        score += 1
        reasons.append("금 부재 +1")
    if binding.get("BindingStrength", 0) >= 2:
        score += 1
        reasons.append("BindingStrength 2 이상 +1")

    month_element = ELEMENT_BY_BRANCH[month_branch]
    month_isolated = element_counts.get(month_element, 0) <= 1 and binding.get("BindingStrength", 0) >= 2
    if month_isolated:
        score += 1
        reasons.append("월지 고립 구조 +1")

    ci = clamp(score, 0, 5)
    level = "낮음" if ci <= 1 else ("중간" if ci <= 3 else "강함")
    return {
        "CI": ci,
        "level": level,
        "dominant_element": dominant,
        "dominant_count": max_count,
        "metal_absent": metal_absent,
        "month_isolated": month_isolated,
        "reasons": reasons,
    }
