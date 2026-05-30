from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import os

from app.core.calendar.solar_terms import ALL_24_SOLAR_TERMS, MONTH_BOUNDARIES, SolarTermBoundary

REQUIRED_TERM_NAMES = [name for name, _ko, _month, _day in ALL_24_SOLAR_TERMS]
REQUIRED_MONTH_BOUNDARY_NAMES = [item.name for item in MONTH_BOUNDARIES]
DEFAULT_TABLE_FILENAME = "solar_terms_1900_2100.json"
_RUNTIME_CACHE: dict[int, SolarTermLookupResult] = {}


@dataclass(frozen=True)
class SolarTermLookupResult:
    mode: str
    source: str
    terms: list[dict]
    validation: dict


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _candidate_table_paths() -> list[Path]:
    candidates: list[Path] = []
    env_path = os.getenv("SAJU_SOLAR_TERMS_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(
        [
            _repo_root() / "data" / DEFAULT_TABLE_FILENAME,
            _repo_root() / "backend" / "data" / DEFAULT_TABLE_FILENAME,
            Path.cwd() / "data" / DEFAULT_TABLE_FILENAME,
        ]
    )
    unique: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        resolved = path.resolve()
        if str(resolved) not in seen:
            unique.append(resolved)
            seen.add(str(resolved))
    return unique


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(_repo_root()))
    except Exception:
        return str(path)


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


def _load_table_data() -> tuple[dict | None, str, list[str]]:
    checked_paths = [_display_path(path) for path in _candidate_table_paths()]
    for path in _candidate_table_paths():
        if not path.exists():
            continue
        try:
            return json.loads(path.read_text(encoding="utf-8")), _display_path(path), checked_paths
        except Exception:
            return None, f"invalid_json:{_display_path(path)}", checked_paths
    return None, "missing", checked_paths


def _load_external_table(year: int) -> SolarTermLookupResult | None:
    data, source, _checked_paths = _load_table_data()
    if not data:
        return None
    year_data = data.get(str(year))
    if not year_data:
        return None
    validation = validate_solar_term_year(year, year_data)
    if not validation["passed"]:
        return None
    return SolarTermLookupResult(mode="solar_term_table", source=source, terms=year_data, validation=validation)


def _load_runtime_skyfield(year: int) -> SolarTermLookupResult | None:
    if year in _RUNTIME_CACHE:
        return _RUNTIME_CACHE[year]
    try:
        from app.core.calendar.runtime_solar_terms import runtime_skyfield_terms_for_year

        result = runtime_skyfield_terms_for_year(year)
        if not result.get("available"):
            return None
        terms = result["terms"]
        validation = validate_solar_term_year(year, terms)
        if not validation["passed"]:
            return None
        lookup = SolarTermLookupResult(
            mode="skyfield_runtime",
            source="skyfield_runtime:de421.bsp",
            terms=terms,
            validation={**validation, "runtime_error": result.get("error")},
        )
        _RUNTIME_CACHE[year] = lookup
        return lookup
    except Exception:
        return None


def _runtime_status(year: int) -> dict:
    try:
        from app.core.calendar.runtime_solar_terms import runtime_skyfield_terms_for_year

        result = runtime_skyfield_terms_for_year(year)
        if not result.get("available"):
            return {"available": False, "source": "skyfield_runtime:de421.bsp", "error": result.get("error")}
        validation = validate_solar_term_year(year, result["terms"])
        return {"available": validation["passed"], "source": "skyfield_runtime:de421.bsp", "validation": validation, "error": result.get("error")}
    except Exception as exc:
        return {"available": False, "source": "skyfield_runtime:de421.bsp", "error": repr(exc)}


def _fixed_terms(year: int) -> list[dict]:
    return [{"name": name, "ko": ko, "datetime": datetime(year, month, day).isoformat(), "source": "fixed_baseline"} for name, ko, month, day in ALL_24_SOLAR_TERMS]


def solar_terms_lookup(year: int) -> SolarTermLookupResult:
    external = _load_external_table(year)
    if external:
        return external
    runtime = _load_runtime_skyfield(year)
    if runtime:
        return runtime
    terms = _fixed_terms(year)
    data, source, checked_paths = _load_table_data()
    year_available = str(year) in data if data else False
    return SolarTermLookupResult(
        mode="fixed_korean_civil_baseline",
        source="builtin_fixed_baseline",
        terms=terms,
        validation={
            "passed": True,
            "errors": [],
            "warnings": ["external solar term table and runtime skyfield unavailable; fixed fallback active"],
            "term_count": len(terms),
            "table_source": source,
            "checked_paths": checked_paths,
            "requested_year": year,
            "requested_year_available": year_available,
        },
    )


def solar_term_table_status(year: int) -> dict:
    data, source, checked_paths = _load_table_data()
    table_status = {
        "available": False,
        "source": source,
        "validation": None,
        "year_validation": None,
        "checked_paths": checked_paths,
        "requested_year": year,
        "requested_year_available": False,
    }
    if data:
        validation = validate_solar_term_table(data)
        year_validation = validate_solar_term_year(year, data.get(str(year), [])) if str(year) in data else None
        requested_year_available = str(year) in data and bool(year_validation and year_validation["passed"])
        table_status.update(
            {
                "available": validation["passed"] and requested_year_available,
                "validation": validation,
                "year_validation": year_validation,
                "requested_year_available": requested_year_available,
            }
        )
    runtime_status = _runtime_status(year)
    active = solar_terms_lookup(year)
    return {
        "available": active.mode in ["solar_term_table", "skyfield_runtime"],
        "mode": active.mode,
        "source": active.source,
        "table": table_status,
        "runtime": runtime_status,
        "fallback_active": active.mode == "fixed_korean_civil_baseline",
    }


def month_boundaries_lookup(year: int) -> list[SolarTermBoundary]:
    lookup = solar_terms_lookup(year)
    if lookup.mode == "fixed_korean_civil_baseline":
        return MONTH_BOUNDARIES
    by_name = {item.get("name"): item for item in lookup.terms}
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
