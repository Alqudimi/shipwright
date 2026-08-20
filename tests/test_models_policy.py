"""Coverage for domain-model edges and policy fallbacks.

The baseline suite verifies the populated model paths. These tests pin down
the edge behaviour: an audit with no checks must never inflate a score, a
non-directory path must be rejected before any detector runs, and policy
loading must degrade gracefully when the TOML file is absent.
"""

from pathlib import Path

from shipwright_core.models import AuditReport, resolve_repository
from shipwright_core.policy import Policy, load_policy


def test_empty_report_scores_zero() -> None:
    """An audit with no checks must never inflate a score.

    Note: `ready` stays True for an empty check set (nothing was blocked),
    so the score floor is the only hard contract here.
    """
    report = AuditReport(repository=".", generated_at="", checks=())
    assert report.score == 0
    assert report.verified_count == 0
    assert report.as_dict()["verdict"] == "ready"


def test_resolve_repository_rejects_non_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "not-a-directory.txt"
    file_path.write_text("x", encoding="utf-8")
    try:
        resolve_repository(str(file_path))
    except ValueError as error:
        assert "not a directory" in str(error)
    else:
        raise AssertionError("resolve_repository must reject a file path")


def test_resolve_repository_accepts_directory(tmp_path: Path) -> None:
    assert resolve_repository(str(tmp_path)) == tmp_path


def test_default_policy_has_safe_values() -> None:
    default = Policy()
    assert default.name == "default"
    assert default.minimum_score == 80
    assert default.include_optional is True
    assert default.required_checks == frozenset()


def test_load_policy_returns_default_when_absent(tmp_path: Path) -> None:
    assert load_policy(tmp_path).name == "default"


def test_policy_unknown_keys_are_ignored(tmp_path: Path) -> None:
    custom = tmp_path / "extra.toml"
    custom.write_text("[policy]\nname='x'\nunknown_key='ignored'\n", encoding="utf-8")
    policy = load_policy(tmp_path, str(custom))
    assert policy.name == "x"
