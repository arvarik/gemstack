# Example: Full-Stack Project — `[frontend, backend]`

A walkthrough of the Gemstack 5-step workflow for a **full-stack** project with a separate frontend and backend — e.g., a Next.js + Go dashboard, a React + Express app, or any project where the client and server are distinct layers.

**Topology:** `[frontend, backend]`
**Active Guardrails:** `frontend.md` + `backend.md` — component state coverage, data integrity, anti-mocking, N+1 query awareness
**Example Project:** A Go backend + Next.js frontend for viewing WHOOP health/fitness data

---

## The Feature

> "Add a sleep trends dashboard that shows the user's sleep score over the last 30/60/90 days as a line chart, with the ability to drill into any single night's detailed breakdown."

---

## Step 1: `/step1-spec` (The Contract)

**Roles:** Product Visionary + UI/UX Designer + Architect
**Phases:** Ideate, Design

### What happens

The **Product Visionary** defines the opportunity:
- **Pain:** Users see individual night scores but can't spot trends or regressions over time.
- **Vision:** A chart that reveals patterns — "oh, my sleep drops every Sunday" — with one-click drill-down.

The **UI/UX Designer** specifies:
- Date range selector: 30/60/90-day toggle (tab-style, not dropdown)
- Line chart showing sleep score over time, with a highlighted average line
- Click any data point to expand a detail card (sleep stages, HRV, respiratory rate)
- All 5 states: empty (no data), loading (skeleton chart), success, error (API failed), partial (some days missing)

The **Architect** locks in the API contracts:

```typescript
// Added to ARCHITECTURE.md

GET /api/sleep/trends?range=30|60|90
Response: {
  data: Array<{ date: string; sleepScore: number; stages: SleepStages }>;
  average: number;
  range: "30" | "60" | "90";
}

GET /api/sleep/:date
Response: {
  date: string;
  sleepScore: number;
  stages: { awake: number; light: number; deep: number; rem: number };
  hrv: number;
  respiratoryRate: number;
}
```

### Topology influence
- **Backend topology:** The Architect defines exact request/response shapes, error responses, and HTTP status codes for each endpoint.
- **Frontend topology:** The UI/UX Designer must design all 5 component states for the chart and detail card.

### Key output
The API contracts in `ARCHITECTURE.md` are the **handshake** that enables the backend and frontend to be built independently (even in parallel via git worktrees).

---

## Step 2: `/step2-trap` (Setting the Trap)

**Roles:** Principal Engineer + SDET
**Phases:** Contract & Plan

### What happens

The **Principal Backend Engineer** writes the backend task plan:
```
1. Add sleep trends query to the data layer (moderate)
2. Create GET /api/sleep/trends handler with range validation (moderate)
3. Create GET /api/sleep/:date handler (trivial)
4. Add caching for trend aggregation (moderate)
```

The **Principal Frontend Engineer** writes the frontend task plan:
```
1. Create SleepTrendsChart component with recharts (complex)
2. Create DateRangeSelector component (trivial)
3. Create SleepDetailCard drill-down component (moderate)
4. Create /dashboard/sleep page composing all components (moderate)
5. Wire React Query hooks for both endpoints (moderate)
```

The **SDET** writes **two test suites** — backend and frontend:

```go
// Backend: sleep_trends_test.go
func TestSleepTrends_ValidRange(t *testing.T) {
    resp := httptest.NewRequest("GET", "/api/sleep/trends?range=30", nil)
    assert.Equal(t, 200, resp.StatusCode)
    var body TrendsResponse
    json.NewDecoder(resp.Body).Decode(&body)
    assert.Equal(t, "30", body.Range)
    assert.NotEmpty(t, body.Data)
}

func TestSleepTrends_InvalidRange(t *testing.T) {
    resp := httptest.NewRequest("GET", "/api/sleep/trends?range=999", nil)
    assert.Equal(t, 400, resp.StatusCode)
}

func TestSleepTrends_MissingRange(t *testing.T) {
    resp := httptest.NewRequest("GET", "/api/sleep/trends", nil)
    assert.Equal(t, 400, resp.StatusCode)
}
```

```typescript
// Frontend: sleep-trends.spec.ts (Playwright)
test('sleep trends page renders loading state', async ({ page }) => {
  await page.goto('/dashboard/sleep');
  await expect(page.getByTestId('chart-skeleton')).toBeVisible();
});

test('date range selector switches between 30/60/90 days', async ({ page }) => {
  await page.goto('/dashboard/sleep');
  await page.getByRole('tab', { name: '60 days' }).click();
  await expect(page.getByTestId('sleep-chart')).toBeVisible();
});

test('clicking a data point shows detail card', async ({ page }) => {
  await page.goto('/dashboard/sleep');
  await page.getByTestId('chart-point-0').click();
  await expect(page.getByTestId('sleep-detail-card')).toBeVisible();
});
```

### Topology influence
- **Backend topology:** The SDET must test all HTTP status codes listed in the Backend Route Coverage Matrix (200, 400, 401, 404).
- **Frontend topology:** The SDET must test all 5 component states in the Frontend Component State Matrix.

---

## Step 3: `/step3-build` (The Autonomous Factory)

**Roles:** Principal Backend Engineer + Principal Frontend Engineer
**Phases:** Build

### What happens

This step can run in **parallel via git worktrees** since the API contracts are locked:

**Backend worktree:**
```bash
$ go test ./internal/handler/sleep_trends_test.go
# ✘ 3 failing → implement handler
$ go test ./internal/handler/sleep_trends_test.go
# ✔ 3 passed — Exit Code 0
```

**Frontend worktree:**
```bash
$ npx playwright test tests/sleep-trends.spec.ts
# ✘ 3 failing → implement components
$ npx playwright test tests/sleep-trends.spec.ts
# ✔ 3 passed — Exit Code 0
```

### Topology influence
- **Backend topology:** Real database calls, no mocking. Tests must hit the actual data layer.
- **Frontend topology:** Every component renders all 5 states. No `// TODO: handle error` stubs.

---

## Step 4: `/step4-audit` (The Jury)

**Roles:** Security Engineer + SDET
**Phases:** Test, Review, Audit

### What happens

**SDET attack patterns (backend):**
- Range parameter injection: `range=30; DROP TABLE`
- Authentication bypass: request without auth token
- N+1 query check: does the trends endpoint issue 30 individual queries?

**SDET attack patterns (frontend):**
- What happens when the API is slow (5+ seconds)?
- What happens with zero data points (new user)?
- Responsive: does the chart work at 375px mobile width?

**Security Engineer:**
- Are sleep scores PII? (Yes — health data)
- Is the API properly authenticated?
- Does the detail endpoint leak other users' data?

### Topology influence
- **Backend topology:** The audit explicitly checks for N+1 queries and tests idempotency.
- **Frontend topology:** The audit verifies all 5 component states render correctly.

### Output
```
.agent/AUDIT_FINDINGS.md

## Findings

### [HIGH] N+1 query in trends endpoint
The handler calls `GetSleepForDate()` in a loop for each day in the range.
With 90-day range, this issues 90 queries.

**Fix:** Use `GetSleepRange(startDate, endDate)` batch query.

### [MEDIUM] Missing error state in chart component
When the API returns 500, the chart shows an infinite spinner instead of
the error state designed in the UX spec.
```

---

## Step 5: `/step5-ship` (The Gatekeeper)

**Roles:** DevOps Engineer + Principal Engineer
**Phases:** Integrate, Ship

### What happens

1. **Integrate:**
   - Merge backend and frontend branches
   - Strip any stub data or mock API responses
   - Verify the Stub Audit Tracker in `STATUS.md` is clear
   - Run full integration test with real backend serving real frontend
2. Run the complete test suite (backend + frontend + e2e)
3. Deploy backend, then frontend
4. Archive feature docs to `docs/archive/sleep-trends/`
5. Reset `STATUS.md` to idle

### Topology influence
- **Backend topology:** The Integrate phase explicitly checks that no mocks survived into production code.
- **Frontend topology:** The Stub Audit Tracker must show zero active stubs before shipping.

---

## Standalone Phase: `/fix`

**A week later**, users report the chart crashes when a day has `null` sleep data (e.g., they didn't wear the device).

```
/fix

Bug: Sleep trends chart crashes with "Cannot read property 'sleepScore' of null"
when a day in the range has no recorded sleep data. The API returns null for
that day but the chart component doesn't handle it.
```

The agent:
1. **Diagnoses:** The API returns `null` entries, the chart maps over them without filtering
2. **Patches:** Filters null entries and shows gaps in the chart line
3. **Verifies:** Adds a regression test with a dataset containing null entries
4. **Done.**

---

## Standalone Phase: `/review`

**After shipping 3 features** in quick succession, you invoke a periodic health check:

```
/architect

Review the current state of this codebase. Have the last 3 features
introduced any architectural drift? Are there emerging patterns that
should be formalized or one-off hacks that should be reconciled?
```

The Architect:
1. **Reads** `ARCHITECTURE.md`, all recent code changes
2. **Identifies** that 3 different data-fetching patterns have crept in (React Query, SWR, and raw fetch)
3. **Recommends** standardizing on React Query and documents the decision in `ARCHITECTURE.md`
4. **No code changes** — the Architect only writes markdown.
