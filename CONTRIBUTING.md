# Contributing to Shipwright

Thank you for improving Shipwright. The project values small, inspectable changes that make release evidence more trustworthy.

## Before you start

Read the README and architecture note. For a new detector, define what evidence it reads, what it never executes, the failure mode, and the remediation a maintainer should take.

## Development loop

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
ruff check .
mypy shipwright_core
```

## Pull requests

Use a focused branch and a Conventional Commit-style title such as `feat: add changelog detector` or `fix: bound text scanning`. New behavior must include a fixture-based regression test and documentation when the CLI contract changes. Avoid adding a dependency when a standard-library implementation is sufficient; if a dependency is justified, document its security and maintenance rationale.

## Design expectations

Detectors must be deterministic, side-effect free, conservative with untrusted files, and return evidence paths. Do not add network calls, shell execution, or credential handling to the core audit path. Keep output schemas backward compatible or document a versioned change.
