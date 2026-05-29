from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BirthInput(BaseModel):
    name: str = "sample"
    sex: Literal["male", "female", "unknown"] = "male"
    birth_datetime: str = "1991-05-29T16:36:00"
    calendar_type: Literal["solar", "lunar"] = "solar"
    timezone: str = "Asia/Seoul"
    location: str = "Seoul"


class RuleRunnerRequest(BaseModel):
    birth: BirthInput = Field(default_factory=BirthInput)
    rule_version: str = "v1.0.0"
