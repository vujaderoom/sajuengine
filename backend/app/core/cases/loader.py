from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def golden_cases_dir() -> Path:
    return _repo_root() / "golden_cases"


def _pillar_text(chart: dict[str, Any] | None) -> str:
    if not chart:
        return ""
    parts = [chart.get("year"), chart.get("month"), chart.get("day"), chart.get("hour")]
    return " ".join([str(part) for part in parts if part])


def _extract_interpretation_summary(case: dict[str, Any]) -> dict[str, Any]:
    expected = case.get("expected", {}) or {}
    interpretation = case.get("interpretation", {}) or {}
    final_result = expected.get("final_result", {}) or {}
    facts = expected.get("facts", {}) or {}
    water = facts.get("water", {}) or {}
    medicine_need = facts.get("medicine_need", {}) or {}
    disease_logic = interpretation.get("disease_logic", {}) or {}
    medicine_logic = interpretation.get("medicine_logic", {}) or {}
    yongshin_logic = interpretation.get("yongshin_logic", {}) or {}

    return {
        "core_disease": disease_logic.get("core") or final_result.get("core_disease"),
        "subtype": disease_logic.get("subtype"),
        "derived_diseases": final_result.get("derived_diseases", []),
        "medicine": final_result.get("medicine") or medicine_logic.get("action"),
        "medicine_type": medicine_logic.get("type"),
        "yongshin": final_result.get("yongshin") or yongshin_logic.get("primary"),
        "yongshin_symbols": final_result.get("yongshin_symbols", []) or yongshin_logic.get("symbols", []),
        "selected_yongshin_source_rule": final_result.get("selected_yongshin_source_rule"),
        "water_is_waterlogged": water.get("is_waterlogged"),
        "water_needs_drying": water.get("needs_drying"),
        "preferred_element": medicine_need.get("preferred_element"),
        "primary_action": medicine_need.get("primary_action"),
        "linked_rules": interpretation.get("linked_rules", []),
        "excluded": yongshin_logic.get("excluded", []),
    }


def load_cases() -> list[dict[str, Any]]:
    base = golden_cases_dir()
    if not base.exists():
        return []

    cases: list[dict[str, Any]] = []
    for path in sorted(base.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        data["_path"] = str(path.relative_to(_repo_root()))
        data["_raw_yaml"] = path.read_text(encoding="utf-8")
        cases.append(data)
    return cases


def summarize_cases() -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for case in load_cases():
        expected = case.get("expected", {}) or {}
        chart = expected.get("chart", {}) or {}
        birth = case.get("birth", {}) or {}
        summaries.append(
            {
                "id": case.get("id"),
                "title": case.get("title"),
                "status": case.get("status"),
                "version": case.get("version"),
                "path": case.get("_path"),
                "birth": birth,
                "chart": chart,
                "pillar_text": _pillar_text(chart),
                "interpretation": case.get("interpretation", {}),
                "interpretation_summary": _extract_interpretation_summary(case),
                "notes": case.get("notes", []),
            }
        )
    return summaries


def get_case(case_id: str) -> dict[str, Any] | None:
    for case in load_cases():
        if case.get("id") == case_id:
            expected = case.get("expected", {}) or {}
            chart = expected.get("chart", {}) or {}
            return {
                "id": case.get("id"),
                "title": case.get("title"),
                "status": case.get("status"),
                "version": case.get("version"),
                "path": case.get("_path"),
                "birth": case.get("birth", {}),
                "chart": chart,
                "pillar_text": _pillar_text(chart),
                "expected": expected,
                "interpretation": case.get("interpretation", {}),
                "interpretation_summary": _extract_interpretation_summary(case),
                "notes": case.get("notes", []),
                "raw_yaml": case.get("_raw_yaml", ""),
            }
    return None
