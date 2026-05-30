from app.core.calendar.service import calculate_chart
from app.schemas import BirthInput


def get_result(dt_text: str):
    return calculate_chart(BirthInput(birth_datetime=dt_text))


def get_chart(dt_text: str):
    return get_result(dt_text)["chart"]


def get_meta(dt_text: str):
    return get_result(dt_text)["calendar_meta"]


def test_sample_chart():
    chart = get_chart("1991-05-29T16:36:00")
    assert chart["year"] == "辛未"
    assert chart["month"] == "癸巳"
    assert chart["day"] == "己亥"
    assert chart["hour"] == "壬申"


def test_ipchun_cases():
    assert get_chart("1991-02-03T12:00:00")["year"] == "庚午"
    assert get_chart("1991-02-03T12:00:00")["month"] == "己丑"
    assert get_meta("1991-02-03T12:00:00")["solar_year_for_pillar"] == 1990
    assert get_chart("1991-02-04T12:00:00")["year"] == "辛未"
    assert get_chart("1991-02-04T12:00:00")["month"] == "庚寅"
    assert get_meta("1991-02-04T12:00:00")["solar_year_for_pillar"] == 1991


def test_lixia_cases():
    assert get_chart("1991-05-05T12:00:00")["month"] == "壬辰"
    assert get_chart("1991-05-06T12:00:00")["month"] == "癸巳"


def test_auxiliary_chart_tables_for_sample():
    result = get_result("1991-05-29T16:36:00")
    assert result["ten_gods"] == {"year": "食神", "month": "偏財", "day": "日元", "hour": "正財"}
    assert result["display_ko"]["ten_gods"] == {"year": "식신", "month": "편재", "day": "일원", "hour": "정재"}
    assert result["hidden_stems"]["year"] == ["丁", "乙", "己"]
    assert result["hidden_stems"]["month"] == ["戊", "庚", "丙"]
    assert result["hidden_stems"]["day"] == ["戊", "甲", "壬"]
    assert result["hidden_stems"]["hour"] == ["戊", "壬", "庚"]
    assert result["display_ko"]["hidden_stems"]["day"] == ["무", "갑", "임"]
    assert result["twelve_unseong"] == {"year": "冠帶", "month": "帝旺", "day": "胎", "hour": "沐浴"}
    assert result["display_ko"]["twelve_unseong"] == {"year": "관대", "month": "제왕", "day": "태", "hour": "목욕"}
    assert result["twelve_shinsal"]["year_base"] == {"year": "華蓋殺", "month": "驛馬殺", "day": "地殺", "hour": "劫殺"}
    assert result["display_ko"]["twelve_shinsal"]["year_base"] == {"year": "화개살", "month": "역마살", "day": "지살", "hour": "겁살"}
    assert result["twelve_shinsal"]["day_base"]["day"] == "地殺"


def test_precise_solar_term_hook_metadata():
    meta = get_meta("1991-05-29T16:36:00")
    assert "precise_solar_terms" in meta
    assert meta["precise_solar_terms"]["mode"] in ["fixed_korean_civil_baseline", "precise_skyfield"]
