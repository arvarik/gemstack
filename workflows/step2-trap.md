---
name: step2-trap
description: "Step 2: Write failing automated tests to trap requirements"
---
# Workflow: Trap (The Test)

<thinking_process>
The Trap phase is about "Requirement Capture." Think about:
1. What does "Success" look like in a test suite?
2. How to ensure the test fails for the right reason before implementation.
</thinking_process>

**Goal:** Create failing automated tests that "trap" the requirement. Nothing moves to "Build" without a failing trap.

## Composition
- **Roles:** `Principal Engineer`, `SDET`
- **Phases:** `Contract & Plan`
- **Native Tools:** Uses `task.md` and `IMPLEMENTATION_PLAN.md`.

## Process

1.  **Draft Tasks**: The **SDET** translates the Spec into a checklist in `task.md`.
2.  **Failing Tests**: The **Principal Engineer** writes the actual test files (Jest, Playwright, etc.) with assertions that fail on the current codebase.

## Accuracy Checks
- [ ] Do all new tests fail with a clear "Expected X, got Y" message?
- [ ] Is there 100% contract coverage for the feature?
- [ ] Is the `task.md` marked with `[/]` for the current building block?

[STATE: READY_FOR_BUILD]