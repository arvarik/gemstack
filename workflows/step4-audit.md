---
name: step4-audit
description: "Step 4: Security, performance, and accessibility review"
---
# Workflow: Audit (The Review)

<thinking_process>
The Audit phase is about "Quality Assurance." Think about:
1. Security vulnerabilities (OWASP).
2. Performance bottlenecks (N+1).
3. Accessibility (A11y) and User Experience.
</thinking_process>

**Goal:** Conduct a fresh-eyes review of the implementation.

## Composition
- **Roles:** `SDET`, `Security Engineer`
- **Phases:** `Audit`
- **Native Tools:** Uses `walkthrough.md` artifact.

## Process

1.  **Security Sweep**: The **Security Engineer** audits the data flow and auth.
2.  **QA Pass**: The **SDET** performs edge-case testing and UX verification.
3.  **Documentation**: Summarize findings in the `walkthrough.md`.

## Accuracy Checks
- [ ] Are there any high-priority security issues?
- [ ] Does the UI meet the design spec from Step 1?
- [ ] Is the `walkthrough.md` ready for final user sign-off?

[STATE: READY_FOR_SHIP]