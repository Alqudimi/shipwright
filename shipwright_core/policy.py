"""Policy-as-code loading for Shipwright.

Style note: the policy surface is deliberately editorial and legible—maintainers
should be able to understand a gate without reading implementation details.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    tomllib = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class Policy:
    name: str = "default"
    required_checks: frozenset[str] = frozenset()
    minimum_score: int = 80
    include_optional: bool = True


def load_policy(repository: Path, explicit_path: str | None = None) -> Policy:
    """Load a local TOML policy, falling back to safe defaults."""

    candidate = Path(explicit_path).expanduser() if explicit_path else repository / "shipwright.toml"
    if not candidate.is_file():
        return Policy()
    if tomllib is None:
        raise RuntimeError("TOML policy files require Python 3.11 or the tomli package")
    with candidate.open("rb") as stream:
        raw: dict[str, Any] = tomllib.load(stream)
    section = raw.get("policy", raw)
    required = section.get("required_checks", [])
    return Policy(
        name=str(section.get("name", candidate.stem)),
        required_checks=frozenset(str(item) for item in required),
        minimum_score=max(0, min(100, int(section.get("minimum_score", 80)))),
        include_optional=bool(section.get("include_optional", True)),
    )
