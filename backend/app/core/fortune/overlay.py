from __future__ import annotations

from itertools import combinations
from typing import Any

from app.core.calendar.relations import (
    BRANCH_BREAKS,
    BRANCH_CLASHES,
    BRANCH_GWIMUN,
    BRANCH_HARMS,
    BRANCH_LIUHE,
    BRANCH_WONJIN,
    DIRECTIONAL,
    STEM_COMBOS,
    TRINES,
)
from app.core.fortune.analysis import ELEMENT_BY_BRANCH, ELEMENT_BY_STEM, ELEMENT_KO

ORIGIN_ORDER = ["year", "month", "day", "hour"]
ORIGIN_LABELS = {"year": "년주", "month": "월주", "day": "일주", "hour": "시주"}
LUCK_LABELS = {"daewoon": "대운", "sewoon": "세운"}

SUPPORTIVE_KINDS = {"branch_liuhe", "stem_combo", "trine_full", "directional_full", "trine_half", "directional_half"}
RISK_KINDS = {"branch_clash", "branch_harm", "branch_break", "wonjin", "gwimun"}


def _origin_items(chart: dict[str, str]) -> list[dict[str, str]]:
    return [
        {"position": key, "label": ORIGIN_LABELS[key], "pillar": chart[key], "stem": chart[key][0], "branch": chart[key][1], "source": "origin"}
        for key in ORIGIN_ORDER
    ]


def _luck_item(kind: str, pillar: str, extra: dict | None = None) -> dict[str, Any]:
    return {"position": kind, "label": LUCK_LABELS[kind], "pillar": pillar, "stem": pillar[0], "branch": pillar[1], "source": kind, **(extra or {})}


def _relation(kind: str, kind_ko: str, name: str, name_ko: str, positions: list[dict], items: list[str], **extra: Any) -> dict[str, Any]:
    luck_positions = [p for p in positions if p.get("source") != "origin"]
    return {
        "kind": kind,
        "kind_ko": kind_ko,
        "name": name,
        "name_ko": name_ko,
        "positions": positions,
        "items": items,
        "luck_involved": bool(luck_positions),
        "luck_positions": luck_positions,
        **extra,
    }


def _pair_relations(items: list[dict]) -> list[dict]:
    relations: list[dict] = []
    for a, b in combinations(items, 2):
        stem_meta = STEM_COMBOS.get(frozenset([a["stem"], b["stem"]]))
        if stem_meta:
            relations.append(_relation("stem_combo", "천간합", stem_meta["name"], stem_meta["name_ko"], [a, b], [a["stem"], b["stem"]], element=stem_meta["element"], element_ko=stem_meta["element_ko"]))

        pair = frozenset([a["branch"], b["branch"]])
        pair_tables = [
            ("branch_clash", "지지충", BRANCH_CLASHES, False),
            ("branch_liuhe", "육합", BRANCH_LIUHE, True),
            ("branch_harm", "해", BRANCH_HARMS, False),
            ("branch_break", "파", BRANCH_BREAKS, False),
            ("wonjin", "원진", BRANCH_WONJIN, False),
            ("gwimun", "귀문", BRANCH_GWIMUN, False),
        ]
        for kind, kind_ko, table, has_element in pair_tables:
            meta = table.get(pair)
            if not meta:
                continue
            if has_element:
                name, name_ko, element, element_ko = meta
                relations.append(_relation(kind, kind_ko, name, name_ko, [a, b], [a["branch"], b["branch"]], element=element, element_ko=element_ko))
            else:
                name, name_ko = meta
                relations.append(_relation(kind, kind_ko, name, name_ko, [a, b], [a["branch"], b["branch"]]))
    return relations


def _set_relations(items: list[dict]) -> list[dict]:
    relations: list[dict] = []
    branch_set = {item["branch"] for item in items}
    for trine in TRINES:
        present = sorted(list(trine["branches"] & branch_set))
        if len(present) >= 2:
            positions = [item for item in items if item["branch"] in present]
            kind = "trine_full" if len(present) == 3 else "trine_half"
            kind_ko = "삼합" if len(present) == 3 else "반합"
            name = trine["name"] if len(present) == 3 else trine["name"].replace("三合", "半合")
            name_ko = trine["name_ko"] if len(present) == 3 else trine["name_ko"].replace("삼합", "반합")
            relations.append(_relation(kind, kind_ko, name, name_ko, positions, present, element=trine["element"], element_ko=trine["element_ko"], completeness="full" if len(present) == 3 else "half"))
    for direction in DIRECTIONAL:
        present = sorted(list(direction["branches"] & branch_set))
        if len(present) >= 2:
            positions = [item for item in items if item["branch"] in present]
            kind = "directional_full" if len(present) == 3 else "directional_half"
            kind_ko = "방합" if len(present) == 3 else "방합부분"
            name = direction["name"] if len(present) == 3 else direction["name"].replace("方合", "方合半")
            name_ko = direction["name_ko"] if len(present) == 3 else direction["name_ko"].replace("방합", "방합부분")
            relations.append(_relation(kind, kind_ko, name, name_ko, positions, present, element=direction["element"], element_ko=direction["element_ko"], completeness="full" if len(present) == 3 else "partial"))
    return relations


def _dedupe(relations: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for relation in relations:
        pos_key = tuple(sorted((p.get("source"), p.get("position"), p.get("pillar")) for p in relation.get("positions", [])))
        key = (relation["kind"], relation["name"], pos_key)
        if key in seen:
            continue
        seen.add(key)
        result.append(relation)
    return result


def _relations_with_luck(origin_chart: dict[str, str], luck_items: list[dict]) -> list[dict]:
    items = _origin_items(origin_chart) + luck_items
    relations = _dedupe(_pair_relations(items) + _set_relations(items))
    return [relation for relation in relations if relation.get("luck_involved")]


def _element_stimulus(luck_items: list[dict], facts: dict) -> dict:
    needs_drying = facts.get("water", {}).get("needs_drying") or facts.get("moisture_profile", {}).get("needs_drying")
    waterlogged = facts.get("water", {}).get("is_waterlogged") or facts.get("moisture_profile", {}).get("state") == "waterlogged"
    counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for item in luck_items:
        counts[ELEMENT_BY_STEM[item["stem"]]] += 1
        counts[ELEMENT_BY_BRANCH[item["branch"]]] += 1

    yongshin_score = 0
    gishin_score = 0
    notes: list[str] = []
    if counts["火"]:
        yongshin_score += counts["火"] * (3 if needs_drying else 1)
        notes.append("火 자극: 말림·건조·증발 작용")
    if counts["水"]:
        gishin_score += counts["水"] * (3 if waterlogged else 1)
        notes.append("水 자극: 침수·수습 과다 리스크")
    if counts["金"]:
        gishin_score += counts["金"] if waterlogged else 0
        notes.append("金 자극: 개통성과 수원 공급성을 동시에 고려")
    if counts["木"]:
        gishin_score += counts["木"] if waterlogged else 0
        notes.append("木 자극: 토 제어와 젖은 토 흔들림을 함께 고려")
    if counts["土"]:
        notes.append("土 자극: 제방·저장과 정체를 함께 고려")
    return {"counts": counts, "counts_ko": {ELEMENT_KO[k]: v for k, v in counts.items()}, "yongshin_score": yongshin_score, "gishin_score": gishin_score, "notes": notes}


def _relation_stimulus(relations: list[dict]) -> dict:
    yongshin_score = 0
    gishin_score = 0
    highlights: list[str] = []
    risks: list[str] = []
    for relation in relations:
        element = relation.get("element")
        kind = relation.get("kind")
        if element == "火" and kind in SUPPORTIVE_KINDS:
            yongshin_score += 3 if kind.endswith("full") or kind == "branch_liuhe" else 1
            highlights.append(f"{relation['name_ko']}: 火 작용 강화")
        if element == "水" and kind in SUPPORTIVE_KINDS:
            gishin_score += 3 if kind.endswith("full") or kind == "branch_liuhe" else 1
            risks.append(f"{relation['name_ko']}: 水 세력 강화")
        if kind in RISK_KINDS:
            gishin_score += 1
            risks.append(f"{relation['name_ko']}: 관계 자극/불안정")
    return {"yongshin_score": yongshin_score, "gishin_score": gishin_score, "highlights": highlights, "risks": risks}


def _grade(yongshin_score: int, gishin_score: int) -> dict:
    net = yongshin_score - gishin_score
    if net >= 4:
        return {"net_score": net, "grade": "supportive", "grade_ko": "용신 작동 우세"}
    if net <= -4:
        return {"net_score": net, "grade": "risky", "grade_ko": "기신 자극 우세"}
    return {"net_score": net, "grade": "mixed", "grade_ko": "혼합 자극"}


def analyze_overlay(origin_chart: dict[str, str], facts: dict, daewoon_item: dict | None = None, sewoon_item: dict | None = None) -> dict:
    luck_items: list[dict] = []
    if daewoon_item:
        luck_items.append(_luck_item("daewoon", daewoon_item["pillar"], {"age_start": daewoon_item.get("age_start"), "year_start": daewoon_item.get("year_start"), "year_end": daewoon_item.get("year_end")}))
    if sewoon_item:
        luck_items.append(_luck_item("sewoon", sewoon_item["pillar"], {"year": sewoon_item.get("year")}))
    relations = _relations_with_luck(origin_chart, luck_items) if luck_items else []
    element_stimulus = _element_stimulus(luck_items, facts)
    relation_stimulus = _relation_stimulus(relations)
    y_score = element_stimulus["yongshin_score"] + relation_stimulus["yongshin_score"]
    g_score = element_stimulus["gishin_score"] + relation_stimulus["gishin_score"]
    grade = _grade(y_score, g_score)
    return {
        "luck_items": luck_items,
        "relations": relations,
        "element_stimulus": element_stimulus,
        "relation_stimulus": relation_stimulus,
        "scores": {"yongshin_score": y_score, "gishin_score": g_score, **grade},
        "summary_ko": _summary_ko(grade["grade"], y_score, g_score, element_stimulus, relation_stimulus),
    }


def _summary_ko(grade: str, y_score: int, g_score: int, element_stimulus: dict, relation_stimulus: dict) -> str:
    if grade == "supportive":
        lead = "운의 자극이 용신 작동 쪽으로 기운다."
    elif grade == "risky":
        lead = "운의 자극이 병·기신을 건드릴 가능성이 크다."
    else:
        lead = "운의 자극은 용신과 기신이 섞여 있다."
    notes = (relation_stimulus.get("highlights") or element_stimulus.get("notes") or relation_stimulus.get("risks") or [""])
    return f"{lead} 용신점수 {y_score}, 기신점수 {g_score}. {notes[0]}"


def analyze_fortune_overlays(chart_result: dict, facts: dict) -> dict:
    chart = chart_result["chart"]
    daewoon_items = chart_result.get("daewoon", {}).get("cycles", [])
    sewoon_items = chart_result.get("sewoon", {}).get("years", [])
    current_daewoon = next((item for item in daewoon_items if item.get("is_current")), None)
    current_sewoon = next((item for item in sewoon_items if item.get("is_current")), None)
    return {
        "model_version": "fortune_overlay_v1.0.0",
        "current": {
            "daewoon_overlay": analyze_overlay(chart, facts, daewoon_item=current_daewoon),
            "sewoon_overlay": analyze_overlay(chart, facts, sewoon_item=current_sewoon),
            "combined_overlay": analyze_overlay(chart, facts, daewoon_item=current_daewoon, sewoon_item=current_sewoon),
        },
        "daewoon": [
            {"index": item.get("index"), "pillar": item.get("pillar"), "age_start": item.get("age_start"), "year_start": item.get("year_start"), "year_end": item.get("year_end"), "overlay": analyze_overlay(chart, facts, daewoon_item=item)}
            for item in daewoon_items
        ],
        "sewoon": [
            {"year": item.get("year"), "pillar": item.get("pillar"), "overlay": analyze_overlay(chart, facts, sewoon_item=item)}
            for item in sewoon_items
        ],
        "rules": [
            "원국+운의 신규 관계 중 운이 관여한 관계만 overlay 자극으로 본다.",
            "火 관계/火 오행은 수습 과다 구조에서 말림·증발 작용으로 가점한다.",
            "水 관계/水 오행은 수습 과다 구조에서 침수 리스크로 감점한다.",
            "충·해·파·원진·귀문은 불안정 자극으로 별도 감점한다.",
        ],
    }
