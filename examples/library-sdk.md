# Example: Library / SDK Project — `[library-sdk, backend]`

A walkthrough of the Gemstack 5-step workflow for a **library or SDK** project that is consumed as a dependency by other projects — e.g., a Go API client wrapper, an npm package, or a Python library.

**Topology:** `[library-sdk, backend]`
**Active Guardrails:** `library-sdk.md` + `backend.md` — API surface stability, backward compatibility, zero-dependency discipline, anti-mocking
**Example Project:** A Go SDK wrapper for a REST API (consumed via `go get`)

---

## The Feature

> "Add support for the Workout endpoints — `GetWorkouts()`, `GetWorkout(id)`, and `CreateWorkout()`. The upstream API just released these endpoints and our SDK consumers are requesting support."

---

## Step 1: `/step1-spec` (The Contract)

**Roles:** Product Visionary + UI/UX Designer + Architect
**Phases:** Ideate, Design

### What happens

For a library/SDK, roles shift context:
- The **Product Visionary** thinks about the SDK *consumer's* pain, not an end user.
- The **UI/UX Designer** designs the *API surface* (the "UI" of a library is its exported functions).
- The **Architect** locks in the public API contract.

**Product Visionary:**
- **Pain:** SDK consumers have to make raw HTTP calls for workout data while every other resource has a typed wrapper.
- **Success:** A consumer calls `client.GetWorkouts(ctx)` and gets back `[]Workout` with zero HTTP knowledge needed.

**Architect locks in the API surface:**

```go
// Added to ARCHITECTURE.md — Public API Contract

type Workout struct {
    ID        int       `json:"id"`
    SportID   int       `json:"sport_id"`
    Start     time.Time `json:"start"`
    End       time.Time `json:"end"`
    Score     float64   `json:"score"`
    Strain    float64   `json:"strain"`
}

// Exported functions (public API surface)
func (c *Client) GetWorkouts(ctx context.Context, params *GetWorkoutsParams) ([]Workout, error)
func (c *Client) GetWorkout(ctx context.Context, id int) (*Workout, error)
func (c *Client) CreateWorkout(ctx context.Context, input CreateWorkoutInput) (*Workout, error)
```

### Topology influence
The **library-sdk topology** requires:
- All exported types and functions documented in `ARCHITECTURE.md` before implementation
- Backward compatibility analysis: do these additions break any existing API?
- Zero new dependencies: the SDK must not add any external packages for this feature

---

## Step 2: `/step2-trap` (Setting the Trap)

**Roles:** Principal Engineer + SDET
**Phases:** Contract & Plan

### What happens

The **Principal Backend Engineer** writes the task plan:
```
1. Define Workout types and CreateWorkoutInput (trivial)
2. Implement GetWorkouts with pagination support (moderate)
3. Implement GetWorkout by ID (trivial)
4. Implement CreateWorkout with input validation (moderate)
5. Add example tests for godoc (trivial)
```

The **SDET** writes the failing test suite:

```go
func TestGetWorkouts(t *testing.T) {
    client := newTestClient(t)
    workouts, err := client.GetWorkouts(context.Background(), nil)
    require.NoError(t, err)
    require.NotEmpty(t, workouts)
    assert.Greater(t, workouts[0].ID, 0)
}

func TestGetWorkouts_WithParams(t *testing.T) {
    client := newTestClient(t)
    params := &GetWorkoutsParams{Limit: 5}
    workouts, err := client.GetWorkouts(context.Background(), params)
    require.NoError(t, err)
    assert.LessOrEqual(t, len(workouts), 5)
}

func TestGetWorkout_NotFound(t *testing.T) {
    client := newTestClient(t)
    _, err := client.GetWorkout(context.Background(), 99999999)
    require.Error(t, err)
    // Should return a typed error, not a generic one
    var apiErr *APIError
    require.ErrorAs(t, err, &apiErr)
    assert.Equal(t, 404, apiErr.StatusCode)
}

func TestCreateWorkout_Valid(t *testing.T) {
    client := newTestClient(t)
    input := CreateWorkoutInput{SportID: 1, Start: time.Now().Add(-1 * time.Hour), End: time.Now()}
    workout, err := client.CreateWorkout(context.Background(), input)
    require.NoError(t, err)
    assert.Equal(t, 1, workout.SportID)
}

func TestCreateWorkout_InvalidInput(t *testing.T) {
    client := newTestClient(t)
    input := CreateWorkoutInput{} // Missing required fields
    _, err := client.CreateWorkout(context.Background(), input)
    require.Error(t, err)
}
```

### Topology influence
- **Backend topology:** Tests must hit a real HTTP server (test server or integration), not mocked responses. The anti-mocking rule is enforced.
- **Library-sdk topology:** The SDET adds rows to the Backend Route Coverage Matrix for each new exported function.

### Key point: tests use `go test -race`
```bash
$ go test -race ./...
# ✘ 5 failing — functions don't exist yet
```

---

## Step 3: `/step3-build` (The Autonomous Factory)

**Roles:** Principal Backend Engineer
**Phases:** Build

### What happens

The Builder implements the workout functions, following existing SDK patterns exactly (same error handling, same pagination approach, same naming conventions).

```bash
$ go test -race ./...
# ✘ 3 failing → implement missing functions
$ go test -race ./...
# ✘ 1 failing → fix error type assertion
$ go test -race ./...
# ✔ All passed — Exit Code 0
```

### Topology influence
- **Library-sdk topology enforces:**
  - Follow existing naming patterns (`GetWorkouts` not `FetchWorkouts` or `ListWorkouts`)
  - Return pointer for single resources, slice for collections (matching existing SDK pattern)
  - Error types match existing `APIError` pattern
  - No new dependencies added to `go.mod`
  - Godoc comments on all exported types and functions
- **Backend topology enforces:**
  - Input validation at the boundary (CreateWorkoutInput)
  - Proper error propagation (don't swallow errors)
  - Context propagation through all calls

---

## Step 4: `/step4-audit` (The Jury)

**Roles:** Security Engineer + SDET
**Phases:** Test, Review, Audit

### What happens

**SDET verification:**
- Run `go test -race -count=3 ./...` (multiple runs to catch race conditions)
- Run `golangci-lint run` for static analysis
- Check that example tests exist (they appear in godoc)
- Verify API surface matches the contract in `ARCHITECTURE.md`

**Security Engineer:**
- Is user input properly validated before sending to the upstream API?
- Could a malicious `CreateWorkoutInput` cause issues upstream?
- Are API credentials properly scoped per-request via context?

### Topology influence
- **Library-sdk topology:** The audit includes an **API surface snapshot diff** — comparing the current exported symbols against the documented surface in `ARCHITECTURE.md` to catch accidental breaking changes.

### Output
```
.agent/AUDIT_FINDINGS.md

## Findings

### [LOW] Missing godoc on CreateWorkoutInput fields
The struct fields lack godoc comments explaining valid ranges
(e.g., SportID must be 0-127 per the API docs).

**Fix:** Add field-level documentation.
```

---

## Step 5: `/step5-ship` (The Gatekeeper)

**Roles:** DevOps Engineer + Principal Engineer
**Phases:** Integrate, Ship

### What happens

For a library/SDK, "shipping" is different from a web app:

1. **Integrate:** No stubs to strip (SDK has no frontend)
2. Run the full test suite with `-race` flag
3. Update `CHANGELOG.md` with the new workout endpoints
4. Tag a new minor version: `git tag v0.5.0` (minor bump — new features, no breaking changes)
5. Push the tag: `git push origin v0.5.0`
6. Consumers can now `go get github.com/user/sdk@v0.5.0`
7. Archive feature docs, reset `STATUS.md`

### Topology influence
- **Library-sdk topology:** Enforces **semver discipline** — new features = minor bump, breaking changes = major bump. The gatekeeper must verify no existing tests broke.

---

## Standalone Phase: `/fix`

**A consumer reports** that `GetWorkouts` panics when the upstream API returns an empty `data` array (new accounts with no workouts).

```
/fix

Bug: GetWorkouts panics with "index out of range" when the API returns
{"data": [], "next_token": null}. The pagination logic assumes data is
non-empty and tries to access data[0].
```

The agent:
1. **Diagnoses:** The pagination cursor uses `data[len(data)-1].ID` without checking for empty
2. **Patches:** Adds an early return for empty data slices
3. **Verifies:** Adds a regression test with empty API response
4. **Tags:** `v0.5.1` (patch bump — bug fix, no API change)
