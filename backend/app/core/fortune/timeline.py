from __future__ import annotations

from typing import Any


def _badge(grade: str) -> str:
    if grade == "supportive":
        return "우호"
    if grade == "risky":
        return "주의"
    return "혼합"


def _compact_daewoon(item: dict[str, Any]) -> dict[str, Any]:
    overlay = item.get("overlay", {})
    scores = overlay.get("scores", {})
    return {
        "type": "daewoon",
        "label": f"{item.get('age_start')}세 {item.get('pillar')}",
        "pillar": item.get("pillar"),
        "age_start": item.get("age_start"),
        "year_start": item.get("year_start"),
        "year_end": item.get("year_end"),
        "grade": scores.get("grade", "mixed"),
        "grade_ko": scores.get("grade_ko", _badge(scores.get("grade", "mixed"))),
        "net_score": scores.get("net_score", 0),
        "yongshin_score": scores.get("yongshin_score", 0),
        "gishin_score": scores.get("gishin_score", 0),
        "summary_ko": overlay.get("summary_ko", ""),
        "top_relations": [r.get("name_ko") for r in overlay.get("relations", [])[:3]],
    }


def _compact_sewoon(item: dict[str, Any]) -> dict[str, Any]:
    overlay = item.get("overlay", {})
    scores = overlay.get("scores", {})
    return {
        "type": "sewoon",
        "label": f"{item.get('year')} {item.get('pillar')}",
        "year": item.get("year"),
        "pillar": item.get("pillar"),
        "grade": scores.get("grade", "mixed"),
        "grade_ko": scores.get("grade_ko", _badge(scores.get("grade", "mixed"))),
        "net_score": scores.get("net_score", 0),
        "yongshin_score": scores.get("yongshin_score", 0),
        "gishin_score": scores.get("gishin_score", 0),
        "summary_ko": overlay.get("summary_ko", ""),
        "top_relations": [r.get("name_ko") for r in overlay.get("relations", [])[:3]],
    }


def build_fortune_timeline(overlay_result: dict[str, Any]) -> dict[str, Any]:
    daewoon = [_compact_daewoon(item) for item in overlay_result.get("daewoon", [])]
    sewoon = [_compact_sewoon(item) for item in overlay_result.get("sewoon", [])]
    combined = daewoon + sewoon
    supportive = sorted([item for item in combined if item["grade"] == "supportive"], key=lambda x: x.get("net_score", 0), reverse=True)
    risky = sorted([item for item in combined if item["grade"] == "risky"], key=lambda x: x.get("net_score", 0))
    mixed = [item for item in combined if item["grade"] == "mixed"]
    return {
        "model_version": "fortune_timeline_v1.0.0",
        "daewoon": daewoon,
        "sewoon": sewoon,
        "highlights": {
            "supportive_top": supportive[:5],
            "risky_top": risky[:5],
            "mixed_count": len(mixed),
        },
        "legend": {
            "supportive": "용신 작동 우세",
            "mixed": "용신·기신 혼합",
            "risky": "기신 자극 우세",
        },
    }
