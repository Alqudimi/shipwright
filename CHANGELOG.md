# Changelog

All notable changes to Shipwright are documented here.

## [0.2.0] - 2026-08-17

### Added

- Non-root Docker image and `.dockerignore` for containerized inspection.
- Scheduled and pull-request security workflows using `pip-audit` and offline `zizmor`.
- Pinned GitHub Actions by commit SHA with checkout credential persistence disabled.
- SARIF rule metadata, remediation help, and `%SRCROOT%` artifact locations.
- Contributor PR guidance and bug/feature issue templates.
- Regression coverage for the SARIF contract and documented hardening rationale.

## [0.1.0] - 2026-08-16

### Added

- Evidence-backed repository audit engine.
- Deterministic checks for structure, documentation, tests, CI, license, packaging, and secret hygiene.
- `inspect` and `gate` CLI commands.
- JSON, Markdown, and SARIF report renderers.
- TOML policy support with required checks and minimum score.
- Fixture-based tests and GitHub Actions validation.
