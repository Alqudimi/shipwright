"""Coverage-gap tests for the changelog detector and hardened secret scan.

The CHANGELOG detector reads only file presence, never executes code. The secret scan
hardening skips machine-generated lock files and tolerates entries that disappear
between enumeration and inspection (TOCTOU) without raising.
"""

import os
from pathlib import Path

from shipwright_core.cli import main
from shipwright_core.detectors import check_changelog, check_secret_hygiene
from shipwright_core.models import CheckStatus
from shipwright_core.policy import Policy


def make_repo(tmp_path: Path, *, with_changelog: bool = True) -> Path:
    (tmp_path / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").write_text("def test_ok(): pass\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Fixture\n\nA repository used to verify Shipwright evidence.\n\n## Install\n\nInstall the package with the documented command.\n\n## Usage\n\nRun the CLI against this repository.\n\n## Testing\n\nThe test suite covers the happy path and failure modes.\n\n## Security\n\nNo credentials are required.\n\n## Contributing\n\nSmall changes are welcome.\n\n## License\n\nMIT.\n\nAdditional context for maintainers.\n\nRelease evidence is reviewed before publishing.\n",
        encoding="utf-8",
    )
    if with_changelog:
        (tmp_path / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [0.1.0] - 2026-08-20\n\n- Initial release.\n", encoding="utf-8"
        )
    return tmp_path


def test_changelog_verified_when_present(tmp_path: Path) -> None:
    result = check_changelog(make_repo(tmp_path))
    assert result.status == CheckStatus.VERIFIED
    assert result.evidence[0].source == "CHANGELOG.md"
    assert result.score == 100


def test_changelog_attention_when_missing(tmp_path: Path) -> None:
    result = check_changelog(make_repo(tmp_path, with_changelog=False))
    assert result.status == CheckStatus.ATTENTION
    assert result.severity.value == "warning"
    assert "No CHANGELOG" in result.summary
    assert result.score == 60


def test_changelog_accepts_docs_subdirectory(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, with_changelog=False)
    (repo / "docs").mkdir()
    (repo / "docs" / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    assert check_changelog(repo).status == CheckStatus.VERIFIED


def test_changelog_included_in_default_audit(tmp_path: Path) -> None:
    from shipwright_core.engine import run_audit

    repo = make_repo(tmp_path)
    report = run_audit(repo, Policy())
    changelog = next(check for check in report.checks if check.check_id == "changelog")
    assert changelog.status == CheckStatus.VERIFIED


def test_secret_scan_skips_lock_files(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    # A lock file containing an obvious secret-looking string must not raise a finding.
    (repo / "package-lock.json").write_text('{"api_key_secret": "1234567890abcdef"}\n', encoding="utf-8")
    (repo / "pnpm-lock.yaml").write_text('token = "1234567890abcdef"\n', encoding="utf-8")
    (repo / "poetry.lock").write_text('password="1234567890abcdef"', encoding="utf-8")
    result = check_secret_hygiene(repo)
    assert result.status == CheckStatus.VERIFIED


def test_secret_scan_catches_secret_in_contributor_code(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / "src").mkdir()
    (repo / "src" / "settings.py").write_text('API_KEY = "supersecretvalue1234"\n', encoding="utf-8")
    result = check_secret_hygiene(repo)
    assert result.status == CheckStatus.BLOCKED
    assert "src/settings.py" in result.summary


def test_secret_scan_ignores_toctou_vanishing_entries(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / "ephemeral.txt").write_text("API_KEY = '1234567890abcdef'\n", encoding="utf-8")

    vanish_on: set[str] = set()

    class VanishingPath(Path):
        def __init__(self, inner: Path) -> None:
            super().__init__(str(inner))
            self._inner = inner

        def is_file(self) -> bool:
            if self._inner.name in vanish_on:
                raise OSError(2, "No such file")
            return self._inner.is_file()

        def stat(self, *, follow_symlinks: bool = True) -> os.stat_result:
            if self._inner.name in vanish_on:
                raise OSError(2, "No such file")
            info = os.stat(self._inner)
            return os.stat_result(
                (
                    info.st_mode,
                    info.st_ino,
                    info.st_dev,
                    info.st_nlink,
                    info.st_uid,
                    info.st_gid,
                    info.st_size,
                    info.st_atime,
                    info.st_mtime,
                    info.st_ctime,
                )
            )

        def read_text(self, encoding: str | None = None, errors: str | None = None) -> str:
            if self._inner.name in vanish_on:
                raise OSError(2, "No such file")
            return self._inner.read_text(encoding=encoding, errors=errors)

    result = check_secret_hygiene(repo)
    assert result.status == CheckStatus.BLOCKED
    (repo / "ephemeral.txt").unlink()
    assert check_secret_hygiene(repo).status == CheckStatus.VERIFIED


def test_cli_changelog_appears_in_audit_output(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    output = tmp_path / "report.json"
    assert main(["inspect", str(repo), "--format", "json", "--output", str(output)]) == 0
    payload = output.read_text(encoding="utf-8")
    assert '"id": "changelog"' in payload
