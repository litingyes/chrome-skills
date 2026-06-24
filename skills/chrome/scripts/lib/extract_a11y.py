"""Accessibility tree extraction and basic a11y rule checks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .cdp import _with_page_session

INTERACTIVE_ROLES = {
    "button",
    "link",
    "checkbox",
    "radio",
    "textbox",
    "combobox",
    "menuitem",
    "tab",
    "switch",
    "slider",
}


def _check_a11y_issues(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []

    landmarks = [n for n in nodes if n["role"] in ("main", "navigation", "banner", "contentinfo")]
    if not any(n["role"] == "main" for n in landmarks):
        issues.append(
            {
                "rule": "a11y.landmark.main",
                "severity": "warn",
                "message": "No main landmark found",
                "selector": None,
            }
        )

    for node in nodes:
        role = node["role"]
        name = (node.get("name") or "").strip()
        if role in INTERACTIVE_ROLES and not name:
            issues.append(
                {
                    "rule": "a11y.name.missing",
                    "severity": "error",
                    "message": f'Interactive element role="{role}" has no accessible name',
                    "selector": f'[data-node-id="{node.get("nodeId")}"]',
                }
            )

    headings = [n for n in nodes if n["role"] == "heading"]
    if not headings:
        issues.append(
            {
                "rule": "a11y.heading.missing",
                "severity": "info",
                "message": "No headings found in accessibility tree",
                "selector": None,
            }
        )

    return issues


async def extract_a11y(session_id: str) -> dict[str, Any]:
    client, _ = await _with_page_session(session_id)
    try:
        await client.call("Accessibility.enable")
        result = await client.call("Accessibility.getFullAXTree")
        nodes_raw = result.get("nodes", [])
        if not nodes_raw:
            tree = await client.call("Accessibility.getFullAXTree", {})
            nodes_raw = tree.get("nodes", [])

        flat: list[dict[str, Any]] = []
        for ax_node in nodes_raw:
            role = ax_node.get("role", {}).get("value", "")
            if ax_node.get("ignored"):
                continue
            name = ax_node.get("name", {}).get("value", "")
            flat.append(
                {
                    "role": role,
                    "name": name,
                    "nodeId": ax_node.get("nodeId"),
                    "backendDOMNodeId": ax_node.get("backendDOMNodeId"),
                }
            )

        issues = _check_a11y_issues(flat)
        return {
            "command": "extract",
            "mode": "a11y",
            "nodes": flat[:200],
            "node_count": len(flat),
            "issues": issues,
            "issue_count": len(issues),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "error": None,
        }
    finally:
        await client.close()
