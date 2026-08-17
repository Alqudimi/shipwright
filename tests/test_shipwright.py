"""Behavioral tests for the evidence ledger."""

from pathlib import Path

from shipwright_core.cli import main
from shipwright_core.engine import gate_passes, run_audit
from shipwright_core.models import CheckStatus
from shipwright_core.policy import Policy, load_policy
from shipwright_core.renderers import to_json, to_markdown, to_sarif


def make_repo(tmp_path: Path, *, complete: bool = True) -> Path:
    (tmp_path / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").write_text("def test_ok(): pass\n", encoding="utf-8")
    if complete:
        (tmp_path / "README.md").write_text("# Fixture\n\nA repository used to verify Shipwright evidence.\n\n## Install\n\nInstall the package with the documented command.\n\n## Usage\n\nRun the CLI against this repository.\n\n## Testing\n\nThe test suite covers the happy path and failure modes.\n\n## Security\n\nNo credentials are required.\n\n## Contributing\n\nSmall changes are welcome.\n\n## License\n\nMIT.\n\nAdditional context for maintainers.\n\nRelease evidence is reviewed before publishing.\n", encoding="utf-8")
    return tmp_path


def test_complete_repository_is_ready(tmp_path: Path) -> None:
    report = run_audit(make_repo(tmp_path), Policy(minimum_score=80))
    assert report.ready
    assert report.score >= 80
    assert report.verified_count == len(report.checks)
    assert gate_passes(report, Policy(minimum_score=80))


def test_missing_readme_blocks_and_gate_fails(tmp_path: Path) -> None:
    report = run_audit(make_repo(tmp_path, complete=False), Policy(required_checks=frozenset({"documentation"})))
    documentation = next(check for check in report.checks if check.check_id == "documentation")
    assert documentation.status == CheckStatus.BLOCKED
    assert not gate_passes(report, Policy(required_checks=frozenset({"documentation"})))


def test_renderers_emit_contracts(tmp_path: Path) -> None:
    report = run_audit(make_repo(tmp_path, complete=False), Policy())
    assert '"checks"' in to_json(report)
    assert "Evidence ledger" in to_markdown(report)
    sarif = to_sarif(report)
    assert '"version": "2.1.0"' in sarif
    assert '"rules"' in sarif
    assert '"uriBaseId": "%SRCROOT%"' in sarif


def test_secret_scan_blocks_high_confidence_pattern(tmp_path: Path) -> None:
    make_repo(tmp_path)
    (tmp_path / "config.py").write_text("API_KEY = '1234567890abcdef'\n", encoding="utf-8")
    report = run_audit(tmp_path, Policy())
    secret = next(check for check in report.checks if check.check_id == "secret-hygiene")
    assert secret.status == CheckStatus.BLOCKED


def test_policy_file_is_loaded(tmp_path: Path) -> None:
    make_repo(tmp_path)
    (tmp_path / "shipwright.toml").write_text("[policy]\nname='strict'\nminimum_score=91\nrequired_checks=['tests']\n", encoding="utf-8")
    policy = load_policy(tmp_path)
    assert policy.name == "strict"
    assert policy.minimum_score == 91
    assert "tests" in policy.required_checks


def test_cli_writes_json_and_gate_returns_success(tmp_path: Path) -> None:
    make_repo(tmp_path)
    output = tmp_path / "report.json"
    assert main(["inspect", str(tmp_path), "--format", "json", "--output", str(output)]) == 0
    assert '"checks"' in output.read_text(encoding="utf-8")
    assert main(["gate", str(tmp_path), "--format", "json"]) == 0
