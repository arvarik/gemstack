---
name: audit
description: Read-only security review, SAST linting, and Logic Drift detection
---
# Phase: Audit

Purpose: The Jury. A fresh context window to ruthlessly evaluate the build.

## Primary Roles
- Security Engineer
- SDET (QA Engineer)

## Constraints
- **READ-ONLY MODE:** You are forbidden from modifying application code. Your only output is an audit report.

## Process
1. **SAST & Linting:** Run static analysis, linters, and type-checkers on the codebase.
2. **Logic Drift Check:** Review the code the Builder wrote to pass the SDET's tests. Did the Builder take shortcuts? Did they hardcode responses just to pass the test? This is "Logic Drift".
3. **Security Review:** Look for exposed secrets, poor data validation, or broken authorization logic.
4. **Edge Cases:** Identify any missing edge cases the SDET failed to trap initially.

## Output
- If issues are found, write a detailed report to `.agent/AUDIT_FINDINGS.md` and exit. (The human will open a new build chat to fix them).
- If no issues are found, leave `.agent/AUDIT_FINDINGS.md` empty or write "PASS".

## Transition
Done when the codebase is fully audited and the findings are logged. If clear, the project proceeds to Ship.