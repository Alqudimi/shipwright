# Release and provenance

Shipwright releases are created from semantic-version tags such as `v0.3.0`. The release workflow builds the sdist and wheel in GitHub Actions, uploads the artifacts, attaches them to the matching GitHub Release, and creates signed artifact attestations through GitHub's OIDC-backed attestation service.

The workflow grants only `contents: write`, `id-token: write`, and `attestations: write`; `contents: write` is required solely to attach the built files to the matching GitHub Release. It does not use a long-lived PyPI token. If PyPI publishing is enabled later, configure PyPI Trusted Publishing for the exact repository, workflow, and environment rather than adding an API key to GitHub Secrets.

After downloading an artifact, consumers can verify provenance with GitHub CLI:

```bash
gh attestation verify shipwright_readiness-0.3.0-py3-none-any.whl \
  -R Alqudimi/shipwright
```

An attestation links the artifact to the repository, commit, workflow, triggering event, and OIDC identity. It does not prove that the source or dependency graph is free of vulnerabilities; consumers must still evaluate the project and their own policy.

The workflow intentionally attests release artifacts, not every test build or source file. This keeps provenance meaningful and limits signing noise. The same artifacts are attached to the GitHub Release so consumers can download the exact files that were attested.

## References

- [GitHub Artifact Attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
- [actions/attest](https://github.com/actions/attest)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [SLSA Provenance](https://slsa.dev/spec/v1.0/provenance)


## Implementation note

The release workflow uses `actions/attest-build-provenance` rather than calling the lower-level `actions/attest` action directly. The wrapper supplies the default SLSA build provenance predicate for release artifacts; direct `actions/attest` use requires an explicit custom predicate or predicate file.

Reference: [actions/attest-build-provenance action.yml](https://github.com/actions/attest-build-provenance/blob/main/action.yml).


## Version integrity

The tag-triggered workflow derives the expected package version from `github.ref_name` and checks the built wheel and source distribution names before attestation or GitHub Release upload. This prevents a release tag from advertising one version while distributing metadata for another version.


## Reproducible build gate

Release builds set `SOURCE_DATE_EPOCH=0`, build the wheel and source distribution twice, and compare sorted SHA-256 manifests. Attestation and release upload run only after both builds are byte-for-byte identical. This does not prove every dependency or environment is reproducible, but it proves the controlled package build in the release runner is deterministic for that commit.

Reference: [SOURCE_DATE_EPOCH specification](https://reproducible-builds.org/specs/source-date-epoch/).

## Consumer verification gate

After attestation and release upload, the workflow runs `gh attestation verify` for every artifact. Verification enforces the repository and the exact `.github/workflows/release.yml` signer, in addition to the default SLSA provenance predicate. This makes the release pipeline test the consumer verification path rather than only checking that an attestation was created.
