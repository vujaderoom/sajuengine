from __future__ import annotations

ELEMENTS = ["木", "火", "土", "金", "水"]
ELEMENT_KO = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}

ELEMENT_BY_STEM = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
ELEMENT_BY_BRANCH = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

MONTH_BASE_CLIMATE = {
    "寅": {"HeatScore": -1, "MoistureScore": 0},
    "卯": {"HeatScore": 0, "MoistureScore": 0},
    "辰": {"HeatScore": 0, "MoistureScore": 1},
    "巳": {"HeatScore": 2, "MoistureScore": -1},
    "午": {"HeatScore": 3, "MoistureScore": -2},
    "未": {"HeatScore": 2, "MoistureScore": 0},
    "申": {"HeatScore": 0, "MoistureScore": 0},
    "酉": {"HeatScore": -1, "MoistureScore": -1},
    "戌": {"HeatScore": -1, "MoistureScore": -1},
    "亥": {"HeatScore": -2, "MoistureScore": 2},
    "子": {"HeatScore": -3, "MoistureScore": 3},
    "丑": {"HeatScore": -2, "MoistureScore": 2},
}

CONTROLLER_MAP = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
SUPPORT_MAP = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
CONTROLLED_BY_MAP = {v: k for k, v in CONTROLLER_MAP.items()}

ELEMENT_CHARS = {
    "木": "甲乙寅卯",
    "火": "丙丁巳午",
    "土": "戊己辰戌丑未",
    "金": "庚辛申酉",
    "水": "壬癸子亥",
}
