"""Audit orchestration and policy enforcement.

Style note: the engine reads like a ledger—collect evidence, apply policy, return
one deterministic report. It never runs arbitrary project commands.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .detectors import DEFAULT_DETECTORS
from .models import AuditReport, CheckResult, CheckStatus
from .policy import Policy


def run_audit(repository: Path, policy: Policy) -> AuditReport:
    checks = tuple(detector(repository) for detector in DEFAULT_DETECTORS)
    checks = tuple(_apply_policy(check, policy) for check in checks)
    return AuditReport(
        repository=str(repository),
        generated_at=datetime.now(UTC).isoformat(),
        checks=checks,
        policy_name=policy.name,
    )


def _apply_policy(check: CheckResult, policy: Policy) -> CheckResult:
    if check.check_id not in policy.required_checks or check.status == CheckStatus.VERIFIED:
        return check
    return CheckResult(
        check_id=check.check_id,
        title=check.title,
        status=CheckStatus.BLOCKED,
        severity=check.severity,
        summary=f"Policy requires this check: {check.summary}",
        evidence=check.evidence,
        remediation=check.remediation,
        score=check.score,
        tags=check.tags + ("policy",),
    )


def gate_passes(report: AuditReport, policy: Policy) -> bool:
    return report.ready and report.score >= policy.minimum_score
