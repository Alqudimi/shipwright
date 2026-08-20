"""Deterministic repository detectors.

Style note: the evidence ledger is visible in every return value; detectors never
silently infer a success and never execute repository code.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from .models import CheckResult, CheckSeverity, CheckStatus, Evidence

Detector = Callable[[Path], CheckResult]
_SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{12,}['\"]")


def _result(
    check_id: str,
    title: str,
    status: CheckStatus,
    summary: str,
    source: str,
    *,
    command: str | None = None,
    remediation: str | None = None,
    severity: CheckSeverity = CheckSeverity.INFO,
    score: int = 100,
    tags: tuple[str, ...] = (),
) -> CheckResult:
    return CheckResult(
        check_id=check_id,
        title=title,
        status=status,
        severity=severity,
        summary=summary,
        evidence=(Evidence(source=source, detail=summary, command=command),),
        remediation=remediation,
        score=score,
        tags=tags,
    )


def check_structure(repository: Path) -> CheckResult:
    required = {".gitignore", "README.md", ".github"}
    present = sorted(item for item in required if (repository / item).exists())
    missing = sorted(required - set(present))
    if missing:
        return _result(
            "structure",
            "Repository structure",
            CheckStatus.ATTENTION,
            f"Missing: {', '.join(missing)}",
            ".",
            remediation="Add the missing maintainer-facing files and automation directory.",
            severity=CheckSeverity.WARNING,
            score=40,
            tags=("maintainer",),
        )
    return _result(
        "structure",
        "Repository structure",
        CheckStatus.VERIFIED,
        "Core repository entry points are present.",
        ".",
        tags=("maintainer",),
    )


def check_documentation(repository: Path) -> CheckResult:
    readme = repository / "README.md"
    if not readme.is_file():
        return _result(
            "documentation",
            "Documentation",
            CheckStatus.BLOCKED,
            "README.md is missing.",
            "README.md",
            remediation="Write a quick-start README before publishing.",
            severity=CheckSeverity.ERROR,
            score=0,
            tags=("docs",),
        )
    lines = readme.read_text(encoding="utf-8", errors="replace").splitlines()
    headings = sum(line.startswith("#") for line in lines)
    has_install = any(
        word in readme.read_text(encoding="utf-8", errors="replace").lower()
        for word in ("install", "quick start", "getting started")
    )
    if len(lines) < 30 or headings < 3 or not has_install:
        return _result(
            "documentation",
            "Documentation",
            CheckStatus.ATTENTION,
            f"README has {len(lines)} lines and {headings} headings; installation guidance is incomplete.",
            "README.md",
            remediation="Add problem, quick start, usage, testing, security, and contribution sections.",
            severity=CheckSeverity.WARNING,
            score=55,
            tags=("docs",),
        )
    return _result(
        "documentation",
        "Documentation",
        CheckStatus.VERIFIED,
        f"README provides {headings} sections and a setup path.",
        "README.md",
        tags=("docs",),
    )


def check_tests(repository: Path) -> CheckResult:
    test_dirs = [
        path for path in (repository / "tests", repository / "test", repository / "spec") if path.is_dir()
    ]
    test_files = [path for path in repository.rglob("test_*.py") if ".git" not in path.parts]
    test_files += [path for path in repository.rglob("*.test.ts") if ".git" not in path.parts]
    if not test_dirs and not test_files:
        return _result(
            "tests",
            "Test surface",
            CheckStatus.BLOCKED,
            "No recognizable test directory or test file was found.",
            ".",
            remediation="Add unit and integration tests before cutting a release.",
            severity=CheckSeverity.ERROR,
            score=0,
            tags=("quality",),
        )
    return _result(
        "tests",
        "Test surface",
        CheckStatus.VERIFIED,
        f"Found {len(test_dirs)} test directory(s) and {len(test_files)} test file(s).",
        "tests/",
        command="pytest",
        tags=("quality",),
    )


def check_ci(repository: Path) -> CheckResult:
    workflows = repository / ".github" / "workflows"
    files = sorted(workflows.glob("*.y*ml")) if workflows.is_dir() else []
    if not files:
        return _result(
            "ci",
            "Continuous integration",
            CheckStatus.ATTENTION,
            "No GitHub Actions workflow was found.",
            ".github/workflows/",
            remediation="Add a workflow that runs formatting, type checks, tests, and build validation.",
            severity=CheckSeverity.WARNING,
            score=25,
            tags=("automation",),
        )
    return _result(
        "ci",
        "Continuous integration",
        CheckStatus.VERIFIED,
        f"Found {len(files)} workflow file(s).",
        ".github/workflows/",
        tags=("automation",),
    )


def check_license(repository: Path) -> CheckResult:
    candidates = [repository / name for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")]
    license_file = next((path for path in candidates if path.is_file()), None)
    if license_file is None:
        return _result(
            "license",
            "Open-source license",
            CheckStatus.ATTENTION,
            "No standard license file was found.",
            ".",
            remediation="Choose and commit an OSI-approved license.",
            severity=CheckSeverity.WARNING,
            score=30,
            tags=("legal",),
        )
    return _result(
        "license",
        "Open-source license",
        CheckStatus.VERIFIED,
        f"License file found at {license_file.name}.",
        license_file.name,
        tags=("legal",),
    )


def check_packaging(repository: Path) -> CheckResult:
    manifests = [
        name
        for name in ("pyproject.toml", "package.json", "Cargo.toml", "go.mod")
        if (repository / name).is_file()
    ]
    if not manifests:
        return _result(
            "packaging",
            "Build/package metadata",
            CheckStatus.ATTENTION,
            "No supported package manifest was found.",
            ".",
            remediation="Add a package manifest with a reproducible build or install command.",
            severity=CheckSeverity.WARNING,
            score=35,
            tags=("build",),
        )
    return _result(
        "packaging",
        "Build/package metadata",
        CheckStatus.VERIFIED,
        f"Detected {', '.join(manifests)}.",
        manifests[0],
        tags=("build",),
    )


def check_secret_hygiene(repository: Path) -> CheckResult:
    suspicious: list[str] = []
    ignored = {".git", ".venv", "node_modules", "dist", "build", "coverage", "tests", "test"}
    # Dependency lock files are machine-generated and never contain contributor credentials.
    ignored_names = ignored | {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
        "Gemfile.lock",
        "composer.lock",
        "Cargo.lock",
        "go.sum",
        "uv.lock",
    }
    for path in repository.rglob("*"):
        try:
            is_file = path.is_file()
        except OSError:
            continue
        if not is_file or any(part in ignored_names for part in path.parts):
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > 512_000 or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".lock"}:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if _SECRET_PATTERN.search(content):
            suspicious.append(str(path.relative_to(repository)))
    if suspicious:
        return _result(
            "secret-hygiene",
            "Secret hygiene",
            CheckStatus.BLOCKED,
            f"Potential hard-coded secret patterns found in {', '.join(suspicious[:5])}.",
            suspicious[0],
            remediation="Remove credentials, rotate exposed values, and use environment-based configuration.",
            severity=CheckSeverity.ERROR,
            score=0,
            tags=("security",),
        )
    return _result(
        "secret-hygiene",
        "Secret hygiene",
        CheckStatus.VERIFIED,
        "No high-confidence hard-coded secret pattern was detected by the conservative scan.",
        ".",
        tags=("security",),
    )


def check_changelog(repository: Path) -> CheckResult:
    candidates = ("CHANGELOG.md", "CHANGELOG.txt", "CHANGELOG", "changelog.md", "docs/CHANGELOG.md")
    changelog_file = next((name for name in candidates if (repository / name).is_file()), None)
    if changelog_file is None:
        return _result(
            "changelog",
            "Changelog",
            CheckStatus.ATTENTION,
            "No CHANGELOG file was found.",
            ".",
            remediation="Keep a CHANGELOG (see keepachangelog.com) so every release decision has a written record.",
            severity=CheckSeverity.WARNING,
            score=60,
            tags=("docs",),
        )
    return _result(
        "changelog",
        "Changelog",
        CheckStatus.VERIFIED,
        f"Changelog found at {changelog_file}.",
        changelog_file,
        tags=("docs",),
    )


DEFAULT_DETECTORS: tuple[Detector, ...] = (
    check_structure,
    check_documentation,
    check_tests,
    check_ci,
    check_license,
    check_packaging,
    check_secret_hygiene,
    check_changelog,
)
