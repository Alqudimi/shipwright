"""Negative-branch coverage for the deterministic repository detectors.

The baseline suite exercises the happy path for each detector. These tests
pin down the decision logic when evidence is missing: every detector must
escalate deterministically (ATTENTION or BLOCKED) instead of silently
inferring success, and each escalation must carry a remediation when one
exists in the code.
"""

from pathlib import Path

from shipwright_core.detectors import (
    check_ci,
    check_documentation,
    check_license,
    check_packaging,
    check_secret_hygiene,
    check_structure,
    check_tests,
)
from shipwright_core.models import CheckStatus


def make_bare_repo(tmp_path: Path) -> Path:
    return tmp_path


def test_structure_escapes_when_entry_points_missing(tmp_path: Path) -> None:
    result = check_structure(make_bare_repo(tmp_path))
    assert result.status == CheckStatus.ATTENTION
    assert result.score == 40
    assert result.severity == "warning"
    assert "README.md" in result.summary
    assert ".gitignore" in result.summary
    assert result.remediation


def test_tests_block_when_surface_absent(tmp_path: Path) -> None:
    result = check_tests(make_bare_repo(tmp_path))
    assert result.status == CheckStatus.BLOCKED
    assert result.severity == "error"
    assert "test" in result.remediation


def test_ci_escapes_when_workflow_directory_missing(tmp_path: Path) -> None:
    result = check_ci(make_bare_repo(tmp_path))
    assert result.status == CheckStatus.ATTENTION
    assert result.score == 25


def test_license_escapes_when_no_manifest_present(tmp_path: Path) -> None:
    result = check_license(make_bare_repo(tmp_path))
    assert result.status == CheckStatus.ATTENTION
    assert result.score == 30


def test_packaging_escapes_when_no_manifest_present(tmp_path: Path) -> None:
    result = check_packaging(make_bare_repo(tmp_path))
    assert result.status == CheckStatus.ATTENTION
    assert result.score == 35


def test_packaging_accepts_alternate_manifests(tmp_path: Path) -> None:
    for manifest in ("package.json", "Cargo.toml", "go.mod"):
        (tmp_path / manifest).write_text("{}", encoding="utf-8")
        assert check_packaging(tmp_path).status == CheckStatus.VERIFIED
        (tmp_path / manifest).unlink()


def test_documentation_blocks_without_readme(tmp_path: Path) -> None:
    result = check_documentation(make_bare_repo(tmp_path))
    assert result.status == CheckStatus.BLOCKED
    assert result.score == 0
    assert result.severity == "error"
    assert "README" in result.summary
    assert result.remediation


def test_documentation_escapes_thin_readme(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Short\n\nToo small.\n", encoding="utf-8")
    result = check_documentation(tmp_path)
    assert result.status == CheckStatus.ATTENTION
    assert result.score == 55
    assert "sections" in result.remediation


def test_secret_scan_skips_large_and_binary_files(tmp_path: Path) -> None:
    """Large files and common binaries must not trigger the pattern scan."""
    large = tmp_path / "dump.log"
    large.write_bytes(b"x" * (512_000 + 1024))
    screenshot = tmp_path / "logo.png"
    screenshot.write_bytes(b"PNG header with token=1234567890abcdef")
    result = check_secret_hygiene(tmp_path)
    assert result.status == CheckStatus.VERIFIED


def test_secret_scan_finds_hidden_credentials(tmp_path: Path) -> None:
    (tmp_path / "env.txt").write_text("token='1234567890abcdef'", encoding="utf-8")
    result = check_secret_hygiene(tmp_path)
    assert result.status == CheckStatus.BLOCKED
    assert result.score == 0
    assert result.severity == "error"
    assert result.remediation
