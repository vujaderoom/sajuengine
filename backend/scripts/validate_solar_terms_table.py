from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.calendar.solar_term_table import validate_solar_term_table  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="data/solar_terms_1900_2100.json")
    args = parser.parse_args()
    path = ROOT / args.path
    data = json.loads(path.read_text(encoding="utf-8"))
    result = validate_solar_term_table(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
