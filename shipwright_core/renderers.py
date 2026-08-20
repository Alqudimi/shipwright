"""Stable report renderers for humans and CI consumers.

Style note: Markdown is formatted as an evidence dossier; SARIF stays machine-first
and points back to the exact repository source for each finding.
"""

from __future__ import annotations

import json
from typing import Any

from .models import AuditReport, CheckStatus


def to_json(report: AuditReport) -> str:
    return json.dumps(report.as_dict(), indent=2, ensure_ascii=False) + "\n"


def to_markdown(report: AuditReport) -> str:
    verdict = "READY" if report.ready else "NEEDS ATTENTION"
    lines = [
        f"# Shipwright report: {verdict}",
        "",
        f"> **{report.repository}** · score **{report.score}/100** · generated `{report.generated_at}`",
        "",
        f"**{report.verified_count} verified** · **{report.attention_count} attention** · **{report.blocked_count} blocked**",
        "",
        "## Evidence ledger",
        "",
        "| Check | Status | Score | Evidence | Next action |",
        "|---|---|---:|---|---|",
    ]
    for check in report.checks:
        evidence = "; ".join(item.source for item in check.evidence)
        action = check.remediation or "No action required."
        lines.append(f"| `{check.check_id}` | `{check.status}` | {check.score} | `{evidence}` | {action} |")
    lines.extend(["", "## Check details", ""])
    for check in report.checks:
        lines.extend(
            [f"### {check.title}", "", f"**Status:** `{check.status}`  ", f"**Summary:** {check.summary}", ""]
        )
        for item in check.evidence:
            command = f" · `{item.command}`" if item.command else ""
            lines.append(f"- `{item.source}` — {item.detail}{command}")
        if check.remediation:
            lines.extend(["", f"**Remediation:** {check.remediation}"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def to_sarif(report: AuditReport) -> str:
    results: list[dict[str, Any]] = []
    rules: list[dict[str, Any]] = []
    for check in report.checks:
        if check.status == CheckStatus.VERIFIED:
            continue
        level = "error" if check.status == CheckStatus.BLOCKED else "warning"
        rules.append(
            {
                "id": check.check_id,
                "shortDescription": {"text": check.title},
                "fullDescription": {"text": check.summary},
                "help": {"text": check.remediation or "No remediation required."},
            }
        )
        results.append(
            {
                "ruleId": check.check_id,
                "level": level,
                "message": {"text": check.summary},
                "locations": [
                    {"physicalLocation": {"artifactLocation": {"uri": item.source, "uriBaseId": "%SRCROOT%"}}}
                    for item in check.evidence
                ],
            }
        )
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "Shipwright", "version": report.tool_version, "rules": rules}},
                "results": results,
            }
        ],
    }
    return json.dumps(payload, indent=2) + "\n"
