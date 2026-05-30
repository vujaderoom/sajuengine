from __future__ import annotations

"""Generate 24 solar-term table with Skyfield.

Recommended usage in Codespaces:

    cd /workspaces/sajuengine
    mkdir -p data
    python backend/scripts/generate_solar_terms_table.py --start 1900 --end 2100 --mode skyfield > data/solar_terms_1900_2100.json

Fallback/dev usage:

    python backend/scripts/generate_solar_terms_table.py --mode fixed > data/solar_terms_1900_2100.json

The generated JSON shape is:

{
  "1991": [
    {"name": "小寒", "ko": "소한", "datetime": "1991-01-06T06:28:00+09:00", "longitude": 285},
    ... 24 terms ...
  ]
}
"""

import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.calendar.solar_terms import ALL_24_SOLAR_TERMS  # noqa: E402

KST = timezone(timedelta(hours=9))

# 24절기 태양 황경. 소한 285도부터 시작해 15도 간격.
TERM_LONGITUDES = {
    "小寒": 285, "大寒": 300, "立春": 315, "雨水": 330,
    "驚蟄": 345, "春分": 0, "淸明": 15, "穀雨": 30,
    "立夏": 45, "小滿": 60, "芒種": 75, "夏至": 90,
    "小暑": 105, "大暑": 120, "立秋": 135, "處暑": 150,
    "白露": 165, "秋分": 180, "寒露": 195, "霜降": 210,
    "立冬": 225, "小雪": 240, "大雪": 255, "冬至": 270,
}


def fixed_baseline_year(year: int) -> list[dict]:
    return [
        {"name": name, "ko": ko, "datetime": datetime(year, month, day, tzinfo=KST).isoformat(), "longitude": TERM_LONGITUDES[name], "source": "generated_fixed_baseline"}
        for name, ko, month, day in ALL_24_SOLAR_TERMS
    ]


def _angle_delta(current: float, target: float) -> float:
    return (current - target + 180.0) % 360.0 - 180.0


def _sun_longitude_degrees(eph, ts, utc_dt: datetime) -> float:
    t = ts.from_datetime(utc_dt.replace(tzinfo=timezone.utc))
    earth = eph["earth"]
    sun = eph["sun"]
    apparent = earth.at(t).observe(sun).apparent()
    _lat, lon, _distance = apparent.ecliptic_latlon()
    return lon.degrees % 360.0


def _bisect_crossing(eph, ts, start_utc: datetime, end_utc: datetime, target: float) -> datetime:
    left = start_utc
    right = end_utc
    left_delta = _angle_delta(_sun_longitude_degrees(eph, ts, left), target)
    for _ in range(50):
        mid = left + (right - left) / 2
        mid_delta = _angle_delta(_sun_longitude_degrees(eph, ts, mid), target)
        if abs((right - left).total_seconds()) <= 30:
            return mid
        if left_delta * mid_delta <= 0:
            right = mid
        else:
            left = mid
            left_delta = mid_delta
    return left + (right - left) / 2


def _find_crossing_near(eph, ts, approx_kst: datetime, target: float) -> datetime:
    center_utc = approx_kst.astimezone(timezone.utc)
    start = center_utc - timedelta(days=4)
    end = center_utc + timedelta(days=4)
    step = timedelta(hours=6)
    prev = start
    prev_delta = _angle_delta(_sun_longitude_degrees(eph, ts, prev), target)
    current = prev + step
    while current <= end:
        current_delta = _angle_delta(_sun_longitude_degrees(eph, ts, current), target)
        if prev_delta == 0 or prev_delta * current_delta <= 0:
            return _bisect_crossing(eph, ts, prev, current, target).astimezone(KST)
        prev = current
        prev_delta = current_delta
        current += step
    raise RuntimeError(f"Could not find crossing near {approx_kst.isoformat()} target={target}")


def skyfield_year(year: int, ephemeris: str = "de421.bsp") -> list[dict]:
    try:
        from skyfield.api import load
    except Exception as exc:
        raise RuntimeError("skyfield is not installed. Run pip install -e backend or pip install skyfield") from exc

    ts = load.timescale()
    eph = load(ephemeris)
    result = []
    for name, ko, month, day in ALL_24_SOLAR_TERMS:
        approx = datetime(year, month, day, 12, 0, tzinfo=KST)
        crossing = _find_crossing_near(eph, ts, approx, TERM_LONGITUDES[name])
        # minute precision is enough for 만세력 경계 판단 and keeps JSON stable.
        crossing = crossing.replace(second=0, microsecond=0)
        result.append({"name": name, "ko": ko, "datetime": crossing.isoformat(), "longitude": TERM_LONGITUDES[name], "source": f"skyfield:{ephemeris}"})
    return result


def build_table(start: int, end: int, mode: str, ephemeris: str) -> dict:
    data = {}
    for year in range(start, end + 1):
        data[str(year)] = skyfield_year(year, ephemeris) if mode == "skyfield" else fixed_baseline_year(year)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1900)
    parser.add_argument("--end", type=int, default=2100)
    parser.add_argument("--mode", choices=["skyfield", "fixed"], default="skyfield")
    parser.add_argument("--ephemeris", default="de421.bsp")
    args = parser.parse_args()
    data = build_table(args.start, args.end, args.mode, args.ephemeris)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
