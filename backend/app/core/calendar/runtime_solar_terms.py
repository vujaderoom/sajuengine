from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import lru_cache

from app.core.calendar.solar_terms import ALL_24_SOLAR_TERMS

KST = timezone(timedelta(hours=9))

TERM_LONGITUDES = {
    "小寒": 285, "大寒": 300, "立春": 315, "雨水": 330,
    "驚蟄": 345, "春分": 0, "淸明": 15, "穀雨": 30,
    "立夏": 45, "小滿": 60, "芒種": 75, "夏至": 90,
    "小暑": 105, "大暑": 120, "立秋": 135, "處暑": 150,
    "白露": 165, "秋分": 180, "寒露": 195, "霜降": 210,
    "立冬": 225, "小雪": 240, "大雪": 255, "冬至": 270,
}


def _angle_delta(current: float, target: float) -> float:
    return (current - target + 180.0) % 360.0 - 180.0


@lru_cache(maxsize=1)
def _skyfield_objects():
    from skyfield.api import load

    ts = load.timescale()
    eph = load("de421.bsp")
    return ts, eph


def _sun_longitude_degrees(eph, ts, utc_dt: datetime) -> float:
    t = ts.from_datetime(utc_dt.replace(tzinfo=timezone.utc))
    apparent = eph["earth"].at(t).observe(eph["sun"]).apparent()
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


@lru_cache(maxsize=256)
def runtime_skyfield_terms_for_year(year: int) -> dict:
    try:
        ts, eph = _skyfield_objects()
        terms = []
        for name, ko, month, day in ALL_24_SOLAR_TERMS:
            approx = datetime(year, month, day, 12, 0, tzinfo=KST)
            crossing = _find_crossing_near(eph, ts, approx, TERM_LONGITUDES[name]).replace(second=0, microsecond=0)
            terms.append({
                "name": name,
                "ko": ko,
                "datetime": crossing.isoformat(),
                "longitude": TERM_LONGITUDES[name],
                "source": "skyfield_runtime:de421.bsp",
            })
        return {"available": True, "terms": terms, "error": None}
    except Exception as exc:
        return {"available": False, "terms": [], "error": repr(exc)}
