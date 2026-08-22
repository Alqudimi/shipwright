# Changelog

All notable changes to Shipwright are documented here.

## [0.3.7] - 2026-08-22

### Added

- Build the wheel and sdist twice with `SOURCE_DATE_EPOCH=0` and compare SHA-256 manifests before release attestation.
- Document the deterministic-build boundary and its limitations.

## [0.3.6] - 2026-08-21

### Fixed

- Align package metadata with the release version after the v0.3.5 guard correctly rejected a stale `0.3.4` metadata value.
- Preserve the failing v0.3.5 release attempt as evidence that the version-integrity gate blocks inconsistent artifacts.

## [0.3.5] - 2026-08-21

### Added

- Verify every release artifact with `gh attestation verify` after upload.
- Enforce the repository and exact Release workflow as the provenance signer.

## [0.3.4] - 2026-08-20

### Fixed

- Align package metadata and built artifact filenames with the semantic Git tag.
- Fail the release workflow before attestation or upload when the tag and artifact versions diverge.

## [0.3.3] - 2026-08-20

### Added

- Attach built wheel and sdist files directly to the matching GitHub Release.

### Fixed

- Avoid shell template injection in the release upload step by passing GitHub context through environment variables.

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
