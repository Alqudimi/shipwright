"""Evidence-first domain models for Shipwright.

Style note: this module follows the Evidence Ledger direction—small, explicit records
that make every release decision traceable to an inspectable source.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class CheckStatus(StrEnum):
    VERIFIED = "verified"
    ATTENTION = "attention"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class CheckSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Evidence:
    """A fact that lets a maintainer reproduce or inspect a check."""

    source: str
    detail: str
    command: str | None = None


@dataclass(frozen=True, slots=True)
class CheckResult:
    """One deterministic repository contract check."""

    check_id: str
    title: str
    status: CheckStatus
    severity: CheckSeverity
    summary: str
    evidence: tuple[Evidence, ...] = ()
    remediation: str | None = None
    score: int = 0
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AuditReport:
    """Immutable report emitted by the audit engine."""

    repository: str
    generated_at: str
    checks: tuple[CheckResult, ...]
    policy_name: str = "default"
    tool_version: str = "0.1.0"

    @property
    def verified_count(self) -> int:
        return sum(check.status == CheckStatus.VERIFIED for check in self.checks)

    @property
    def attention_count(self) -> int:
        return sum(check.status == CheckStatus.ATTENTION for check in self.checks)

    @property
    def blocked_count(self) -> int:
        return sum(check.status == CheckStatus.BLOCKED for check in self.checks)

    @property
    def score(self) -> int:
        if not self.checks:
            return 0
        return round(sum(check.score for check in self.checks) / len(self.checks))

    @property
    def ready(self) -> bool:
        return self.blocked_count == 0 and self.attention_count == 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "repository": self.repository,
            "generated_at": self.generated_at,
            "policy": self.policy_name,
            "tool_version": self.tool_version,
            "verdict": "ready" if self.ready else "needs-attention",
            "score": self.score,
            "summary": {
                "verified": self.verified_count,
                "attention": self.attention_count,
                "blocked": self.blocked_count,
                "total": len(self.checks),
            },
            "checks": [
                {
                    "id": check.check_id,
                    "title": check.title,
                    "status": check.status,
                    "severity": check.severity,
                    "summary": check.summary,
                    "score": check.score,
                    "tags": list(check.tags),
                    "remediation": check.remediation,
                    "evidence": [
                        {"source": item.source, "detail": item.detail, "command": item.command}
                        for item in check.evidence
                    ],
                }
                for check in self.checks
            ],
        }


def resolve_repository(path: str) -> Path:
    """Resolve and validate a repository path without following files outside it."""

    repository = Path(path).expanduser().resolve()
    if not repository.is_dir():
        raise ValueError(f"Repository path is not a directory: {path}")
    return repository
