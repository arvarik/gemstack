---
name: frontend
description: Frontend topology guardrails — Next.js 15, hydration safety, and state management
---
# Topology: Frontend

<thinking_process>
The Frontend topology focuses on "Experiential Fidelity" and "Performance." Think about:
1. Next.js 15 Server Components vs. Client Components.
2. Hydration mismatches (often caused by AI-generated non-deterministic components).
3. Accessibility (A11y) as a first-class citizen.
</thinking_process>

<guardrails>
## Guardrail 1: Next.js 15 Architecture
- Use **Server Components** by default. Only use `'use client'` for interactive leaves.
- Use **Server Actions** for mutations. Avoid client-side `fetch` to internal API routes where possible to improve security and performance.

## Guardrail 2: Hydration Safety
- Avoid using non-deterministic data (e.g., `Math.random()`, `new Date()`) directly in the initial render without `useEffect` or `suppressHydrationWarning`.

## Guardrail 3: Component Atomicity
- Follow a "Shadcn-style" atomic component pattern. Keep UI logic separate from business logic.
- Every component must have an associated `.spec.ts` (Playwright) if it contains complex interaction logic.

## Guardrail 4: A11y First
- Use semantic HTML tags (`<main>`, `<nav>`, `<section>`).
- Ensure all interactive elements have unique IDs and ARIA labels where necessary.
</guardrails>

<reporting>
### Frontend Lighthouse/CWV Targets
The SDET should record these in `TESTING.md`:

| Metric | Target | Current |
|--------|--------|---------|
| LCP    | < 2.5s | —       |
| CLS    | < 0.1  | —       |
| INP    | < 200ms| —       |
</reporting>
