from __future__ import annotations

"""Solar term table generator scaffold.

Usage target:
    python backend/scripts/generate_solar_terms_table.py > data/solar_terms_1900_2100.json

This scaffold intentionally does not ship calculated ephemeris values. For production, wire Skyfield
longitude crossing calculation or import a verified Korean standard solar-term table, then emit:

{
  "1991": [
    {"name": "小寒", "ko": "소한", "datetime": "1991-01-06T00:00:00+09:00"},
    ... 24 terms ...
  ]
}
"""

import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.calendar.solar_terms import ALL_24_SOLAR_TERMS  # noqa: E402


def fixed_baseline_year(year: int) -> list[dict]:
    return [
        {"name": name, "ko": ko, "datetime": datetime(year, month, day).isoformat(), "source": "generated_fixed_baseline"}
        for name, ko, month, day in ALL_24_SOLAR_TERMS
    ]


def main() -> None:
    data = {str(year): fixed_baseline_year(year) for year in range(1900, 2101)}
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
