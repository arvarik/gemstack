# Testing Strategy & Results

_This file tracks test methods, scenarios, and results with concrete execution evidence. Bugs found here block the release of a feature. Agents must update this during the Test and Fix phases._

## 0. Local Development Setup
_Exact steps to get the application running locally so agents can execute tests. Copy-paste ready._

### Prerequisites
- e.g., Node.js 22+, npm — or Python 3.11+, ffmpeg — or Go 1.25+, Docker, golangci-lint
- e.g., Copy `.env.example` to `.env` and configure required keys

### Start the App
- e.g., `npm run dev` — starts frontend on :5173 and backend on :3001
- e.g., `python -m src.aisrt run /path/to/media --dry-run`
- e.g., `make build && ./bin/app serve` — or `docker compose up -d`
- e.g., `./media-scrubber.sh -d /path/to/media` (dry-run by default)

### Seed / Reset Data
- e.g., `npm run seed` — drops and repopulates with synthetic demo data
- e.g., N/A — uses filesystem as input source
- e.g., `make docker-up` — starts PostgreSQL with TimescaleDB extension

### Database
- e.g., SQLite file auto-created on first run at `./app.db`
- e.g., Run `docker compose up db` for PostgreSQL + TimescaleDB
- e.g., N/A — no database (stateless utility)

### Code Generation (if applicable)
- e.g., `sqlc generate` — regenerates type-safe Go DB code from `queries/query.sql`
- e.g., `swag init -g cmd/server/main.go` — regenerates Swagger docs
- e.g., N/A

---

## 1. Test Methods & Tools
_How do we test this project locally? Give the exact CLI commands and tools._

### Unit / Integration Tests
- **Run all tests**: `npm test` (watch) / `npx vitest run` (single pass) / `pytest tests/` / `go test ./...`
- **Run specific suite**: `npx vitest run tests/unit/search.test.ts` / `pytest tests/test_extractor.py` / `go test ./internal/service/...`
- **Run with race detector** (Go): `go test -race -count=1 ./...`
- **Coverage**: `npx vitest run --coverage` / `pytest --cov=src/` / `go test -cover ./...`
- **Testcontainers** (Go): If using testcontainers-go, Docker must be running. Tests will spin up ephemeral PostgreSQL instances.

### Type Checking & Linting
- **TypeScript**: `npx tsc --noEmit` — must produce 0 errors
- **ESLint**: `npx eslint .` — must produce 0 warnings
- **Python**: `mypy src/ tests/ --strict` + `ruff check .` + `ruff format --check .`
- **Go**: `golangci-lint run ./...` — must produce 0 warnings. Also run `go vet ./...`
- **Bash**: `shellcheck media-scrubber.sh` (if ShellCheck is installed)

### Backend / API Testing
- Execute actual `curl` or `httpie` commands against the running server.
- Validate response shapes match API contracts in ARCHITECTURE.md.
- For Go APIs with Swagger: validate against `docs/swagger.json`.

### Frontend / UI Testing
- Write and execute Playwright/Puppeteer scripts for interaction flows, or run component tests via `npm run test:ui`.
- Test at responsive breakpoints: 375px (mobile), 768px (tablet), 1440px (desktop).

### Manual / Visual
- Mark scenarios as `NEEDS_HUMAN_REVIEW` if they require visual confirmation (e.g., colors, spacing, animations, drag-and-drop).

## 2. Execution Evidence Rules
_Never mark a test as PASS without evidence._
- For backend tests, paste the exact `curl` command and its stdout/stderr JSON response in the Notes column.
- For Go tests, paste the output of `go test -v ./...` (showing individual test PASS/FAIL lines).
- For frontend automated tests, paste the output of the test runner (e.g., Playwright/Jest output).
- For type checking / linting, paste the command and its output (e.g., `npx tsc --noEmit → 0 errors`, `golangci-lint run → no issues`).
- "PASS" with no evidence is treated as UNTESTED.

---

## Current Feature Scenarios: {Feature Name}

| Scenario | Status | Notes (Evidence) |
|----------|--------|------------------|
| Empty/null/missing inputs | UNTESTED | |
| Valid payload creates resource | UNTESTED | |
| Invalid payload returns structured error | UNTESTED | |
| State transitions (back button) | UNTESTED | |
| Rapid repeated actions (spam click) | UNTESTED | |
| Responsive check (375px mobile) | NEEDS_HUMAN_REVIEW | Check that cards stack vertically. |
| Responsive check (1440px desktop) | NEEDS_HUMAN_REVIEW | Check max-width constraints. |

---

## Backend Route Coverage Matrix (Backend Topology Only)

_Populated by the SDET during the Trap phase. One row per API endpoint. All cells must show PASS with execution evidence or FAIL with reproduction steps._

| Endpoint | Method | 200 OK | 400 Bad Req | 401/403 Auth | 404 Not Found | Idempotent | Edge Cases |
|----------|--------|--------|-------------|--------------|---------------|------------|------------|
| _(populated per feature)_ | | | | | | | |

_If not a backend project, write "N/A — No backend API endpoints."_

---

## Frontend Component State Matrix (Frontend Topology Only)

_Populated by the SDET during the Trap phase. Every interactive component must be tested across all visual states._

| Component | Empty | Loading | Success | Error | Partial |
|-----------|-------|---------|---------|-------|---------|
| _(populated per feature)_ | | | | | |

_If not a frontend project, write "N/A — No frontend UI components."_

---

## ML / AI Evaluation Thresholds (ML/AI Topology Only)

_Populated by the ML Engineer during the Build phase. Track eval scores over time to detect regression._

| Metric | Target | Current | Method | Eval Set | Prompt Ver. | Last Run |
|--------|--------|---------|--------|----------|-------------|----------|
| _(populated per feature)_ | | | | | | |

### Eval / Holdout Boundary
- **eval_set**: `eval/` directory — Agent may read and optimize against these.
- **holdout_set**: `eval/holdout/` directory — HUMAN-ONLY. Agent must never reference these files.

_If not an ML/AI project, write "N/A — No ML evaluation metrics."_

---

## Bugs Found (Fix Phase Queue)
_List specific bugs discovered during testing. Agents in the 'Fix' phase will read this section._

1. **[Blocks release]** Form double-submit creates duplicate entries.
   - **Repro**: Fill form, click Save twice rapidly.
   - **Expected**: Button disables on first click.
   - **Actual**: Two requests go through.
   - **Severity**: blocks release / degraded experience / cosmetic
   - **Status**: OPEN (QA marks PASS during re-test)

---

## Regression Scenarios (Persistent)
_These scenarios survive the Ship phase cleanup. They are re-run on every release to catch regressions. Add critical paths and previously-shipped bug fixes here._

| Scenario | Last Verified | Notes |
|----------|---------------|-------|
| _Example: Contact search returns results for partial name match_ | _YYYY-MM-DD_ | _Core search path — always verify_ |
| _Example: Graceful shutdown flushes in-progress work_ | _YYYY-MM-DD_ | _Previously broken — fixed in v1.2_ |
| _Example: Race detector passes on all packages_ | _YYYY-MM-DD_ | _Go: `go test -race ./...`_ |
