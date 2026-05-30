from app.core.calendar.service import calculate_chart
from app.schemas import BirthInput


def get_result(dt_text: str, sex: str = "male"):
    return calculate_chart(BirthInput(birth_datetime=dt_text, sex=sex))


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


def test_calendar_relations_for_sample():
    result = get_result("1991-05-29T16:36:00")
    relation_names = [item["name"] for item in result["relations"]["items"]]
    assert "巳亥沖" in relation_names
    assert "巳申合" in relation_names
    assert "申亥害" in relation_names
    assert result["relations"]["summary"]["has_clash"] is True
    assert result["relations"]["summary"]["has_liuhe"] is True
    assert result["manseryuk_view"]["relations"]["summary"]["has_harm"] is True


def test_daewoon_for_sample_male_yin_year():
    result = get_result("1991-05-29T16:36:00", sex="male")
    daewoon = result["daewoon"]
    assert daewoon["direction"]["direction"] == "backward"
    assert daewoon["base_month_pillar"] == "癸巳"
    assert daewoon["cycles"][0]["pillar"] == "壬辰"
    assert len(daewoon["cycles"]) == 10
    assert daewoon["start"]["start_age_decimal"] > 0


def test_sewoon_and_manseryuk_rows():
    result = get_result("1991-05-29T16:36:00", sex="male")
    sewoon = result["sewoon"]
    assert len(sewoon["years"]) == 11
    assert sewoon["current"] is not None
    assert "relations_with_origin" in sewoon["years"][0]
    rows = result["manseryuk_view"]["rows"]
    assert rows[0]["label"] == "천간 십성"
    assert any(row["key"] == "relative_xunkong" for row in rows)


def test_fortune_overlay_for_sample():
    chart_result = get_result("1991-05-29T16:36:00", sex="male")
    from app.core.fact_builder.service import build_fact
    from app.core.fortune.analysis import analyze_fortune

    facts = build_fact(chart_result)
    fortune = analyze_fortune(chart_result, facts)
    overlay = fortune["overlay_result"]
    assert overlay["model_version"] == "fortune_overlay_v1.0.0"
    assert "combined_overlay" in overlay["current"]
    assert "scores" in overlay["current"]["combined_overlay"]
    assert "yongshin_score" in overlay["current"]["combined_overlay"]["scores"]
    assert "gishin_score" in overlay["current"]["combined_overlay"]["scores"]
    assert isinstance(overlay["current"]["combined_overlay"]["relations"], list)


def test_solar_term_table_status_metadata():
    meta = get_meta("1991-05-29T16:36:00")
    assert meta["solar_term_mode"] in ["fixed_korean_civil_baseline", "solar_term_table", "skyfield_runtime"]
    assert "solar_terms" in meta
    assert "solar_term_table_status" in meta
    assert meta["solar_term_table_status"]["mode"] in ["fixed_korean_civil_baseline", "solar_term_table", "skyfield_runtime"]


def test_precise_solar_term_hook_metadata():
    meta = get_meta("1991-05-29T16:36:00")
    assert "precise_solar_terms" in meta
    assert meta["precise_solar_terms"]["mode"] in ["fixed_korean_civil_baseline", "precise_skyfield"]
