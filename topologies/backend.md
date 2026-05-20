---
name: backend
description: Backend topology guardrails — data integrity, deterministic testing, mocking prevention
---
# Topology: Backend

<thinking_process>
The Backend topology focuses on "Determinism" and "Data Integrity." Think about:
1. Preventing the "Mocking Illusion" (tests passing with fake data).
2. Ensuring N+1 query safety.
3. Protecting the database schema as the source of truth.
</thinking_process>

<guardrails>
## Guardrail 1: The Mocking Illusion
LLM agents often mock database calls to make tests pass. This is FORBIDDEN.

### Rules for the SDET (Trap Phase)
- Integration tests MUST hit a real, ephemeral database (e.g., Docker container or in-memory SQLite).
- Use randomized test data (e.g., Faker) to prevent the LLM from hardcoding test values in route handlers.

### Rules for the Builder (Build Phase)
- You may NOT alter the database schema to pass a test. If a schema change is needed, yield to the Architect.
- Use **Drizzle ORM** where possible for its performance and type safety.

## Guardrail 2: N+1 Query Awareness
When implementing nested data fetching, the Builder must explicitly document the query strategy.
- **Preferred**: Use Drizzle `with` relations or explicit SQL JOINs.
- **Forbidden**: Fetching related data in a loop.

## Guardrail 3: Transaction Isolation
All mutations must be wrapped in transactions where atomicity is required. Tests must roll back on teardown to prevent test pollution.
</guardrails>

<reporting>
### Backend Route Coverage Matrix
The SDET must populate this in `TESTING.md` during the Trap phase:

| Endpoint | Method | 200 OK | 400 Bad Req | 401/403 Auth | Idempotent |
|----------|--------|--------|-------------|--------------|------------|
| /api/... | ...    | [ ]    | [ ]         | [ ]          | [ ]        |
</reporting>
