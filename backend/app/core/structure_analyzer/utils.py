from __future__ import annotations

from app.core.structure_analyzer.constants import ELEMENT_BY_BRANCH, ELEMENT_BY_STEM, ELEMENTS


def clamp(value: int | float, low: int, high: int) -> int:
    return int(max(low, min(high, value)))


def chart_parts(chart: dict[str, str]) -> tuple[list[str], list[str]]:
    stems = [chart[key][0] for key in ["year", "month", "day", "hour"]]
    branches = [chart[key][1] for key in ["year", "month", "day", "hour"]]
    return stems, branches


def count_elements(stems: list[str], branches: list[str]) -> dict[str, int]:
    counts = {element: 0 for element in ELEMENTS}
    for stem in stems:
        counts[ELEMENT_BY_STEM[stem]] += 1
    for branch in branches:
        counts[ELEMENT_BY_BRANCH[branch]] += 1
    return counts


def temperature_label(score: int) -> str:
    if score <= -2:
        return "한랭"
    if score >= 2:
        return "조열"
    return "적정"


def humidity_label(score: int) -> str:
    if score <= -2:
        return "건조"
    if score >= 2:
        return "과습"
    return "적정"


def dominant_element(element_counts: dict[str, int], month_branch: str) -> str:
    max_count = max(element_counts.values()) if element_counts else 0
    winners = [element for element, count in element_counts.items() if count == max_count]
    month_element = ELEMENT_BY_BRANCH[month_branch]
    if month_element in winners:
        return month_element
    return winners[0] if winners else month_element
