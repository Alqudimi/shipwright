"""Error-path coverage for the Shipwright CLI.

The baseline suite asserts the success paths of `inspect` and `gate`. These
tests pin down the failure contract: malformed invocations must exit with
code 2 and a descriptive message, and the `gate` command must exit with
code 1 when the report cannot satisfy the configured policy.
"""

from pathlib import Path

import pytest

from shipwright_core.cli import main
from shipwright_core.policy import load_policy


def test_cli_missing_command_exits_with_code_two(capsys: object) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2


def test_cli_unknown_command_exits_with_code_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["bogus"])
    assert exc_info.value.code == 2


def test_cli_invalid_path_exits_with_code_two(capsys: object) -> None:
    exit_code = main(["inspect", "/nonexistent/path/abc123"])
    assert exit_code == 2


def test_cli_error_writes_to_stderr(tmp_path: Path, capsys: object) -> None:
    main(["inspect", "/nonexistent/path/abc123"])
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert captured.err.startswith("shipwright:")
    assert captured.out == ""


def test_gate_fails_when_score_below_minimum(tmp_path: Path) -> None:
    """A repository with no evidence must make `gate` exit with code 1."""
    (tmp_path / "README.md").write_text("# T\n", encoding="utf-8")
    exit_code = main(["gate", str(tmp_path), "--policy", "/dev/null"])
    assert exit_code == 1


def test_cli_sarif_format_writes_report(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Fixture\n\nA repository used to verify Shipwright evidence.\n\n## Install\n\nInstall the package.\n\n## Usage\n\nRun the CLI.\n\n## Testing\n\nTests exist here.\n\n## Security\n\nNo credentials needed.\n\n## Contributing\n\nWelcome.\n\n## License\n\nMIT.\n\nRelease evidence is reviewed before publishing.\n", encoding="utf-8")
    output = tmp_path / "report.sarif"
    assert main(["inspect", str(tmp_path), "--format", "sarif", "--output", str(output)]) == 0
    content = output.read_text(encoding="utf-8")
    assert '"version": "2.1.0"' in content


def test_policy_explicit_path_loads(tmp_path: Path) -> None:
    custom = tmp_path / "custom.toml"
    custom.write_text("[policy]\nname='release'\nminimum_score=50\n", encoding="utf-8")
    policy = load_policy(tmp_path, str(custom))
    assert policy.name == "release"
    assert policy.minimum_score == 50


def test_policy_clamps_minimum_score(tmp_path: Path) -> None:
    custom = tmp_path / "clamp.toml"
    custom.write_text("[policy]\nminimum_score=900\n", encoding="utf-8")
    assert load_policy(tmp_path, str(custom)).minimum_score == 100
