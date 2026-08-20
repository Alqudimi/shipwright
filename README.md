# Shipwright

> **Know what is ready before the tag exists.**

Shipwright is a local-first repository release-readiness auditor. It inspects the evidence already present in a codebase—tests, documentation, CI, packaging, licensing, and secret hygiene—and turns it into a deterministic verdict for maintainers and CI.

[![CI](https://github.com/Alqudimi/shipwright/actions/workflows/ci.yml/badge.svg)](https://github.com/Alqudimi/shipwright/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-C65D38.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-1F2937.svg)](pyproject.toml)
[![Security](https://img.shields.io/badge/security-pip--audit%20%2B%20zizmor-3D765C.svg)](.github/workflows/security.yml)

## Why Shipwright exists

Repository quality is usually split across a linter, a test runner, a security scanner, a README, and a handful of CI files. A green build can still ship with no license, no installation path, no regression tests, or an accidentally committed credential. Shipwright does not replace those tools. It provides the missing maintainer-facing contract: **what was checked, what evidence supports it, and what must happen before release**.

It is intentionally local-first. Shipwright does not execute repository code, upload source files, or require a database. The result is a portable JSON document, a human-readable evidence dossier, or SARIF for GitHub Code Scanning.

## What it checks

| Signal | Example evidence | Output |
|---|---|---|
| Repository structure | `.gitignore`, `README.md`, `.github/` | Verified or actionable gap |
| Documentation | README length, headings, setup language | Evidence path and remediation |
| Test surface | `tests/`, `test_*.py`, `*.test.ts` | Test discovery evidence |
| Continuous integration | GitHub Actions workflow files | CI presence |
| Open-source readiness | LICENSE/COPYING | License evidence |
| Build metadata | `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod` | Package contract |
| Secret hygiene | Conservative high-confidence literal scan | Blocker with file path |
| Release metadata | CHANGELOG presence in the tree | Changelog evidence or attention |

## Quick start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
shipwright inspect .
```

Inspect a repository from anywhere:

```bash
shipwright inspect ~/src/project --format markdown
shipwright inspect ~/src/project --format json --output report.json
shipwright inspect ~/src/project --format sarif --output shipwright.sarif
```

Use `gate` in CI. It returns exit code `1` when a repository is not ready and `2` for an invocation/configuration error:

```bash
shipwright gate . --format markdown
```

## Policy as code

Create `shipwright.toml` in the repository when the default contract needs to be stricter:

```toml
[policy]
name = "public-release"
minimum_score = 90
required_checks = ["documentation", "tests", "ci", "license", "secret-hygiene"]
include_optional = true
```

Policies make the decision reviewable. They do not silently run arbitrary commands; Shipwright only inspects the repository and records the requested contract.

## Output formats

Markdown is designed for a pull request or release checklist. JSON is the stable integration contract for dashboards and automation. SARIF contains non-verified findings with repository-relative evidence locations and can be uploaded to GitHub Code Scanning.

## Architecture

```text
                   +----------------+
 repository path ->|  CLI / config  |
                   +--------+-------+
                            |
                   +--------v-------+
                   | Audit engine   |  deterministic orchestration
                   +--------+-------+
                            |
        +-------------------+-------------------+
        |                   |                   |
   structure          docs/tests/CI       license/secrets
        +-------------------+-------------------+
                            |
                   +--------v-------+
                   | Evidence model |
                   +--------+-------+
                            |
                 JSON / Markdown / SARIF
```

The core package is framework-independent: domain models do not know about Click, GitHub, or a database. Detectors are small functions returning `CheckResult` records. New checks and future providers can be added without changing the output contract.

## Container quick start

The CLI can run in a minimal non-root container without installing Python locally:

```bash
docker build -t shipwright .
docker run --rm -v "$PWD:/workspace:ro" -w /workspace shipwright inspect .
```

The image is intentionally read-only from the inspected repository’s perspective and does not execute project code.

## Development

```bash
python -m pytest
ruff check .
mypy shipwright_core
python -m build
```

The test suite uses temporary fixture repositories and covers ready paths, policy blockers, report contracts, and secret detection. Shipwright never executes a target repository during inspection.

## Release provenance

Version tags trigger a release workflow that builds the Python artifacts and creates OIDC-backed provenance attestations. Consumers can verify a downloaded artifact with `gh attestation verify`; see [docs/release.md](docs/release.md). This links an artifact to its source and build, but does not replace vulnerability review.

## Security workflow

The repository has a separate scheduled and pull-request security workflow. `pip-audit` checks the installed Python dependency graph, while `zizmor` audits GitHub Actions workflow patterns. These tools are deliberately composed rather than reimplemented inside Shipwright.

## Security model

Shipwright treats the inspected repository as untrusted input. It reads bounded text files, skips large/binary artifacts, does not evaluate configuration, does not invoke project commands, and emits paths as evidence. The secret detector is conservative and is not a replacement for dedicated secret scanners. See [SECURITY.md](SECURITY.md) for responsible disclosure.

## Project map

- `shipwright_core/models.py` — immutable evidence and report domain models.
- `shipwright_core/detectors.py` — deterministic repository checks.
- `shipwright_core/engine.py` — orchestration and policy enforcement.
- `shipwright_core/renderers.py` — JSON, Markdown, and SARIF adapters.
- `shipwright_core/cli.py` — stable command-line interface.
- `docs/architecture.md` — design boundaries and extension points.
- `docs/improvement-audit.md` — competitive rationale and hardening decisions.
- `.github/workflows/ci.yml` — lint, type check, tests, and build.
- `.github/workflows/security.yml` — dependency and workflow security checks.
- `.github/workflows/release.yml` — package build and signed artifact provenance.
- `docs/release.md` — release, attestation, and PyPI publishing guidance.

## Roadmap

The next releases can add opt-in detectors for dependency manifests, reproducible build commands, changelog content structure (keep-a-changelog sections), SPDX validation, and GitHub App/PR annotations. Provider adapters should remain optional so the core CLI stays local, deterministic, and useful offline.

## Contributing

Small, evidence-backed changes are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), add a fixture-based regression test for new detectors, and explain any new dependency or permission in the pull request.

## License

Shipwright is released under the [MIT License](LICENSE).
