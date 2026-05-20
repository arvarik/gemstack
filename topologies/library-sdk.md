---
name: library-sdk
description: Library and SDK topology guardrails — semantic versioning, zero-dependency philosophy, and DX
---
# Topology: Library / SDK

<thinking_process>
The Library/SDK topology focuses on "Stability" and "Developer Experience (DX)." Think about:
1. Public API stability and Breaking Changes.
2. Dependency bloat.
3. Documentation quality (TypeDoc, JSDoc).
</thinking_process>

<guardrails>
## Guardrail 1: The Public Interface Mutex
- Any change to a public function signature, exported type, or class member MUST be approved by the Architect.
- Use **SemVer** strictly. If the public interface changes, increment the major version.

## Guardrail 2: Zero-Dependency Philosophy
- Avoid adding external dependencies unless absolutely necessary. Every dependency added increases the attack surface and bundle size.
- Prefer native platform APIs (Node `fs/promises`, Browser `fetch`).

## Guardrail 3: Documentation is Code
- Every public export MUST have a JSDoc block with `@example`.
- Automated docs (e.g., TypeDoc) must be generated and verified in the Audit phase.

## Guardrail 4: Compatibility Testing
- Libraries must be tested against all supported runtime versions (e.g., Node 18, 20, 22).
</guardrails>

<reporting>
### Public API Surface Log (in ARCHITECTURE.md)
The Architect must maintain this log:

| Version | Date | Export | Type | Change Description |
|---------|------|--------|------|--------------------|
| ...     | ...  | ...    | ...  | ...                |
</reporting>
