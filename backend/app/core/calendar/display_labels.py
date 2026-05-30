from __future__ import annotations

STEM_KO = {
    "甲": "갑", "乙": "을", "丙": "병", "丁": "정", "戊": "무", "己": "기", "庚": "경", "辛": "신", "壬": "임", "癸": "계",
}
BRANCH_KO = {
    "子": "자", "丑": "축", "寅": "인", "卯": "묘", "辰": "진", "巳": "사", "午": "오", "未": "미", "申": "신", "酉": "유", "戌": "술", "亥": "해",
}
UNSEONG_KO = {
    "長生": "장생", "沐浴": "목욕", "冠帶": "관대", "建祿": "건록", "帝旺": "제왕", "衰": "쇠", "病": "병", "死": "사", "墓": "묘", "絶": "절", "胎": "태", "養": "양",
}
SHINSAL_KO = {
    "劫殺": "겁살", "災殺": "재살", "天殺": "천살", "地殺": "지살", "年殺": "년살", "月殺": "월살", "亡身殺": "망신살", "將星殺": "장성살", "攀鞍殺": "반안살", "驛馬殺": "역마살", "六害殺": "육해살", "華蓋殺": "화개살",
}
TEN_GOD_KO = {
    "比肩": "비견", "劫財": "겁재", "食神": "식신", "傷官": "상관", "偏財": "편재", "正財": "정재", "偏官": "편관", "正官": "정관", "偏印": "편인", "正印": "정인", "日元": "일원",
}


def stem_to_ko(stem: str) -> str:
    return STEM_KO.get(stem, stem)


def branch_to_ko(branch: str) -> str:
    return BRANCH_KO.get(branch, branch)


def stems_to_ko(stems: list[str]) -> list[str]:
    return [stem_to_ko(stem) for stem in stems]


def localize_chart_tables(chart_result: dict) -> dict:
    return {
        "ten_gods": {k: TEN_GOD_KO.get(v, v) for k, v in chart_result.get("ten_gods", {}).items()},
        "hidden_stems": {k: stems_to_ko(v) for k, v in chart_result.get("hidden_stems", {}).items()},
        "twelve_unseong": {k: UNSEONG_KO.get(v, v) for k, v in chart_result.get("twelve_unseong", {}).items()},
        "twelve_shinsal": {
            base: {k: SHINSAL_KO.get(v, v) for k, v in table.items()}
            for base, table in chart_result.get("twelve_shinsal", {}).items()
        },
    }
