---
name: library-sdk
description: Library/SDK topology guardrails — API surface stability, backward compatibility, documentation
---
# Topology: Library / SDK

**Core Focus:** API Surface Stability and Consumer Safety.

**When this topology applies:** Go modules, npm packages, Python libraries, or any project that is consumed as a dependency by other projects rather than deployed as a standalone application.

_This profile is a behavioral modifier. It does not replace any role or workflow — it adds domain-specific constraints on top of whatever workflow the agent is currently executing. Read this profile when the project's `ARCHITECTURE.md` declares `library-sdk` in its Topology field._

_**Note on Backend Route Coverage Matrix:** When both `library-sdk` and `backend` topologies are active, the Backend Route Coverage Matrix in TESTING.md should be adapted for exported functions rather than HTTP endpoints. Use columns: `Endpoint / Function | Method | Valid Input | Invalid Input | Error Handling | Edge Cases` instead of the HTTP-oriented columns._

---

## Guardrail 1: Public API Surface Documentation

The `ARCHITECTURE.md` "API Contracts" section must document every exported type, function, and interface that consumers depend on. This is the library's external contract.

### Rules for the Architect (Spec Phase)

- Document every public function signature, its parameters, return types, and behavior.
- Changes to the public API surface require explicit Architect approval. The Builder cannot unilaterally add, remove, or modify exported symbols.

### Rules for the Auditor (Audit Phase)

- Verify that every exported symbol in the source code is documented in `ARCHITECTURE.md`.
- Flag any undocumented public function, type, or interface.

---

## Guardrail 2: Backward Compatibility

Breaking changes to the public API are the most dangerous thing a library can ship. A single breaking change can cascade failures across every consumer.

### Rules for the SDET (Trap Phase)

Write tests that verify:

- Existing public function signatures haven't changed.
- Return types haven't changed shape.
- Default behavior is preserved when new optional parameters are added.
- Deprecated functions still work (with warnings) until the next major version.

### Rules for the Auditor (Audit Phase)

- Compare the current public API surface against the documented surface in `ARCHITECTURE.md`.
- If a function signature changed, verify that the semver version bump matches the change:
  - Patch: bug fixes, no API changes.
  - Minor: new features, backward compatible.
  - Major: breaking changes (requires explicit justification).

---

## Guardrail 3: Zero-Dependency Discipline

LLM agents tend to `npm install` or `go get` aggressively — every new dependency a library adds becomes a transitive dependency for all consumers. This guardrail forces a deliberate pause.

### Rules for the Builder (Build Phase)

- Adding a new external dependency requires explicit justification in the commit message AND Architect approval (yield and prompt).
- Before adding a dependency, check: can this be implemented with the standard library? If yes, do that instead.
- If a dependency is required, prefer well-maintained, minimal libraries over feature-rich frameworks.

### Rules for the Auditor (Audit Phase)

- Check `go.mod` / `package.json` / `pyproject.toml` for any new dependencies added during the current feature.
- For each new dependency: verify it has a compatible license, is actively maintained, and doesn't pull in a large transitive dependency tree.

---

## Guardrail 4: Example Tests

Every public function should have at least one example test. These serve as both documentation and regression tests — they show consumers how to use the function AND verify it still works.

### Format by Language

- **Go:** `Example*` functions in `*_test.go` files (rendered by `go doc`).
- **Python:** Doctests in docstrings or dedicated `examples/` directory.
- **Node.js / TypeScript:** Code blocks in README.md that are validated by a test runner, or dedicated `examples/` directory with runnable scripts.

### Rules for the SDET (Trap Phase)

- For every new public function added during a feature, write at least one example test.
- Example tests must be self-contained — a consumer should be able to copy-paste the example and have it work.

### Rules for the Auditor (Audit Phase)

- Flag any public function that lacks an example test.
- Verify that existing example tests still compile/run after API changes.

---

## Guardrail 5: Release Checklist

Before shipping any version of a library/SDK, verify:

- [ ] All public functions have example tests.
- [ ] `CHANGELOG.md` documents all changes since the last release.
- [ ] Version number follows semver and matches the scope of changes.
- [ ] No new dependencies added without Architect approval.
- [ ] All deprecated functions include deprecation notices with migration guidance.
- [ ] CI passes with the minimum supported language/runtime version (not just latest).

**Applies to:** Release Gatekeeper (Ship phase).
