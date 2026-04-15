---
name: step4-audit
description: "Step 4: Fresh-context security and logic review with fix loop protocol"
---
# Workflow: Audit (The Jury)

**Goal:** A fresh context window in read-only mode to ruthlessly evaluate the build for Logic Drift and security.

## Composition
This workflow composes:
- **Roles:** `Security Engineer`, `SDET`
- **Phases:** `Audit`

## Process

1. **Security & Logic Review (Security Engineer + SDET):**
   - Enter **Read-only mode**. You cannot write or modify application code.
   - **Scope your review with `git diff`:** Run `git diff --stat origin/main` for an overview, then `git diff origin/main` to review exactly what changed. Evaluate the diff — not the entire codebase.
   - Run SAST linters and security checks.
   - Test edge cases.
   - Look for "Logic Drift" in the diff (shortcuts the Builder took to pass the tests — hardcoded values, static responses, minimal implementations).

2. **Routing Loop:**
   - If you find issues, write them to `.agent/AUDIT_FINDINGS.md` and exit. The human will then open a new `/step3-build` chat to fix them.
   - If the codebase is clear, ensure `.agent/AUDIT_FINDINGS.md` reflects this so we can proceed to Step 5.

## Accuracy Check
This phase prevents bad code from slipping through. No code modifications are allowed here, only reporting.

## ROUTING PROTOCOL (Yield & Prompt)
At the end of your execution, or if you hit a blocker you cannot resolve, you must output a `### SYSTEM ROUTING` block. Explicitly tell the human orchestrator exactly what slash command to run next in a New Chat, or what human action is required.

**Example:**
```markdown
### SYSTEM ROUTING
[🛑] BLOCKED: I am building the frontend, but the backend `Interaction` schema is missing from ARCHITECTURE.md. I am yielding.
🟠 NEXT ACTION: Open a New Chat, run `/step1-spec`, and instruct the Architect to define the Interaction schema.
```

---

## Fix Loop Protocol

When audit finds issues, this protocol defines the structured loop between Audit and Build:

1. **Auditor** writes all findings to `.agent/AUDIT_FINDINGS.md` with:
   - Severity: `[BLOCKS_RELEASE]` / `[DEGRADED]` / `[COSMETIC]`
   - Exact reproduction steps or output evidence
   - Expected vs. actual behavior
   - File paths and line numbers

2. **Human** opens New Chat → runs `/step3-build` with instruction:
   "You are in Fix-only mode. Read `.agent/AUDIT_FINDINGS.md`.
   Resolve all documented issues. Do not add new features."

3. **Builder** patches each finding, runs tests, then clears
   `.agent/AUDIT_FINDINGS.md` → writes "ALL ISSUES RESOLVED"

4. **Human** opens New Chat → runs `/step4-audit` for re-verification

5. Loop repeats until audit passes (`.agent/AUDIT_FINDINGS.md` = "PASS")