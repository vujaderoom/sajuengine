from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _repo_root() -> Path:
    # backend/app/core/rule_dsl/loader.py -> repo root
    return Path(__file__).resolve().parents[4]


def rules_dir(version: str = "v1.0.0") -> Path:
    return _repo_root() / "rules" / version


def load_rules(version: str = "v1.0.0") -> list[dict[str, Any]]:
    base = rules_dir(version)
    if not base.exists():
        return []

    rules: list[dict[str, Any]] = []
    for path in sorted(base.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        data["_path"] = str(path.relative_to(_repo_root()))
        rules.append(data)

    return sorted(rules, key=lambda rule: rule.get("priority", 0), reverse=True)


def summarize_rules(version: str = "v1.0.0") -> list[dict[str, Any]]:
    return [
        {
            "id": rule.get("id"),
            "title": rule.get("title"),
            "layer": rule.get("layer"),
            "target": rule.get("target"),
            "priority": rule.get("priority", 0),
            "enabled": rule.get("enabled", True),
            "status": rule.get("status"),
            "path": rule.get("_path"),
        }
        for rule in load_rules(version)
    ]
