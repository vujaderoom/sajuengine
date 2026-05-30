from __future__ import annotations

from itertools import combinations
from typing import Any

STEM_COMBOS = {
    frozenset(["甲", "己"]): {"name": "甲己合", "name_ko": "갑기합", "element": "土", "element_ko": "토"},
    frozenset(["乙", "庚"]): {"name": "乙庚合", "name_ko": "을경합", "element": "金", "element_ko": "금"},
    frozenset(["丙", "辛"]): {"name": "丙辛合", "name_ko": "병신합", "element": "水", "element_ko": "수"},
    frozenset(["丁", "壬"]): {"name": "丁壬合", "name_ko": "정임합", "element": "木", "element_ko": "목"},
    frozenset(["戊", "癸"]): {"name": "戊癸合", "name_ko": "무계합", "element": "火", "element_ko": "화"},
}

BRANCH_CLASHES = {
    frozenset(["子", "午"]): ("子午沖", "자오충"),
    frozenset(["丑", "未"]): ("丑未沖", "축미충"),
    frozenset(["寅", "申"]): ("寅申沖", "인신충"),
    frozenset(["卯", "酉"]): ("卯酉沖", "묘유충"),
    frozenset(["辰", "戌"]): ("辰戌沖", "진술충"),
    frozenset(["巳", "亥"]): ("巳亥沖", "사해충"),
}

BRANCH_LIUHE = {
    frozenset(["子", "丑"]): ("子丑合", "자축합", "土", "토"),
    frozenset(["寅", "亥"]): ("寅亥合", "인해합", "木", "목"),
    frozenset(["卯", "戌"]): ("卯戌合", "묘술합", "火", "화"),
    frozenset(["辰", "酉"]): ("辰酉合", "진유합", "金", "금"),
    frozenset(["巳", "申"]): ("巳申合", "사신합", "水", "수"),
    frozenset(["午", "未"]): ("午未合", "오미합", "火", "화"),
}

BRANCH_HARMS = {
    frozenset(["子", "未"]): ("子未害", "자미해"),
    frozenset(["丑", "午"]): ("丑午害", "축오해"),
    frozenset(["寅", "巳"]): ("寅巳害", "인사해"),
    frozenset(["卯", "辰"]): ("卯辰害", "묘진해"),
    frozenset(["申", "亥"]): ("申亥害", "신해해"),
    frozenset(["酉", "戌"]): ("酉戌害", "유술해"),
}

BRANCH_BREAKS = {
    frozenset(["子", "酉"]): ("子酉破", "자유파"),
    frozenset(["丑", "辰"]): ("丑辰破", "축진파"),
    frozenset(["寅", "亥"]): ("寅亥破", "인해파"),
    frozenset(["卯", "午"]): ("卯午破", "묘오파"),
    frozenset(["巳", "申"]): ("巳申破", "사신파"),
    frozenset(["未", "戌"]): ("未戌破", "미술파"),
}

BRANCH_WONJIN = {
    frozenset(["子", "未"]): ("子未元嗔", "자미원진"),
    frozenset(["丑", "午"]): ("丑午元嗔", "축오원진"),
    frozenset(["寅", "酉"]): ("寅酉元嗔", "인유원진"),
    frozenset(["卯", "申"]): ("卯申元嗔", "묘신원진"),
    frozenset(["辰", "亥"]): ("辰亥元嗔", "진해원진"),
    frozenset(["巳", "戌"]): ("巳戌元嗔", "사술원진"),
}

BRANCH_GWIMUN = {
    frozenset(["子", "酉"]): ("子酉鬼門", "자유귀문"),
    frozenset(["丑", "午"]): ("丑午鬼門", "축오귀문"),
    frozenset(["寅", "未"]): ("寅未鬼門", "인미귀문"),
    frozenset(["卯", "申"]): ("卯申鬼門", "묘신귀문"),
    frozenset(["辰", "亥"]): ("辰亥鬼門", "진해귀문"),
    frozenset(["巳", "戌"]): ("巳戌鬼門", "사술귀문"),
}

TRINES = [
    {"branches": {"申", "子", "辰"}, "name": "申子辰三合", "name_ko": "신자진삼합", "element": "水", "element_ko": "수"},
    {"branches": {"亥", "卯", "未"}, "name": "亥卯未三合", "name_ko": "해묘미삼합", "element": "木", "element_ko": "목"},
    {"branches": {"寅", "午", "戌"}, "name": "寅午戌三合", "name_ko": "인오술삼합", "element": "火", "element_ko": "화"},
    {"branches": {"巳", "酉", "丑"}, "name": "巳酉丑三合", "name_ko": "사유축삼합", "element": "金", "element_ko": "금"},
]

DIRECTIONAL = [
    {"branches": {"亥", "子", "丑"}, "name": "亥子丑方合", "name_ko": "해자축방합", "element": "水", "element_ko": "수"},
    {"branches": {"寅", "卯", "辰"}, "name": "寅卯辰方合", "name_ko": "인묘진방합", "element": "木", "element_ko": "목"},
    {"branches": {"巳", "午", "未"}, "name": "巳午未方合", "name_ko": "사오미방합", "element": "火", "element_ko": "화"},
    {"branches": {"申", "酉", "戌"}, "name": "申酉戌方合", "name_ko": "신유술방합", "element": "金", "element_ko": "금"},
]

SELF_PENALTY = {
    "辰": ("辰辰自刑", "진진자형"),
    "午": ("午午自刑", "오오자형"),
    "酉": ("酉酉自刑", "유유자형"),
    "亥": ("亥亥自刑", "해해자형"),
}

POSITION_LABELS = {"year": "년주", "month": "월주", "day": "일주", "hour": "시주"}
ORDER = ["year", "month", "day", "hour"]


def _branch_items(chart: dict[str, str]) -> list[dict[str, str]]:
    return [{"position": key, "label": POSITION_LABELS[key], "branch": chart[key][1], "pillar": chart[key]} for key in ORDER]


def _stem_items(chart: dict[str, str]) -> list[dict[str, str]]:
    return [{"position": key, "label": POSITION_LABELS[key], "stem": chart[key][0], "pillar": chart[key]} for key in ORDER]


def _relation(kind: str, kind_ko: str, name: str, name_ko: str, positions: list[dict], branches_or_stems: list[str], **extra: Any) -> dict[str, Any]:
    return {
        "kind": kind,
        "kind_ko": kind_ko,
        "name": name,
        "name_ko": name_ko,
        "positions": positions,
        "items": branches_or_stems,
        **extra,
    }


def analyze_relations(chart: dict[str, str]) -> dict[str, Any]:
    stems = _stem_items(chart)
    branches = _branch_items(chart)
    relations: list[dict[str, Any]] = []

    for a, b in combinations(stems, 2):
        meta = STEM_COMBOS.get(frozenset([a["stem"], b["stem"]]))
        if meta:
            relations.append(_relation("stem_combo", "천간합", meta["name"], meta["name_ko"], [a, b], [a["stem"], b["stem"]], element=meta["element"], element_ko=meta["element_ko"]))

    pair_tables = [
        ("branch_clash", "지지충", BRANCH_CLASHES, False),
        ("branch_liuhe", "육합", BRANCH_LIUHE, True),
        ("branch_harm", "해", BRANCH_HARMS, False),
        ("branch_break", "파", BRANCH_BREAKS, False),
        ("wonjin", "원진", BRANCH_WONJIN, False),
        ("gwimun", "귀문", BRANCH_GWIMUN, False),
    ]
    for a, b in combinations(branches, 2):
        pair = frozenset([a["branch"], b["branch"]])
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

    branch_set = {item["branch"] for item in branches}
    for trine in TRINES:
        present = sorted(list(trine["branches"] & branch_set))
        if len(present) == 3:
            positions = [item for item in branches if item["branch"] in trine["branches"]]
            relations.append(_relation("trine_full", "삼합", trine["name"], trine["name_ko"], positions, present, element=trine["element"], element_ko=trine["element_ko"], completeness="full"))
        elif len(present) == 2:
            positions = [item for item in branches if item["branch"] in present]
            relations.append(_relation("trine_half", "반합", trine["name"].replace("三合", "半合"), trine["name_ko"].replace("삼합", "반합"), positions, present, element=trine["element"], element_ko=trine["element_ko"], completeness="half"))

    for direction in DIRECTIONAL:
        present = sorted(list(direction["branches"] & branch_set))
        if len(present) == 3:
            positions = [item for item in branches if item["branch"] in direction["branches"]]
            relations.append(_relation("directional_full", "방합", direction["name"], direction["name_ko"], positions, present, element=direction["element"], element_ko=direction["element_ko"], completeness="full"))
        elif len(present) == 2:
            positions = [item for item in branches if item["branch"] in present]
            relations.append(_relation("directional_half", "방합부분", direction["name"].replace("方合", "方合半"), direction["name_ko"].replace("방합", "방합부분"), positions, present, element=direction["element"], element_ko=direction["element_ko"], completeness="partial"))

    branch_counts: dict[str, int] = {}
    for item in branches:
        branch_counts[item["branch"]] = branch_counts.get(item["branch"], 0) + 1
    for branch, count in branch_counts.items():
        if count >= 2 and branch in SELF_PENALTY:
            name, name_ko = SELF_PENALTY[branch]
            positions = [item for item in branches if item["branch"] == branch]
            relations.append(_relation("self_penalty", "자형", name, name_ko, positions, [branch] * count, count=count))

    branch_names = [r for r in relations if r["kind"].startswith("branch") or r["kind"] in ["trine_full", "trine_half", "directional_full", "directional_half", "self_penalty", "wonjin", "gwimun"]]
    return {
        "items": relations,
        "summary": {
            "total": len(relations),
            "stem_combo": len([r for r in relations if r["kind"] == "stem_combo"]),
            "branch_related": len(branch_names),
            "has_clash": any(r["kind"] == "branch_clash" for r in relations),
            "has_liuhe": any(r["kind"] == "branch_liuhe" for r in relations),
            "has_harm": any(r["kind"] == "branch_harm" for r in relations),
            "has_break": any(r["kind"] == "branch_break" for r in relations),
            "has_wonjin": any(r["kind"] == "wonjin" for r in relations),
            "has_gwimun": any(r["kind"] == "gwimun" for r in relations),
        },
        "by_kind": {kind: [r for r in relations if r["kind"] == kind] for kind in sorted({r["kind"] for r in relations})},
    }
