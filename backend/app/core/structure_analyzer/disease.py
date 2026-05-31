from __future__ import annotations


def determine_disease_and_depth(climate: dict, binding: dict, concentration: dict, facts_hint: dict | None = None) -> dict:
    heat = climate.get("HeatScore", 0)
    moisture = climate.get("MoistureScore", 0)
    ewm = climate.get("EWMScore", 0)
    ci = concentration.get("CI", 0)
    bs = binding.get("BindingStrength", 0)
    metal_absent = concentration.get("metal_absent", False)
    tags = list(climate.get("tags", []))

    core = "기후형"
    core_detail = "기후형 병"
    derived: list[str] = []
    reason = "HeatScore/MoistureScore 기반 기후 불균형"

    if moisture >= 2:
        core = "기후형"
        core_detail = "기후형(수습 과다·침수)"
        reason = "MoistureScore 과습 및 EWM 작동성으로 수습 과다 구조"
    elif heat >= 2 and moisture <= -2:
        core = "기후형"
        core_detail = "기후형(조열·건조)"
        reason = "HeatScore 조열 + MoistureScore 건조"
    elif bs >= 2 and ci >= 4:
        core = "유통 차단형"
        core_detail = "유통 차단형 병"
        reason = "BindingStrength와 CI가 높아 유통 경로 단일화/차단 가능성"
    elif ci >= 4:
        core = "용도 상실형"
        core_detail = "용도 상실형 병"
        reason = "특정 오행 결집도가 높아 기능 편향 가능성"

    if bs >= 2 and core != "유통 차단형":
        derived.append("유통 차단형")
    if ci >= 4 and core != "용도 상실형":
        derived.append("용도 상실형")
    if metal_absent and "유통 차단형" not in derived and core != "유통 차단형":
        derived.append("유통 차단형")

    depth_score = 0
    depth_reasons: list[str] = []
    if abs(heat) >= 2:
        depth_score += 1
        depth_reasons.append("HeatScore 절대값 ≥2")
    if abs(moisture) >= 2:
        depth_score += 1
        depth_reasons.append("MoistureScore 절대값 ≥2")
    if ewm <= 1:
        depth_score += 1
        depth_reasons.append("EWMScore 0~1")
    if ci >= 4:
        depth_score += 1
        depth_reasons.append("CI ≥4")
    if bs >= 2:
        depth_score += 1
        depth_reasons.append("BindingStrength ≥2")
    if metal_absent and "유통 차단형" in derived:
        depth_score += 1
        depth_reasons.append("금 부재 + 유통 차단 파생 병")

    if depth_score <= 1:
        depth = 1
    elif depth_score <= 3:
        depth = 2
    elif depth_score <= 5:
        depth = 3
    else:
        depth = 4

    collapse_tags = ["storage_collapse", "flow_collapse", "sudden_transition"]
    limited_reason = None
    if depth == 4 and not any(tag in tags for tag in collapse_tags):
        depth = 3
        limited_reason = "Depth4는 저장 파열/유통 붕괴/급전환 증거 태그가 필요하여 최대 3으로 제한"

    return {
        "core": core,
        "core_detail": core_detail,
        "derived": derived,
        "reason": reason,
        "DepthScore": min(depth_score, 6),
        "Depth": depth,
        "depth_reasons": depth_reasons,
        "depth_limited_reason": limited_reason,
    }


def determine_medicine_and_yongshin(climate: dict, disease: dict, concentration: dict) -> dict:
    heat = climate.get("HeatScore", 0)
    moisture = climate.get("MoistureScore", 0)
    ewm = climate.get("EWMScore", 0)
    core_detail = disease.get("core_detail", "")

    if "수습 과다" in core_detail or moisture >= 2:
        medicine = {"type": "기후 복원형", "grade": "A", "freedom": "작동", "name": "말림·건조·증발", "action": "drying_evaporation"}
        yongshin = {"element": "火", "validation_passed": True, "secondary": ["巳火", "午火", "丙火", "丁火"]}
    elif "조열" in core_detail or (heat >= 2 and moisture <= -2):
        freedom = "상실" if ewm <= 1 else "작동"
        medicine = {"type": "기후 복원형", "grade": "B" if freedom == "작동" else "C", "freedom": freedom, "name": "수분 회복", "action": "moisture_recovery"}
        yongshin = {"element": "水", "validation_passed": freedom == "작동", "secondary": ["金"] if concentration.get("metal_absent") is False else []}
    elif disease.get("core") == "유통 차단형":
        medicine = {"type": "유통 개통형", "grade": "B", "freedom": "작동", "name": "유통 개통", "action": "opening_flow"}
        yongshin = {"element": "金", "validation_passed": True, "secondary": []}
    else:
        medicine = {"type": "용도 재설정형", "grade": "C", "freedom": "제한", "name": "기능 재배치", "action": "functional_reassignment"}
        yongshin = {"element": concentration.get("dominant_element", "土"), "validation_passed": False, "secondary": []}

    return {"medicines": [medicine], "yongshin": yongshin}
