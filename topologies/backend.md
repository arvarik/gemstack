---
name: backend
description: Backend topology guardrails — data integrity, deterministic testing, mocking prevention
---
# Topology: Backend

**Core Focus:** Determinism and Data Integrity.

**When this topology applies:** Projects that are backend-only services, CLI tools with data persistence, APIs without a frontend, or the backend portion of a full-stack project.

_This profile is a behavioral modifier. It does not replace any role or workflow — it adds domain-specific constraints on top of whatever workflow the agent is currently executing. Read this profile when the project's `ARCHITECTURE.md` declares `backend` in its Topology field._

---

## Guardrail 1: The Mocking Illusion

LLM agents will mock database calls, HTTP clients, and external services in production code to make tests pass. This is the single most dangerous failure mode in backend development with AI agents.

### Rules for the SDET (Trap Phase)

- Integration tests MUST hit a real, ephemeral database (Docker Testcontainers, in-memory SQLite, or a test-specific database instance). Mocking the database layer in integration tests is FORBIDDEN.
- Use randomized test data (e.g., Faker libraries, random UUIDs, random strings) so the LLM cannot predict exact test values and hardcode them in route handlers.
- Emphasize negative constraints: at least 40% of test scenarios must validate that invalid inputs are correctly rejected. These cannot be faked by hardcoding happy-path responses.
- Test idempotency: calling the same mutation twice must not create duplicates or corrupt state.

### Rules for the Builder (Build Phase)

- You may NOT alter the database schema to pass a test. If a test fails due to schema mismatch, yield to the Architect.
- Every database operation that modifies data must be wrapped in error handling. Silent failures (swallowing errors, empty catch blocks) are FORBIDDEN.

### Rules for the Auditor (Audit Phase)

- Search for hardcoded return values in route handlers. If a handler returns a static object without querying the database, flag it as a **Mocking Illusion**.
- Check that test assertions use dynamic/randomized values, not hardcoded strings that match hardcoded responses.

---

## Guardrail 2: Transaction Isolation for Tests

All database test scenarios must execute within isolated transactions that roll back on teardown, OR use a fresh ephemeral database per test suite. This prevents test pollution where one test's side effects cause another test to pass or fail incorrectly.

**Applies to:** SDET (Trap phase), Builder (Build phase).

---

## Guardrail 3: N+1 Query Awareness

When implementing nested data fetching (e.g., "get all users with their posts"), the Builder must explicitly document the query strategy in a code comment. Acceptable strategies vary by stack:

- **Go + sqlc:** JOINs in the SQL query file.
- **Node.js + Drizzle/Prisma:** `with` relations or explicit `include`.
- **Python + SQLAlchemy:** `joinedload()` / `selectinload()`.

The Auditor must flag any endpoint that fetches related data in a loop without batching.

**Applies to:** Builder (Build phase), Auditor (Audit phase).

---

## Reporting: Route Coverage Matrix

The SDET must populate this table in the project's `TESTING.md` for every API endpoint during the Trap phase:

```markdown
## Backend Route Coverage Matrix

| Endpoint | Method | 200 OK | 400 Bad Req | 401/403 Auth | 404 Not Found | Idempotent | Edge Cases |
|----------|--------|--------|-------------|--------------|---------------|------------|------------|
| /api/v1/users | GET | [ ] | [ ] | [ ] | N/A | N/A | [ ] pagination bounds |
| /api/v1/users | POST | [ ] | [ ] | [ ] | N/A | [ ] | [ ] duplicate email |
| /api/v1/users/:id | DELETE | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] cascade effects |
```

All cells must show PASS with execution evidence or FAIL with reproduction steps. "PASS" without evidence is treated as UNTESTED.
