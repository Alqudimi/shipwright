# Shipwright Architecture

Shipwright is organized around one boundary: **the repository is untrusted input, and the report is a stable public contract**.

## Runtime flow

```text
Path + shipwright.toml
          |
          v
   resolve_repository
          |
          v
      run_audit
          |
    +-----+------------------+
    | deterministic detectors |
    +-----+------------------+
          |
          v
  immutable CheckResult records
          |
          v
     policy enforcement
          |
          v
 JSON / Markdown / SARIF
```

The domain model in `shipwright_core.models` contains no filesystem orchestration beyond safe path resolution and no CLI concerns. Detectors in `detectors.py` are pure repository readers that return `CheckResult`. The engine composes them and applies policy. Renderers adapt one report into output formats without changing its meaning.

## Safety boundaries

The core path never imports or executes target code, never runs shell commands, never sends network requests, and skips large or binary files during text inspection. Future detectors must preserve these defaults. Optional command execution, if ever added, must be isolated behind an explicit adapter with allow-listed commands and a separate policy gate.

## Extension points

A new detector implements `Detector = Callable[[Path], CheckResult]` and is added to the detector registry with a stable `check_id`. A new renderer consumes `AuditReport` and must preserve the same verdict, score, status, evidence, and remediation semantics. Provider integrations such as GitHub PR annotations belong outside the core package and must remain optional.

## Compatibility

The JSON report is the primary integration contract. New fields may be added; existing field meanings and check IDs should remain stable during the 0.x line. Breaking changes require a changelog entry and a versioned migration note.
