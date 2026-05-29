from __future__ import annotations

import operator
from typing import Any

OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
}


def resolve_path(context: dict[str, Any], dotted_path: str) -> Any:
    current: Any = context
    for part in dotted_path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
    return current


def parse_value(value: str) -> Any:
    value = value.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "null":
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def evaluate_condition(condition: str, context: dict[str, Any]) -> dict[str, Any]:
    for op_text, op_func in OPERATORS.items():
        token = f" {op_text} "
        if token in condition:
            left_text, right_text = condition.split(token, 1)
            left_value = resolve_path(context, left_text.strip())
            right_value = parse_value(right_text)
            result = op_func(left_value, right_value)
            return {
                "condition": condition,
                "left": left_text.strip(),
                "operator": op_text,
                "right": right_value,
                "actual": left_value,
                "result": result,
            }

    return {
        "condition": condition,
        "left": condition,
        "operator": None,
        "right": None,
        "actual": None,
        "result": False,
        "error": "unsupported_condition",
    }


def evaluate_when(when: dict[str, Any] | None, context: dict[str, Any]) -> dict[str, Any]:
    if not when:
        return {"result": True, "items": []}

    if "all" in when:
        items = [evaluate_condition(condition, context) for condition in when.get("all", [])]
        return {"result": all(item["result"] for item in items), "mode": "all", "items": items}

    if "any" in when:
        items = [evaluate_condition(condition, context) for condition in when.get("any", [])]
        return {"result": any(item["result"] for item in items), "mode": "any", "items": items}

    return {"result": False, "items": [], "error": "unsupported_when"}
