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
1. **Scope the Review:** Run `git diff --stat origin/main` to identify which files changed and how much. Then run `git diff origin/main` to isolate exactly what the Builder changed. **Evaluate the diff, not the entire codebase.** LLMs are significantly better at critiquing isolated diffs than scanning whole files.
2. **SAST & Linting:** Run static analysis, linters, and type-checkers on the codebase.
3. **Logic Drift Check:** Review the diff for shortcuts the Builder took to pass the tests. Did they hardcode responses? Return static objects without querying the database? Write minimal implementations that satisfy assertions but lack real logic? This is "Logic Drift."
4. **Security Review:** Look for exposed secrets, poor data validation, or broken authorization logic — scoped to the changed files.
5. **Edge Cases:** Identify any missing edge cases the SDET failed to trap initially.

## Output
- If issues are found, write a detailed report to `.agent/AUDIT_FINDINGS.md` and exit. (The human will open a new build chat to fix them).
- If no issues are found, leave `.agent/AUDIT_FINDINGS.md` empty or write "PASS".

## Transition
Done when the codebase is fully audited and the findings are logged. If clear, the project proceeds to Ship.