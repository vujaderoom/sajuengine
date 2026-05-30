from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from app.core.calendar.solar_terms import ALL_24_SOLAR_TERMS, MONTH_BOUNDARIES, SolarTermBoundary


@dataclass(frozen=True)
class SolarTermLookupResult:
    mode: str
    source: str
    terms: list[dict]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _table_path() -> Path:
    return _repo_root() / "data" / "solar_terms_1900_2100.json"


def _load_external_table(year: int) -> SolarTermLookupResult | None:
    path = _table_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        year_data = data.get(str(year))
        if not year_data:
            return None
        return SolarTermLookupResult(mode="solar_term_table", source=str(path.relative_to(_repo_root())), terms=year_data)
    except Exception:
        return None


def _fixed_terms(year: int) -> list[dict]:
    return [{"name": name, "ko": ko, "datetime": datetime(year, month, day).isoformat(), "source": "fixed_baseline"} for name, ko, month, day in ALL_24_SOLAR_TERMS]


def solar_terms_lookup(year: int) -> SolarTermLookupResult:
    external = _load_external_table(year)
    if external:
        return external
    return SolarTermLookupResult(mode="fixed_korean_civil_baseline", source="builtin_fixed_baseline", terms=_fixed_terms(year))


def month_boundaries_lookup(year: int) -> list[SolarTermBoundary]:
    external = _load_external_table(year)
    if not external:
        return MONTH_BOUNDARIES
    by_name = {item.get("name"): item for item in external.terms}
    boundaries: list[SolarTermBoundary] = []
    for boundary in MONTH_BOUNDARIES:
        row = by_name.get(boundary.name)
        if not row:
            boundaries.append(boundary)
            continue
        dt = datetime.fromisoformat(row["datetime"])
        boundaries.append(
            SolarTermBoundary(
                name=boundary.name,
                ko=boundary.ko,
                branch=boundary.branch,
                month_order=boundary.month_order,
                month=dt.month,
                day=dt.day,
                hour=dt.hour,
                minute=dt.minute,
            )
        )
    return boundaries
