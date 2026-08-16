"""Command-line interface for Shipwright.

Style note: terminal output is concise and decision-oriented, while full evidence is
available through the selected report format.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import gate_passes, run_audit
from .models import resolve_repository
from .policy import load_policy
from .renderers import to_json, to_markdown, to_sarif


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shipwright", description="Evidence-backed release readiness for repositories.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("inspect", "Inspect a repository and emit its evidence ledger."), ("gate", "Fail when the repository is not release-ready.")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("path", nargs="?", default=".", help="Repository path (default: current directory).")
        command.add_argument("--format", choices=("markdown", "json", "sarif"), default="markdown")
        command.add_argument("--policy", help="Path to a shipwright.toml policy file.")
        command.add_argument("--output", help="Write the report to a file instead of stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repository = resolve_repository(args.path)
        policy = load_policy(repository, args.policy)
        report = run_audit(repository, policy)
        renderer = {"markdown": to_markdown, "json": to_json, "sarif": to_sarif}[args.format]
        content = renderer(report)
        if args.output:
            Path(args.output).expanduser().resolve().write_text(content, encoding="utf-8")
        else:
            print(content, end="")
        if args.command == "gate" and not gate_passes(report, policy):
            return 1
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"shipwright: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
