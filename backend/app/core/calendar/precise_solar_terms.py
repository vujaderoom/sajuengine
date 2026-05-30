from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PreciseSolarTermResult:
    available: bool
    mode: str
    reason: str
    terms: list[dict]


def compute_precise_solar_terms_for_year(year: int, timezone: str = "Asia/Seoul") -> PreciseSolarTermResult:
    """Precise solar-term hook.

    현재 저장소는 외부 ephemeris 파일을 포함하지 않기 때문에 실제 절기 시각 계산은
    아직 fallback으로 처리한다. 다음 단계에서 skyfield + de421.bsp 또는 사전 생성된
    절기 시각 테이블을 붙이면 이 함수의 내부 구현만 교체하면 된다.
    """
    try:
        import skyfield  # type: ignore  # noqa: F401
    except Exception:
        return PreciseSolarTermResult(
            available=False,
            mode="fixed_korean_civil_baseline",
            reason="skyfield package or ephemeris data is not available; using fixed baseline",
            terms=[],
        )

    return PreciseSolarTermResult(
        available=False,
        mode="fixed_korean_civil_baseline",
        reason="skyfield package is available but ephemeris implementation is not wired yet",
        terms=[],
    )


def precise_mode_summary(year: int, timezone: str = "Asia/Seoul") -> dict:
    result = compute_precise_solar_terms_for_year(year, timezone)
    return {
        "available": result.available,
        "mode": result.mode,
        "reason": result.reason,
        "terms": result.terms,
    }
