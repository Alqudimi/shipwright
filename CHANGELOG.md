# Changelog

All notable changes to Shipwright are documented here.

## [Unreleased]

### Added

- New `changelog` detector that reports whether a `CHANGELOG` file exists, following the keep-a-changelog convention.
- Secret-hygiene scan now ignores machine-generated dependency lock files (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Gemfile.lock`, `composer.lock`, `Cargo.lock`, `go.sum`, `uv.lock`) so contributors are never flagged by artifact content.
- Secret-hygiene scan now tolerates entries that disappear between enumeration and inspection (time-of-check/time-of-use races) instead of crashing the audit.

## [0.3.2] - 2026-08-19

### Fixed

- Use the official `attest-build-provenance` wrapper so tag releases generate the default SLSA build provenance predicate.
- Keep the release path pinned and avoid custom predicate configuration for standard build provenance.

## [0.3.1] - 2026-08-19

### Fixed

- Declared the SLSA v1 provenance predicate required by the GitHub attestation action.
- Added regression verification for the tag-triggered release workflow after the first v0.3.0 attestation attempt failed at that input validation step.

## [0.3.0] - 2026-08-19

### Added

- Release workflow for semantic-version tags.
- OIDC-backed signed artifact provenance attestations for sdist and wheel outputs.
- Consumer verification and future PyPI Trusted Publishing documentation.

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
