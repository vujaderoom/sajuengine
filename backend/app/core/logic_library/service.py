from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml
from pydantic import BaseModel, Field

from app.core.calendar.service import calculate_chart
from app.core.fact_builder.service import build_fact
from app.schemas import BirthInput

LOGIC_STATUSES = ["draft", "structured", "reviewed", "active", "disabled"]


class LogicStructureRequest(BaseModel):
    original_text: str
    title: str = ""
    category: str = "auto"
    source: str = "user"


class LogicCardCreateRequest(BaseModel):
    original_text: str
    title: str = ""
    category: str = "auto"
    status: str = "draft"
    active: bool = False
    source: str = "user"
    tags: list[str] = Field(default_factory=list)
    structured: dict[str, Any] | None = None


class LogicCardUpdateRequest(BaseModel):
    title: str | None = None
    original_text: str | None = None
    category: str | None = None
    status: str | None = None
    active: bool | None = None
    source: str | None = None
    tags: list[str] | None = None
    structured: dict[str, Any] | None = None


class LogicMatchRequest(BaseModel):
    birth: BirthInput = Field(default_factory=BirthInput)
    include_inactive: bool = False


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _logic_dir() -> Path:
    return _repo_root() / "logic_cards"


def _safe_id(value: str) -> str:
    safe = value.strip().lower().replace(" ", "_").replace("/", "_").replace("..", "_")
    return safe or f"logic_{uuid4().hex[:8]}"


def _logic_path(logic_id: str) -> Path:
    return _logic_dir() / f"{_safe_id(logic_id)}.yaml"


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def _infer_category(text: str) -> str:
    if _contains_any(text, ["용신", "기신", "약", "병", "조후"]):
        return "병약용신"
    if _contains_any(text, ["일간", "갑목", "을목", "병화", "정화", "무토", "기토", "경금", "신금", "임수", "계수"]):
        return "일간별 성향"
    if _contains_any(text, ["재다", "관다", "인다", "식상", "상관", "편재", "정재", "편관", "정관"]):
        return "십성"
    if _contains_any(text, ["대운", "세운", "운에서", "년운"]):
        return "대운/세운"
    if _contains_any(text, ["합", "충", "형", "파", "해", "원진", "귀문", "삼합", "방합"]):
        return "합충형파"
    if _contains_any(text, ["도화", "홍염", "역마", "망신", "화개", "공망"]):
        return "신살/공망"
    return "일반 명리 문장"


def _infer_conditions(text: str) -> dict[str, Any]:
    conditions: dict[str, Any] = {"all": []}
    stem_map = {
        "갑목": "甲", "을목": "乙", "병화": "丙", "정화": "丁", "무토": "戊", "기토": "己", "경금": "庚", "신금": "辛", "임수": "壬", "계수": "癸",
        "甲": "甲", "乙": "乙", "丙": "丙", "丁": "丁", "戊": "戊", "己": "己", "庚": "庚", "辛": "辛", "壬": "壬", "癸": "癸",
    }
    for word, stem in stem_map.items():
        if word in text and ("일간" in text or word in ["갑목", "을목", "병화", "정화", "무토", "기토", "경금", "신금", "임수", "계수"]):
            conditions["all"].append({"path": "chart.day", "op": "contains", "value": stem, "label": f"일간 {stem}"})
            break
    element_words = {
        "木": ["목", "목이", "목다", "목 많", "木"],
        "火": ["화", "화가", "화다", "화 많", "火"],
        "土": ["토", "토가", "토다", "토 많", "土"],
        "金": ["금", "금이", "금다", "금 많", "金"],
        "水": ["수", "수가", "수다", "수 많", "水"],
    }
    for element, words in element_words.items():
        if _contains_any(text, words) and _contains_any(text, ["많", "과", "다", "왕", "강"]):
            conditions["all"].append({"path": "facts.element_balance", "op": "element_high", "value": element, "label": f"{element} 과다/강"})
    if not conditions["all"]:
        conditions["all"].append({"path": "chart", "op": "exists", "value": True, "label": "일반 참고 문장"})
    return conditions


def _infer_effect(text: str, category: str) -> dict[str, Any]:
    tags: list[str] = []
    risk_level = "low"
    if _contains_any(text, ["술", "유흥", "여자", "이성", "향락"]):
        tags += ["향락성", "이성관심", "발산성"]
        risk_level = "high"
    if _contains_any(text, ["돈", "재물", "재성", "재다"]):
        tags += ["재물", "재성"]
    if _contains_any(text, ["직업", "관", "조직", "규율"]):
        tags += ["직업", "조직성"]
    if _contains_any(text, ["말림", "건조", "증발"]):
        tags += ["말림", "건조", "증발"]
    if _contains_any(text, ["침수", "습", "물"]):
        tags += ["수습", "침수"]
    if not tags:
        tags = [category]
    return {"type": "auxiliary_tag", "tags": list(dict.fromkeys(tags)), "score_delta": 0.2 if risk_level == "low" else 0.3, "risk_level": risk_level, "apply_to_final": False}


def structure_logic_text(request: LogicStructureRequest) -> dict[str, Any]:
    text = request.original_text.strip()
    category = request.category if request.category != "auto" else _infer_category(text)
    title = request.title.strip() or (text[:30] + ("..." if len(text) > 30 else ""))
    structured = {
        "title": title,
        "category": category,
        "conditions": _infer_conditions(text),
        "interpretation": {
            "summary": text,
            "normalized_summary": _normalize_sentence(text),
            "usage": "보조 판단 문장으로 사용. 단정 결론이 아니라 후보 태그와 해석 근거로 활용.",
        },
        "effect": _infer_effect(text, category),
        "caution": {
            "risk_level": "high" if _contains_any(text, ["술", "여자", "바람", "죽", "이혼", "사망", "범죄"]) else "medium",
            "notes": [
                "문장 원문은 보존하고, 엔진에는 조건/태그/점수로만 반영합니다.",
                "성향·사건 단정 금지. 원국 전체, 대운·세운, 보조 조건과 함께 봅니다.",
                "active=true로 켜기 전 반드시 검토하세요.",
            ],
        },
        "engine_mapping": {
            "candidate_type": "logic_card",
            "active_required": True,
            "finalizer_role": "auxiliary_evidence",
            "rule_candidate_ready": False,
        },
    }
    return {"original_text": text, "structured": structured, "confidence": "scaffold", "notes": ["I-3 구조화는 규칙 기반 초안입니다.", "추후 LLM 구조화기로 교체 가능하도록 입출력 형태를 고정했습니다."]}


def _normalize_sentence(text: str) -> str:
    replacements = {"좋아한다": "기울 수 있다", "많으면": "많을 때", "이다": "로 볼 수 있다"}
    result = text
    for a, b in replacements.items():
        result = result.replace(a, b)
    return result


def create_logic_card(request: LogicCardCreateRequest) -> dict[str, Any]:
    structured = request.structured or structure_logic_text(LogicStructureRequest(original_text=request.original_text, title=request.title, category=request.category, source=request.source))["structured"]
    logic_id = _safe_id(f"logic_{uuid4().hex[:8]}")
    status = request.status if request.status in LOGIC_STATUSES else "draft"
    active = bool(request.active)
    if status == "active":
        active = True
    if status == "disabled":
        active = False
    card = {
        "id": logic_id,
        "title": request.title or structured.get("title") or request.original_text[:30],
        "status": status,
        "active": active,
        "category": request.category if request.category != "auto" else structured.get("category", "일반 명리 문장"),
        "original_text": request.original_text,
        "structured": structured,
        "source": request.source,
        "tags": list(dict.fromkeys(request.tags + structured.get("effect", {}).get("tags", []))),
        "created_at": _now(),
        "updated_at": _now(),
    }
    path = _logic_path(logic_id)
    _logic_dir().mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return {"saved": True, "path": str(path.relative_to(_repo_root())), "card": card}


def _load_card_path(path: Path) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        data["_path"] = str(path.relative_to(_repo_root()))
        data["_raw_yaml"] = path.read_text(encoding="utf-8")
        return data
    except Exception:
        return None


def list_logic_cards(include_disabled: bool = True) -> dict[str, Any]:
    if not _logic_dir().exists():
        return {"total": 0, "cards": []}
    cards = []
    for path in sorted(_logic_dir().glob("*.yaml")):
        card = _load_card_path(path)
        if not card:
            continue
        if not include_disabled and not card.get("active"):
            continue
        cards.append(_summary(card))
    return {"total": len(cards), "cards": cards}


def _summary(card: dict[str, Any]) -> dict[str, Any]:
    return {"id": card.get("id"), "title": card.get("title"), "category": card.get("category"), "status": card.get("status"), "active": card.get("active", False), "original_text": card.get("original_text"), "tags": card.get("tags", []), "path": card.get("_path"), "updated_at": card.get("updated_at")}


def get_logic_card(logic_id: str) -> dict[str, Any] | None:
    path = _logic_path(logic_id)
    if not path.exists():
        return None
    return _load_card_path(path)


def update_logic_card(logic_id: str, request: LogicCardUpdateRequest) -> dict[str, Any] | None:
    card = get_logic_card(logic_id)
    if not card:
        return None
    for field in ["title", "original_text", "category", "source"]:
        value = getattr(request, field)
        if value is not None:
            card[field] = value
    if request.tags is not None:
        card["tags"] = request.tags
    if request.structured is not None:
        card["structured"] = request.structured
    if request.status is not None:
        card["status"] = request.status if request.status in LOGIC_STATUSES else card.get("status", "draft")
    if request.active is not None:
        card["active"] = bool(request.active)
        card["status"] = "active" if request.active else ("disabled" if card.get("status") == "active" else card.get("status", "draft"))
    if card.get("status") == "active":
        card["active"] = True
    if card.get("status") == "disabled":
        card["active"] = False
    card["updated_at"] = _now()
    path = _logic_path(logic_id)
    clean = {k: v for k, v in card.items() if not k.startswith("_")}
    path.write_text(yaml.safe_dump(clean, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return {"updated": True, "card": get_logic_card(logic_id)}


def delete_logic_card(logic_id: str) -> dict[str, Any] | None:
    path = _logic_path(logic_id)
    if not path.exists():
        return None
    path.unlink()
    return {"deleted": True, "id": logic_id}


def toggle_logic_card(logic_id: str, active: bool) -> dict[str, Any] | None:
    return update_logic_card(logic_id, LogicCardUpdateRequest(active=active, status="active" if active else "disabled"))


def match_logic_cards(request: LogicMatchRequest) -> dict[str, Any]:
    chart_payload = calculate_chart(request.birth)
    facts = build_fact(chart_payload)
    chart = chart_payload["chart"]
    cards = [get_logic_card(item["id"]) for item in list_logic_cards(include_disabled=request.include_inactive)["cards"]]
    matches = []
    for card in cards:
        if not card:
            continue
        if not request.include_inactive and not card.get("active"):
            continue
        score, reasons = _match_card(card, chart, facts)
        if score > 0:
            matches.append({"id": card.get("id"), "title": card.get("title"), "category": card.get("category"), "active": card.get("active"), "score": score, "reasons": reasons, "effect": card.get("structured", {}).get("effect", {}), "original_text": card.get("original_text")})
    return {"chart": chart, "matches": sorted(matches, key=lambda x: x["score"], reverse=True), "facts_used": {"temperature": facts.get("temperature_profile"), "moisture": facts.get("moisture_profile")}}


def _match_card(card: dict[str, Any], chart: dict[str, str], facts: dict[str, Any]) -> tuple[float, list[str]]:
    conditions = card.get("structured", {}).get("conditions", {}).get("all", [])
    if not conditions:
        return 0.1, ["조건 없는 참고 문장"]
    score = 0.0
    reasons = []
    for condition in conditions:
        path = condition.get("path")
        op = condition.get("op")
        value = condition.get("value")
        if path == "chart.day" and op == "contains" and value in chart.get("day", ""):
            score += 1.0
            reasons.append(condition.get("label") or f"일주에 {value} 포함")
        elif path == "chart" and op == "exists":
            score += 0.1
            reasons.append("일반 참고 조건")
        elif path == "facts.element_balance" and op == "element_high":
            # 아직 정밀 오행 세력 스코어가 없으므로 원국 문자 출현 횟수 기반 임시 매칭
            element_chars = {"火": "丙丁巳午", "水": "壬癸子亥", "木": "甲乙寅卯", "金": "庚辛申酉", "土": "戊己辰戌丑未"}.get(value, "")
            count = sum(1 for pillar in chart.values() for ch in pillar if ch in element_chars)
            if count >= 2:
                score += 0.7
                reasons.append(condition.get("label") or f"{value} 출현 {count}회")
    return score, reasons
