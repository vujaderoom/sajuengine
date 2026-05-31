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
    for path in sorted(base.rglob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        raw = path.read_text(encoding="utf-8")
        data["_path"] = str(path.relative_to(_repo_root()))
        data["_raw_yaml"] = raw
        rules.append(data)

    return sorted(rules, key=lambda rule: rule.get("priority", 0), reverse=True)


def get_rule(rule_id: str, version: str = "v1.0.0") -> dict[str, Any] | None:
    for rule in load_rules(version):
        if rule.get("id") == rule_id:
            return rule
    return None


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


def detail_rule(rule_id: str, version: str = "v1.0.0") -> dict[str, Any] | None:
    rule = get_rule(rule_id, version)
    if not rule:
        return None

    return {
        "rule_version": version,
        "id": rule.get("id"),
        "title": rule.get("title"),
        "layer": rule.get("layer"),
        "target": rule.get("target"),
        "priority": rule.get("priority", 0),
        "enabled": rule.get("enabled", True),
        "status": rule.get("status"),
        "path": rule.get("_path"),
        "when": rule.get("when", {}),
        "then": rule.get("then", {}),
        "score": rule.get("score", {}),
        "counter_rules": rule.get("counter_rules", []),
        "explain": rule.get("explain", {}),
        "evidence_query": rule.get("evidence_query", {}),
        "raw_yaml": rule.get("_raw_yaml", ""),
    }
