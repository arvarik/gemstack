---
name: test
description: Adopt the test phase
---
# Phase: Test

Purpose: Find out what's broken before the user does.

## Primary Roles
- QA Engineer (functional testing, finding bugs)
- ML Engineer (model quality testing, performance benchmarks)

## Inputs
- .agent-context/TESTING.md for scenarios and project-specific test methods
- The code built in the build phase
- Design docs for expected behavior reference

## Process

### Step 0: State Unification (if parallel worktrees were used)
Before testing, check if any temporary test files exist from
parallel build agents:
1. Check: `ls .agent-context/TESTING-*.md 2>/dev/null`
2. If found, read each temporary file and merge its scenarios
   into the appropriate section of .agent-context/TESTING.md
   (don't just concatenate - organize by feature section)
3. Delete the temporary files: `rm .agent-context/TESTING-*.md`
4. Commit the unified TESTING.md before proceeding

### Functional Testing (QA Engineer):
1. Read TESTING.md for the test method this project uses
2. Run happy path for each scenario first
3. Then attack systematically:
   - Edge cases: empty inputs, max values, special characters
   - State transitions: back button, refresh mid-flow, stale data
   - Multi-step flows: what if step 2 fails after step 1 succeeded?
   - Responsiveness: 375px, 768px, 1440px (frontend only)
   - Performance: does anything feel slow?
4. Document every result in TESTING.md WITH EVIDENCE

### Model/Pipeline Testing (ML Engineer):
1. Run against clean test fixtures - establish baseline
2. Run against messy/edge-case inputs (corrupt files, wrong
   encoding, truncated data, very long inputs)
3. Measure: latency, memory, output quality
4. Compare against performance targets from design doc

## Evidence Requirement
Every result must include execution evidence in the Notes column:
- Backend tests: the actual command run and its stdout/stderr
  Example: `curl -X POST .../interactions -d '{"type":"coffee"}' -> 201 {"data":{"id":"abc"}}`
- Frontend (automated): Playwright/Jest command and output
  Example: `npx playwright test reconnect.spec.ts -> 8 passed, 1 failed`
- Frontend (visual): mark as NEEDS_HUMAN_REVIEW with specific
  instructions: "At 1440px on /dashboard, check that reconnect
  cards are evenly spaced and don't exceed ~320px width"
- "PASS" with no evidence is treated as UNTESTED

## Output
Update TESTING.md:

| Scenario | Status | Notes (evidence required) |
|----------|--------|--------------------------|
| [description] | PASS / FAIL / BLOCKED / NEEDS_HUMAN_REVIEW | [terminal output or review instructions] |

### Bugs Found
For each bug:
- Severity: blocks release / degraded experience / cosmetic
- Reproduction steps (exact)
- Expected vs actual behavior

## Files Updated
| File | Change |
|------|--------|
| .agent-context/TESTING.md | Scenarios updated with results + evidence |
| .agent-context/STATUS.md | Updated to reflect test results / bug-fix mode |

## Transition
If bugs with severity "blocks release" exist, they go to the
fix phase. Do NOT proceed to review or the next feature.
Update STATUS.md to "bug-fix mode."

If all scenarios pass with evidence, move to review phase.

## Critical Rule
Blocking bugs are BLOCKING. Do not move to the next feature
while "blocks release" bugs exist.