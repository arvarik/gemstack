---
name: llm-failure-modes
description: Reference catalog of known LLM agent failure modes and mitigations
---
# Known LLM Agent Failure Modes

A reference catalog of failure patterns observed when LLM agents write code. Consult this when debugging unexpected agent behavior.

_This is a reference document, not a guardrail profile. It is topology-independent — the failures documented here can occur in any project type. Specific mitigations are implemented in the topology profiles and role files._

---

## Data Integrity Failures

### The Mocking Illusion
**What:** The agent mocks database calls, HTTP clients, or external services in production code (not just test code) to make tests pass faster.
**Detection:** Search for mock/stub patterns outside of test directories. Check if route handlers return hardcoded objects without querying the database.
**Mitigation:** Integration tests must hit real databases. Use randomized test data. Emphasize negative test cases.
**Guardrail:** `topologies/backend.md` → Guardrail 1.

### Silent Data Corruption
**What:** The agent swallows database errors with empty catch blocks, causing mutations to silently fail while the endpoint returns 200 OK.
**Detection:** Search for empty `catch`/`except` blocks. Check that all database write operations have error handling that surfaces failures.
**Mitigation:** Require explicit error propagation in all data mutation paths. The Builder role forbids empty catch blocks.
**Guardrail:** `topologies/backend.md` → Guardrail 1 (Builder rules).

### Hardcoded Response Bypass
**What:** The agent writes route handlers that return static objects matching test assertions, without actually implementing the business logic.
**Detection:** Compare route handler complexity against test complexity. Simple handlers passing complex tests are suspicious.
**Mitigation:** Use randomized test data so the agent can't predict expected values. Test idempotency and negative paths which can't be faked with static responses.
**Guardrail:** `topologies/backend.md` → Guardrail 1 (Auditor rules).

### N+1 Query Snowball
**What:** The agent implements nested data fetching with a loop of individual queries (e.g., fetching posts for every user in a list). Works fine with test data but causes exponential slowdown in production.
**Detection:** Profile endpoint response times with realistic data volumes. Search for database queries inside loops.
**Mitigation:** Require explicit query strategy documentation. Use JOINs, `include`, or `joinedload()` depending on the ORM.
**Guardrail:** `topologies/backend.md` → Guardrail 3.

---

## Frontend Failures

### State Management Bloat
**What:** The agent imports multiple state management libraries (Redux, Zustand, Jotai, React Query) in the same project, creating conflicting state patterns.
**Detection:** Check `package.json` for multiple state management dependencies. Search for conflicting import patterns.
**Mitigation:** `STYLE.md` must specify the single allowed state management approach. Adding new dependencies requires Architect approval.
**Guardrail:** `topologies/frontend.md` → Guardrail 3.

### Single-State Testing
**What:** The agent only tests the "success" state of a component and ignores empty, loading, error, and partial states. The component ships with untested visual states that break in edge cases.
**Detection:** Review the Component State Matrix in TESTING.md for gaps. Check test files for rendering assertions — most will only test the happy path.
**Mitigation:** Require the 5-state matrix (Empty, Loading, Success, Error, Partial) for every interactive component.
**Guardrail:** `topologies/frontend.md` → Guardrail 1.

### CSS Hallucination
**What:** The agent writes CSS that looks syntactically correct but produces visually incorrect output (wrong colors, broken layouts, overlapping elements). CLI agents cannot see rendered output.
**Detection:** Cannot be detected by CLI agents. Mark visual tests as `NEEDS_HUMAN_REVIEW`.
**Mitigation:** Use design tokens from `STYLE.md`. Never invent ad-hoc color values. Human must verify visual output.

### Hydration Mismatch (SSR)
**What:** Server-rendered HTML doesn't match client-rendered HTML, causing React/Svelte/Vue hydration errors — flickering UI, lost interactivity, or console errors.
**Detection:** Check build output for hydration warnings. Run `next build` and scan for mismatch errors.
**Mitigation:** Never use `Date.now()`, `Math.random()`, or browser-only APIs in components that render on the server without proper `useEffect` guards.
**Guardrail:** `topologies/frontend.md` → Guardrail 2.

### Stub Amnesia
**What:** The agent creates stubs/mocks during the Build phase and forgets to remove them before shipping, so mock data goes to production.
**Detection:** `grep -r "// STUB:" src/` or `grep -r "REMOVE_STUB" src/` returns results after the Build phase.
**Mitigation:** Stub Audit Tracker in STATUS.md. All stubs must show REMOVED status before shipping.
**Guardrail:** `topologies/frontend.md` → Guardrail 4.

---

## ML/AI Failures

### Context Window Blowout
**What:** The agent runs `print(df)` or logs raw model responses, flooding the context window with data and causing the agent to lose track of earlier instructions.
**Detection:** The agent's output quality suddenly degrades mid-session. Earlier task context is lost. Responses become generic or repetitive.
**Mitigation:** Use `.info()`, `.describe()`, `.head()`. Write large outputs to files. Truncate model responses before logging.
**Guardrail:** `topologies/ml-ai.md` → Guardrail 4.

### Eval Overfitting
**What:** The agent tunes prompts to maximize scores on the eval dataset but the improvements don't generalize to real-world inputs.
**Detection:** Holdout set scores diverge from eval set scores. (Requires human-run holdout evaluation.)
**Mitigation:** Maintain a holdout set that the agent never sees. Run holdout evaluation as a human-in-the-loop step during the Release Gatekeeper workflow.
**Guardrail:** `topologies/ml-ai.md` → Guardrail 5.

### Cost Exhaustion Loop
**What:** The agent enters an infinite optimization loop, calling LLM APIs repeatedly trying to improve a metric by fractions of a percent.
**Detection:** API cost tracking shows rapid spending. Improvement rate drops below meaningful thresholds. Session exceeds 30 minutes in a tuning loop.
**Mitigation:** Multi-variable circuit breaker: attempt count (5), cost cap (from Model Ledger), improvement rate (<2% for 3 attempts), wall-clock time (30 min).
**Guardrail:** `topologies/ml-ai.md` → Guardrail 2.

### Prompt Drift
**What:** The agent makes small, untracked changes to prompts across multiple files, making it impossible to correlate prompt changes with quality changes.
**Detection:** `git diff` shows prompt string changes scattered across multiple source files rather than in a centralized `/prompts` directory.
**Mitigation:** Externalize prompts to `/prompts` directory. Log all changes in the Prompt Versioning Changelog. Inline prompt strings are forbidden.
**Guardrail:** `topologies/ml-ai.md` → Guardrail 3.

### Schema Compliance Assumption
**What:** The agent assumes LLM output will always conform to the requested JSON schema, and writes code with no fallback for malformed responses. Works in testing (where outputs are usually well-formed) but crashes in production (where edge cases trigger unstructured output).
**Detection:** Search for JSON.parse calls without try/catch. Check if schema validation exists before downstream processing.
**Mitigation:** Always wrap LLM response parsing in validation + error handling. Use structured output modes when available (e.g., Gemini's `responseMimeType: "application/json"`). Layer 2 tests verify schema compliance.
**Guardrail:** `topologies/ml-ai.md` → Guardrail 1 (Layer 1 tests).

---

## Process Failures

### The Hanging Terminal
**What:** The agent runs `npm run dev`, `python main.py`, or `go run ./cmd/server` in the foreground, permanently blocking its terminal session. All subsequent commands queue behind the blocked process.
**Detection:** The agent stops producing output. Commands time out. No progress on any task.
**Mitigation:** Always background long-running processes: `npm run dev > /dev/null 2>&1 &`. Already mandated in all engineering roles and the ML Engineer's Terminal Execution section.

### Ghost Contracts
**What:** In full-stack projects, the backend agent changes the API response shape without updating the frontend or the contract in ARCHITECTURE.md, causing silent integration failures.
**Detection:** Frontend integration tests fail after backend changes. TypeScript type errors at API boundaries. Response shapes in ARCHITECTURE.md don't match actual API output.
**Mitigation:** Contract changes require Architect approval. The Integrate phase catches these at the boundary. Both backend and frontend must build against the contract in ARCHITECTURE.md.

### Dependency Cascade
**What:** The agent installs a dependency to solve a simple problem, bringing in a large transitive dependency tree. Particularly dangerous in library/SDK projects where the dependency becomes a transitive dependency for all consumers.
**Detection:** Check `package.json` / `go.mod` / `pyproject.toml` for new entries after build. Run `npm ls --all` or `go mod graph` to see transitive impact.
**Mitigation:** Adding dependencies requires Architect approval. Prefer standard library solutions. For libraries, this is a hard constraint.
**Guardrail:** `topologies/library-sdk.md` → Guardrail 3.

### Configuration Destruction
**What:** The agent runs destructive infrastructure commands (`terraform apply`, `docker compose down -v`, `kubectl delete`) without human approval, destroying configuration or data.
**Detection:** Post-mortem analysis of terminal history shows the agent executed destructive commands autonomously.
**Mitigation:** Unconditional prohibition on destructive infrastructure commands. Agent prepares the plan; human applies it.
**Guardrail:** `topologies/infrastructure.md` → Guardrail 2.

### Scope Creep via Refactoring
**What:** The agent, when asked to fix a small bug, rewrites surrounding code "for better readability" or "modernization" — introducing regressions in areas unrelated to the bug fix.
**Detection:** `git diff --stat` shows far more files changed than the bug scope warrants. Lines changed exceed 10× the expected fix size.
**Mitigation:** The Fix phase workflow constrains the agent to only modifying code related to the specific bug. Agents must not refactor adjacent code without explicit Architect approval.
