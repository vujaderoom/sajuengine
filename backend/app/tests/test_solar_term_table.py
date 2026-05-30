from app.core.calendar.solar_term_table import validate_solar_term_year, validate_solar_term_table
from app.core.calendar.solar_terms import ALL_24_SOLAR_TERMS


def make_year(year: int):
    return [
        {"name": name, "ko": ko, "datetime": f"{year:04d}-{month:02d}-{day:02d}T00:00:00+09:00"}
        for name, ko, month, day in ALL_24_SOLAR_TERMS
    ]


def test_validate_solar_term_year_passes():
    result = validate_solar_term_year(1991, make_year(1991))
    assert result["passed"] is True
    assert result["term_count"] == 24


def test_validate_solar_term_year_fails_missing_term():
    result = validate_solar_term_year(1991, make_year(1991)[:-1])
    assert result["passed"] is False
    assert result["errors"]


def test_validate_solar_term_table_passes():
    result = validate_solar_term_table({"1991": make_year(1991)})
    assert result["passed"] is True
    assert result["year_count"] == 1
