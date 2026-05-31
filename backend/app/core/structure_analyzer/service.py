from __future__ import annotations

from app.core.extensions.balance import calculate_balance_extension
from app.core.structure_analyzer.binding import calculate_binding
from app.core.structure_analyzer.climate import calculate_climate
from app.core.structure_analyzer.concentration import calculate_concentration
from app.core.structure_analyzer.disease import determine_disease_and_depth, determine_medicine_and_yongshin
from app.core.structure_analyzer.utils import chart_parts, count_elements


def analyze_structure(chart_payload: dict) -> dict:
    chart = chart_payload["chart"]
    relations = chart_payload.get("relations", {"items": [], "summary": {}, "by_kind": {}})
    stems, branches = chart_parts(chart)
    element_counts = count_elements(stems, branches)
    climate = calculate_climate(chart, stems, branches, relations, element_counts)
    binding = calculate_binding(relations, element_counts)
    concentration = calculate_concentration(chart, element_counts, binding)
    disease = determine_disease_and_depth(climate, binding, concentration)
    medicine_yongshin = determine_medicine_and_yongshin(climate, disease, concentration)
    balance = calculate_balance_extension(chart, stems, branches, element_counts, binding, climate, concentration)

    delta_inputs = {
        "base_depth": disease["Depth"],
        "climate": {
            "HeatScore": climate["HeatScore"],
            "MoistureScore": climate["MoistureScore"],
            "EWMScore": climate["EWMScore"],
            "temperature": climate["temperature"],
            "humidity": climate["humidity"],
            "tags": climate.get("tags", []),
        },
        "binding": {
            "bindings": binding.get("bindings", []),
            "BindingStrength": binding.get("BindingStrength", 0),
            "transformation": binding.get("transformation", False),
        },
        "concentration": {
            "CI": concentration.get("CI", 0),
            "level": concentration.get("level", "낮음"),
            "dominant_element": concentration.get("dominant_element"),
            "metal_absent": concentration.get("metal_absent", False),
        },
        "diseases": {
            "core": disease.get("core"),
            "core_detail": disease.get("core_detail"),
            "derived": disease.get("derived", []),
            "DepthScore": disease.get("DepthScore"),
        },
        "medicines": medicine_yongshin.get("medicines", []),
        "yongshin": medicine_yongshin.get("yongshin", {}),
        "extension": {"balance": balance},
    }

    return {
        "model_version": "structure_analyzer_v1.0.0",
        "chart": chart,
        "stems": stems,
        "branches": branches,
        "element_counts": element_counts,
        "climate": climate,
        "binding": binding,
        "concentration": concentration,
        "disease": disease,
        "medicine_yongshin": medicine_yongshin,
        "DeltaInputs": delta_inputs,
        "layer_protocol": {
            "L2": "원국 구조 확정 및 DeltaInputs 생성",
            "L1": "DeltaInputs 기반 운 Δ 계산",
            "extension_rule": "확장 모듈은 DeltaInputs.extension 하위에만 기록하고 병/약/용신을 직접 수정하지 않음",
        },
    }
