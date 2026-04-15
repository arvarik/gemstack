---
name: frontend
description: Frontend topology guardrails — visual verification, state management, hydration safety
---
# Topology: Frontend

**Core Focus:** Visual State Coverage and Integration Discipline.

**When this topology applies:** Projects with a web UI (React, Next.js, Svelte, Vue), or the frontend portion of a full-stack project.

_This profile is a behavioral modifier. It does not replace any role or workflow — it adds domain-specific constraints on top of whatever workflow the agent is currently executing. Read this profile when the project's `ARCHITECTURE.md` declares `frontend` in its Topology field._

---

## Guardrail 1: Component State Coverage

Every interactive UI component must be tested across all visual states. The five states come from the UI/UX Designer role's requirement: "Design all states: empty, loading, partial, success, error." This guardrail enforces that requirement in testing.

### Rules for the SDET (Trap Phase)

Populate this matrix in the project's `TESTING.md` for every interactive component:

```markdown
## Frontend Component State Matrix

| Component | Empty State | Loading State | Success State | Error State | Partial State |
|-----------|-------------|---------------|---------------|-------------|---------------|
| UserDashboard | [ ] | [ ] | [ ] | [ ] | [ ] |
| SearchResults | [ ] | [ ] | [ ] | [ ] | [ ] |
| SettingsForm | [ ] N/A | [ ] | [ ] | [ ] | [ ] N/A |
```

### What Can Be Automated

Write Playwright or component tests that render each state and assert DOM structure. Mark these PASS/FAIL with execution evidence.

### What Cannot Be Fully Automated

**Structural verification (automated):** If the agent has vision capabilities (VLM), use Playwright or equivalent to take screenshots of each component state (empty, loading, success, error, partial). Feed the screenshots back into the agent context to verify structural correctness — component renders, layout isn't broken, error states display correctly, elements are present and positioned.

**Aesthetic verification (human):** Visual *quality* — brand alignment, color harmony, spacing feel, animation polish — cannot be reliably judged by current VLMs. Mark aesthetic checks as `NEEDS_HUMAN_REVIEW` per the QA Engineer role rules. Do not remove this designation even when VLM structural checks pass.

---

## Guardrail 2: Hydration Safety (SSR Frameworks Only)

**Skip this guardrail for SPA-only projects** (e.g., Vite + React without SSR). It only applies when the project's `ARCHITECTURE.md` lists an SSR framework (Next.js, SvelteKit, Nuxt, Remix, Astro with islands).

### Rules for the QA Engineer (Audit Phase)

1. Check the terminal build output for hydration mismatch warnings.
2. Run `next build` (or equivalent) and verify zero hydration errors in the output.
3. Test that client-side interactivity works after initial server render.

### Common Causes to Check

- `Date.now()`, `Math.random()`, or browser-only APIs used in components that render on the server.
- Conditional rendering based on `window` or `document` objects without proper `useEffect` guards.
- Third-party scripts injected at different times on server vs. client.

---

## Guardrail 3: State Management Discipline

LLM agents have a tendency to import multiple state management libraries in the same project (Redux + Zustand + React Query simultaneously). This creates conflicting patterns and makes the codebase unmaintainable.

### Rules for the Builder (Build Phase)

- Use ONLY the state management approach documented in the project's `STYLE.md`.
- If `STYLE.md` doesn't specify one, default to the lightest option that satisfies the use case:
  - **Server state**: React Query / SWR / TanStack Query.
  - **Client state**: Built-in `useState` / `useReducer`.
  - **Complex client state**: Zustand (if already in the project) or Context + `useReducer`.
- Adding a new state management dependency requires Architect approval (yield and prompt).

### Rules for the Auditor (Audit Phase)

- Check `package.json` for multiple state management dependencies. Flag if more than one pattern coexists without justification in `STYLE.md`.
- Search for conflicting import patterns (e.g., both `zustand` and `redux` imports in the same project).

---

## Guardrail 4: Stub Tracking (Full-Stack Projects Only)

When both `frontend` and `backend` topologies are active, the frontend Builder will create stubs and mocks to develop against API contracts before the backend is ready.

### Rules for the Builder (Build Phase)

- Track every stub in the **Stub Audit Tracker** section of `STATUS.md`.
- Use a consistent stub pattern (MSW, inline mock data, or hardcoded arrays — pick one per project).
- Tag stub locations with a searchable marker comment: `// STUB: [endpoint]` or `/* STUB: [endpoint] */`.

### Rules for the Ship Workflow

- Before shipping, the Stub Audit Tracker in `STATUS.md` must show all stubs as `REMOVED`.
- Run `grep -r "// STUB:" src/` to verify zero remaining stubs in the codebase.
