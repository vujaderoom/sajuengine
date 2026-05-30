from __future__ import annotations

# 지장간은 사용자 기준의 여기/중기/정기 순서로 표기한다.
# 예: 亥=戊甲壬, 申=戊壬庚, 巳=戊庚丙, 未=丁乙己
HIDDEN_STEMS = {
    "子": ["壬", "癸"],
    "丑": ["癸", "辛", "己"],
    "寅": ["戊", "丙", "甲"],
    "卯": ["甲", "乙"],
    "辰": ["乙", "癸", "戊"],
    "巳": ["戊", "庚", "丙"],
    "午": ["丙", "己", "丁"],
    "未": ["丁", "乙", "己"],
    "申": ["戊", "壬", "庚"],
    "酉": ["庚", "辛"],
    "戌": ["辛", "丁", "戊"],
    "亥": ["戊", "甲", "壬"],
}


def hidden_stems_for_branch(branch: str) -> list[str]:
    return HIDDEN_STEMS[branch]


def hidden_stems_for_chart(chart: dict[str, str]) -> dict[str, list[str]]:
    return {
        "year": hidden_stems_for_branch(chart["year"][1]),
        "month": hidden_stems_for_branch(chart["month"][1]),
        "day": hidden_stems_for_branch(chart["day"][1]),
        "hour": hidden_stems_for_branch(chart["hour"][1]),
    }
