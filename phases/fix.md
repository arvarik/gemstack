---
name: fix
description: Targeted bug fixes from audit findings — fix-only mode, no new features
---
# Phase: Fix

Purpose: Repair specific bugs found during testing or review.
This is NOT the build phase. The scope is surgically narrow.

## Primary Roles
- Principal Backend Engineer
- Principal Frontend Engineer
- ML Engineer

## When To Use
- QA found bugs in the test phase (listed in TESTING.md)
- Review phase found blocking issues (listed in STATUS.md)
- NEVER for new features, refactoring, or "while I'm here" improvements

## Inputs
- .agent/TESTING.md for bug descriptions, repro steps, severity
- .agent/STATUS.md for review action items (if from review phase)

## Process
1. Read the specific bug from TESTING.md or STATUS.md
2. Read ONLY the file(s) involved in the bug
3. Identify the root cause
4. Fix the exact issue. Change the minimum lines necessary.
5. Verify the fix addresses the repro steps

## Rules
- You are in FIX mode. Your scope is the bug and nothing else.
- Do NOT refactor surrounding code
- Do NOT change the architecture
- Do NOT "improve" nearby code you happen to notice
- Do NOT add features, even small ones
- If the fix requires an architectural change, STOP and escalate
  to the architect role. Document why in STATUS.md.

## Output
- Minimal code change fixing the specific bug
- If fixing a QA bug (from TESTING.md): update TESTING.md, change
  the bug's status to FIXED (not PASS - QA confirms PASS during re-test)
- If fixing a Review action item (from STATUS.md): update STATUS.md,
  mark the action item as FIXED

## Files Updated
| File | Change |
|------|--------|
| (only the files containing the bug) | Minimal fix |
| .agent/TESTING.md | Bug status changed to FIXED (if bug came from QA) |
| .agent/STATUS.md | Action item marked FIXED (if issue came from review) |

## Transition
After all blocking bugs are fixed, return to the test phase for
the QA engineer to re-verify. QA marks scenarios as PASS with
evidence. Only then proceed to review (or ship if already reviewed).