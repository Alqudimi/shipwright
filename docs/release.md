# Release and provenance

Shipwright releases are created from semantic-version tags such as `v0.3.0`. The release workflow builds the sdist and wheel in GitHub Actions, uploads the artifacts, and creates signed artifact attestations through GitHub's OIDC-backed attestation service.

The workflow grants only `contents: read`, `id-token: write`, and `attestations: write`. It does not use a long-lived PyPI token. If PyPI publishing is enabled later, configure PyPI Trusted Publishing for the exact repository, workflow, and environment rather than adding an API key to GitHub Secrets.

After downloading an artifact, consumers can verify provenance with GitHub CLI:

```bash
gh attestation verify shipwright_readiness-0.3.0-py3-none-any.whl \
  -R Alqudimi/shipwright
```

An attestation links the artifact to the repository, commit, workflow, triggering event, and OIDC identity. It does not prove that the source or dependency graph is free of vulnerabilities; consumers must still evaluate the project and their own policy.

The workflow intentionally attests release artifacts, not every test build or source file. This keeps provenance meaningful and limits signing noise.

## References

- [GitHub Artifact Attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
- [actions/attest](https://github.com/actions/attest)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [SLSA Provenance](https://slsa.dev/spec/v1.0/provenance)


## Implementation note

The release workflow uses `actions/attest-build-provenance` rather than calling the lower-level `actions/attest` action directly. The wrapper supplies the default SLSA build provenance predicate for release artifacts; direct `actions/attest` use requires an explicit custom predicate or predicate file.

Reference: [actions/attest-build-provenance action.yml](https://github.com/actions/attest-build-provenance/blob/main/action.yml).
