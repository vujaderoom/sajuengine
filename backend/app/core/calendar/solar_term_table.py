from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from app.core.calendar.solar_terms import ALL_24_SOLAR_TERMS, MONTH_BOUNDARIES, SolarTermBoundary

REQUIRED_TERM_NAMES = [name for name, _ko, _month, _day in ALL_24_SOLAR_TERMS]
REQUIRED_MONTH_BOUNDARY_NAMES = [item.name for item in MONTH_BOUNDARIES]


@dataclass(frozen=True)
class SolarTermLookupResult:
    mode: str
    source: str
    terms: list[dict]
    validation: dict


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _table_path() -> Path:
    return _repo_root() / "data" / "solar_terms_1900_2100.json"


def validate_solar_term_year(year: int, terms: list[dict]) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    names = [item.get("name") for item in terms]
    missing = [name for name in REQUIRED_TERM_NAMES if name not in names]
    if missing:
        errors.append(f"missing solar terms: {','.join(missing)}")
    for item in terms:
        if "name" not in item or "datetime" not in item:
            errors.append("each term requires name and datetime")
            continue
        try:
            dt = datetime.fromisoformat(item["datetime"])
        except Exception:
            errors.append(f"invalid datetime for {item.get('name')}: {item.get('datetime')}")
            continue
        if dt.year not in [year, year + 1]:
            warnings.append(f"term {item.get('name')} datetime year {dt.year} is outside expected range")
    return {"passed": not errors, "errors": errors, "warnings": warnings, "term_count": len(terms)}


def validate_solar_term_table(data: dict) -> dict:
    year_results = {}
    errors = []
    for year_text, terms in data.items():
        try:
            year = int(year_text)
        except Exception:
            errors.append(f"invalid year key: {year_text}")
            continue
        result = validate_solar_term_year(year, terms)
        year_results[year_text] = result
        if not result["passed"]:
            errors.append(f"{year_text}: {'; '.join(result['errors'])}")
    return {"passed": not errors, "errors": errors, "year_results": year_results, "year_count": len(year_results)}


def _load_table_data() -> tuple[dict | None, str]:
    path = _table_path()
    if not path.exists():
        return None, "missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), str(path.relative_to(_repo_root()))
    except Exception:
        return None, "invalid_json"


def _load_external_table(year: int) -> SolarTermLookupResult | None:
    data, source = _load_table_data()
    if not data:
        return None
    year_data = data.get(str(year))
    if not year_data:
        return None
    validation = validate_solar_term_year(year, year_data)
    if not validation["passed"]:
        return None
    return SolarTermLookupResult(mode="solar_term_table", source=source, terms=year_data, validation=validation)


def _fixed_terms(year: int) -> list[dict]:
    return [{"name": name, "ko": ko, "datetime": datetime(year, month, day).isoformat(), "source": "fixed_baseline"} for name, ko, month, day in ALL_24_SOLAR_TERMS]


def solar_terms_lookup(year: int) -> SolarTermLookupResult:
    external = _load_external_table(year)
    if external:
        return external
    terms = _fixed_terms(year)
    return SolarTermLookupResult(
        mode="fixed_korean_civil_baseline",
        source="builtin_fixed_baseline",
        terms=terms,
        validation={"passed": True, "errors": [], "warnings": ["external solar term table not found or invalid; fixed fallback active"], "term_count": len(terms)},
    )


def solar_term_table_status(year: int) -> dict:
    data, source = _load_table_data()
    if not data:
        return {"available": False, "source": source, "mode": "fixed_korean_civil_baseline", "validation": None}
    validation = validate_solar_term_table(data)
    year_validation = validate_solar_term_year(year, data.get(str(year), [])) if str(year) in data else None
    return {"available": validation["passed"], "source": source, "mode": "solar_term_table" if validation["passed"] else "fixed_korean_civil_baseline", "validation": validation, "year_validation": year_validation}


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
