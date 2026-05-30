from __future__ import annotations

GAN_YINYANG = {
    "甲": "yang", "乙": "yin", "丙": "yang", "丁": "yin", "戊": "yang", "己": "yin", "庚": "yang", "辛": "yin", "壬": "yang", "癸": "yin",
}
GAN_ELEMENT = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

TEN_GODS = {
    ("same", True): "比肩",
    ("same", False): "劫財",
    ("output", True): "食神",
    ("output", False): "傷官",
    ("wealth", True): "偏財",
    ("wealth", False): "正財",
    ("officer", True): "偏官",
    ("officer", False): "正官",
    ("resource", True): "偏印",
    ("resource", False): "正印",
}


def ten_god(day_stem: str, target_stem: str) -> str:
    day_element = GAN_ELEMENT[day_stem]
    target_element = GAN_ELEMENT[target_stem]
    same_polarity = GAN_YINYANG[day_stem] == GAN_YINYANG[target_stem]

    if target_element == day_element:
        relation = "same"
    elif GENERATES[day_element] == target_element:
        relation = "output"
    elif CONTROLS[day_element] == target_element:
        relation = "wealth"
    elif CONTROLS[target_element] == day_element:
        relation = "officer"
    elif GENERATES[target_element] == day_element:
        relation = "resource"
    else:
        raise ValueError(f"invalid ten god relation: {day_stem}->{target_stem}")
    return TEN_GODS[(relation, same_polarity)]


def ten_gods_for_chart(chart: dict[str, str]) -> dict[str, str]:
    day_stem = chart["day"][0]
    return {
        "year": ten_god(day_stem, chart["year"][0]),
        "month": ten_god(day_stem, chart["month"][0]),
        "day": "日元",
        "hour": ten_god(day_stem, chart["hour"][0]),
    }
