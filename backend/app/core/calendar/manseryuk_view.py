from __future__ import annotations

from app.core.calendar.display_labels import TEN_GOD_KO, branch_to_ko, stem_to_ko, UNSEONG_KO
from app.core.calendar.hidden_stems import hidden_stems_for_chart
from app.core.calendar.ten_gods import ten_god
from app.core.calendar.twelve_unseong import twelve_unseong
from app.core.calendar.xunkong import xunkong_for_chart

ORDER = ["hour", "day", "month", "year"]
PILLAR_LABELS = {"year": "년주", "month": "월주", "day": "일주", "hour": "시주"}


def _main_hidden_stem(hidden_stems: list[str]) -> str:
    return hidden_stems[-1]


def _hidden_stem_items(day_stem: str, stems: list[str]) -> list[dict]:
    return [
        {
            "stem": stem,
            "stem_ko": stem_to_ko(stem),
            "ten_god": ten_god(day_stem, stem),
            "ten_god_ko": TEN_GOD_KO.get(ten_god(day_stem, stem), ten_god(day_stem, stem)),
        }
        for stem in stems
    ]


def _relative_xunkong_label(key: str, branch: str, year_xunkong: list[str], day_xunkong: list[str]) -> dict:
    if key == "day":
        is_void = branch in year_xunkong
        return {
            "base": "year",
            "base_label": "년공망",
            "void_branches": year_xunkong,
            "void_branches_ko": [branch_to_ko(item) for item in year_xunkong],
            "is_void": is_void,
            "display": "[年]공망" if is_void else "-",
            "display_ko": "[년]공망" if is_void else "-",
        }
    is_void = branch in day_xunkong
    return {
        "base": "day",
        "base_label": "일공망",
        "void_branches": day_xunkong,
        "void_branches_ko": [branch_to_ko(item) for item in day_xunkong],
        "is_void": is_void,
        "display": "[日]공망" if is_void else "-",
        "display_ko": "[일]공망" if is_void else "-",
    }


def build_manseryuk_view(chart_result: dict) -> dict:
    chart = chart_result["chart"]
    day_stem = chart["day"][0]
    hidden_stems = hidden_stems_for_chart(chart)
    xunkong = xunkong_for_chart(chart)
    year_xunkong = xunkong["year"]
    day_xunkong = xunkong["day"]
    display_ko = chart_result.get("display_ko", {})

    pillars = []
    for key in ORDER:
        pillar = chart[key]
        stem = pillar[0]
        branch = pillar[1]
        hs = hidden_stems[key]
        branch_main_stem = _main_hidden_stem(hs)
        branch_ten_god = ten_god(day_stem, branch_main_stem)
        pillar_stem_unseong = twelve_unseong(stem, branch)
        pillars.append(
            {
                "key": key,
                "label": PILLAR_LABELS[key],
                "pillar": pillar,
                "stem": stem,
                "stem_ko": stem_to_ko(stem),
                "branch": branch,
                "branch_ko": branch_to_ko(branch),
                "stem_ten_god": "日干" if key == "day" else chart_result["ten_gods"][key],
                "stem_ten_god_ko": "일간(나)" if key == "day" else display_ko["ten_gods"][key],
                "branch_ten_god": branch_ten_god,
                "branch_ten_god_ko": TEN_GOD_KO.get(branch_ten_god, branch_ten_god),
                "hidden_stems": _hidden_stem_items(day_stem, hs),
                "twelve_unseong": chart_result["twelve_unseong"][key],
                "twelve_unseong_ko": display_ko["twelve_unseong"][key],
                "pillar_stem_twelve_unseong": pillar_stem_unseong,
                "pillar_stem_twelve_unseong_ko": UNSEONG_KO.get(pillar_stem_unseong, pillar_stem_unseong),
                "twelve_shinsal_year_base": chart_result["twelve_shinsal"]["year_base"][key],
                "twelve_shinsal_year_base_ko": display_ko["twelve_shinsal"]["year_base"][key],
                "xunkong": xunkong[key],
                "xunkong_ko": [branch_to_ko(branch) for branch in xunkong[key]],
                "relative_xunkong": _relative_xunkong_label(key, branch, year_xunkong, day_xunkong),
            }
        )

    return {
        "order": ORDER,
        "pillars": pillars,
        "xunkong_by_pillar": xunkong,
        "relative_xunkong_rule": "day pillar checks year-xunkong; year/month/hour pillars check day-xunkong",
        "year_xunkong": year_xunkong,
        "year_xunkong_ko": [branch_to_ko(branch) for branch in year_xunkong],
        "day_xunkong": day_xunkong,
        "day_xunkong_ko": [branch_to_ko(branch) for branch in day_xunkong],
        "default_shinsal_base": "year_base",
    }
