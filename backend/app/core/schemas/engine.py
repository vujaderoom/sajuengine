from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class EvidenceQuery(BaseModel):
    tags: list[str] = Field(default_factory=list)


class Proposal(BaseModel):
    proposal_id: str
    candidate_type: str
    value: str
    score_delta: float = 0.0
    source_rule: str | None = None
    reason: str = ""
    confidence_signal: Literal["weak", "medium", "strong"] = "medium"
    symbols: list[str] = Field(default_factory=list)
    action: str | None = None
    rule_priority: int = 0
    evidence_query: EvidenceQuery = Field(default_factory=EvidenceQuery)


class CoreDisease(BaseModel):
    type: str
    name: str
    depth: int = 1
    reason: str = ""
    source_rule: str | None = None


class DerivedDisease(BaseModel):
    type: str
    name: str
    reason: str = ""


class Medicine(BaseModel):
    type: str
    name: str
    action: str
    execution_grade: Literal["A", "B", "C", "D"] = "B"
    freedom: Literal["작동", "제한", "상실", "미정"] = "작동"
    reason: str = ""


class YongshinCandidate(BaseModel):
    value: str
    symbols: list[str] = Field(default_factory=list)
    score: float = 0.0
    source_rule: str | None = None
    reason: str = ""
    action: str | None = None


class SelectedYongshin(BaseModel):
    primary: str
    symbols: list[str] = Field(default_factory=list)
    secondary: list[str] = Field(default_factory=list)
    source_rule: str | None = None
    reason: str = ""
    excluded: list[dict[str, Any]] = Field(default_factory=list)


class GishinCandidate(BaseModel):
    value: str
    reason: str = ""
    source: str | None = None


class Confidence(BaseModel):
    score: float
    level: Literal["강한 판정", "경향성 판정", "가능성 판정", "판단 보류"]


class FinalEngineResult(BaseModel):
    core_disease: CoreDisease
    derived_diseases: list[DerivedDisease] = Field(default_factory=list)
    medicine: Medicine
    yongshin_candidates: list[YongshinCandidate] = Field(default_factory=list)
    selected_yongshin: SelectedYongshin
    gishin_candidates: list[GishinCandidate] = Field(default_factory=list)
    stability_grade: Literal["A", "B", "C", "D"] = "B"
    confidence: Confidence


class ReportPayload(BaseModel):
    chart: dict[str, Any]
    facts: dict[str, Any]
    climate_profile: dict[str, Any]
    binding_profile: dict[str, Any]
    storage_profile: dict[str, Any]
    flow_profile: dict[str, Any]
    proposal_summary: dict[str, Any]
    disease_profile: dict[str, Any]
    medicine_profile: dict[str, Any]
    yongshin: dict[str, Any]
    confidence: dict[str, Any]
    delta_inputs: dict[str, Any]
    luck_delta: dict[str, Any]
    rag_evidence: list[dict[str, Any]] = Field(default_factory=list)
    decision_trace_id: str
    rule_version: str
    renderer_guardrails: list[str] = Field(default_factory=list)
    final_interpretation: str = ""
