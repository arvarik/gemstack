# Testing Strategy & Results

_This file tracks test methods, scenarios, and results with concrete execution evidence. Bugs found here block the release of a feature. Agents must update this during the Test and Fix phases._

## 1. Test Methods & Tools
_How do we test this project locally? Give the exact CLI commands and tools._
- **Backend**: Execute actual `curl` or `httpie` commands against the running server. Run unit/integration tests (e.g., `npm run test:backend`).
- **Frontend**: Write and execute Playwright/Puppeteer scripts for interaction flows, or run Component tests via `npm run test:ui`.
- **Manual/Visual**: Mark scenarios as `NEEDS_HUMAN_REVIEW` if they require visual confirmation (e.g., colors, spacing, animations).

## 2. Execution Evidence Rules
_Never mark a test as PASS without evidence._
- For backend tests, paste the exact `curl` command and its stdout/stderr JSON response in the Notes column.
- For frontend automated tests, paste the output of the test runner (e.g., Playwright/Jest output).
- "PASS" with no evidence is treated as UNTESTED.

---

## Current Feature Scenarios: {Feature Name}

| Scenario | Status | Notes (Evidence) |
|----------|--------|------------------|
| Empty/null/missing inputs | UNTESTED | |
| Valid payload creates resource | UNTESTED | |
| State transitions (back button) | UNTESTED | |
| Rapid repeated actions (spam click) | UNTESTED | |
| Responsive check (375px mobile) | NEEDS_HUMAN_REVIEW | Check that cards stack vertically. |

## Bugs Found (Fix Phase Queue)
_List specific bugs discovered during testing. Agents in the 'Fix' phase will read this section._

1. **[Blocks release]** Form double-submit creates duplicate entries.
   - **Repro**: Fill form, click Save twice rapidly.
   - **Expected**: Button disables on first click.
   - **Actual**: Two requests go through.
   - **Severity**: blocks release / degraded experience / cosmetic
   - **Status**: OPEN (QA marks PASS during re-test)
