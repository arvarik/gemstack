---
name: audit
description: Run the audit workflow (Step 4)
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
   - Run SAST linters and security checks.
   - Test edge cases.
   - Look for "Logic Drift" (shortcuts the Builder took to pass the tests).

2. **Routing Loop:**
   - If you find issues, write them to `.agent/AUDIT_FINDINGS.md` and exit. The human will then open a new `/workflow:build` chat to fix them.
   - If the codebase is clear, ensure `.agent/AUDIT_FINDINGS.md` reflects this so we can proceed to Step 5.

## Accuracy Check
This phase prevents bad code from slipping through. No code modifications are allowed here, only reporting.

## ROUTING PROTOCOL (Yield & Prompt)
At the end of your execution, or if you hit a blocker you cannot resolve, you must output a `### SYSTEM ROUTING` block. Explicitly tell the human orchestrator exactly what slash command to run next in a New Chat, or what human action is required.

**Example:**
```markdown
### SYSTEM ROUTING
[🛑] BLOCKED: I am building the frontend, but the backend `Interaction` schema is missing from ARCHITECTURE.md. I am yielding.
🟠 NEXT ACTION: Open a New Chat, run `/workflow:spec`, and instruct the Architect to define the Interaction schema.
```