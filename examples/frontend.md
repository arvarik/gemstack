# Example: Frontend Project — `[frontend]`

A walkthrough of the Gemstack 5-step workflow for a **frontend-only** project like a Next.js blog, a static site, or a single-page application with no separate backend.

**Topology:** `[frontend]`
**Active Guardrails:** `frontend.md` — component state coverage, hydration safety, state management discipline
**Example Project:** A Next.js personal blog with MDX content and static generation

---

## The Feature

> "Add a search page that lets readers filter blog posts by title, tags, and content. Results should update as the user types with debounced input."

---

## Step 1: `/step1-spec` (The Contract)

**Roles:** Product Visionary + UI/UX Designer + Architect
**Phases:** Ideate, Design

### What happens

The **Product Visionary** defines the pain and the vision:
- **Pain:** Readers with 50+ posts can't find anything. They scroll aimlessly.
- **Vision:** A search bar that feels like Raycast — instant, keyboard-navigable, zero-friction.
- **Success:** A reader finds a specific post within 3 seconds of landing on the search page.

The **UI/UX Designer** specifies the interaction design:
- Search input with debounced updates (300ms)
- Results list showing title, excerpt, matching tags highlighted
- All 5 states designed: empty (prompt text), loading (skeleton), success (results), error (retry), partial (some matches)
- Keyboard navigation: arrow keys to move, Enter to open, Esc to clear
- Responsive: full-width on mobile, constrained on desktop

The **Architect** locks in the contracts:
- No new API routes (frontend-only — search happens client-side)
- Search index built at build time via Velite
- New types exported: `SearchResult`, `SearchIndex`
- Route: `/search` as a new page

### Topology influence
The **frontend topology** requires the UI/UX Designer to design all 5 component states (empty, loading, success, error, partial). This is enforced — you can't skip them.

### Output files
```
docs/designs/2026-04-15-search-page.md      # UX spec with all states
.agent/ARCHITECTURE.md                       # Updated with SearchResult type, /search route
.agent/STATUS.md                             # [STATE: READY_FOR_TRAP]
```

---

## Step 2: `/step2-trap` (Setting the Trap)

**Roles:** Principal Engineer + SDET
**Phases:** Contract & Plan

### What happens

The **Principal Frontend Engineer** writes the task plan:
```
docs/plans/2026-04-15-search-page.md

Tasks:
1. Create search index generation in velite.config.ts (trivial)
2. Create SearchBar component with debounced input (moderate)
3. Create SearchResults component with keyboard nav (complex)
4. Create /search page composing both components (moderate)
5. Add search link to main navigation (trivial)
```

The **SDET** reads the contracts and writes the **failing test suite**:
```typescript
// tests/search.spec.ts (Playwright)

test('search page renders empty state initially', async ({ page }) => {
  await page.goto('/search');
  await expect(page.getByText('Search posts by title, tag, or content')).toBeVisible();
});

test('typing filters results with debounce', async ({ page }) => {
  await page.goto('/search');
  await page.getByRole('searchbox').fill('nextjs');
  await page.waitForTimeout(400); // debounce + render
  await expect(page.getByTestId('search-results')).toBeVisible();
});

test('empty search shows no-results state', async ({ page }) => {
  await page.goto('/search');
  await page.getByRole('searchbox').fill('xyznonexistent');
  await page.waitForTimeout(400);
  await expect(page.getByText('No posts found')).toBeVisible();
});

test('keyboard navigation works', async ({ page }) => {
  await page.goto('/search');
  await page.getByRole('searchbox').fill('react');
  await page.waitForTimeout(400);
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  await expect(page).not.toHaveURL('/search');
});
```

### Topology influence
The **frontend topology** requires the SDET to test all 5 component states in the Frontend Component State Matrix. The SDET adds rows for `SearchBar` and `SearchResults` to `TESTING.md`.

### Output files
```
docs/plans/2026-04-15-search-page.md        # Step-by-step task list
tests/search.spec.ts                         # Failing test suite
.agent/TESTING.md                            # Updated component state matrix
.agent/STATUS.md                             # [STATE: READY_FOR_BUILD]
```

### The tests MUST fail
```bash
$ npx playwright test tests/search.spec.ts
# ✘ 4 tests failed — /search page doesn't exist yet
```

---

## Step 3: `/step3-build` (The Autonomous Factory)

**Roles:** Principal Frontend Engineer
**Phases:** Build

### What happens

The Builder reads the plan and implements each task in order. They run the test suite in the terminal after each change and loop until all tests pass.

```bash
# The Builder's loop:
$ npx playwright test tests/search.spec.ts
# ✘ 3 failing → fix SearchBar component
$ npx playwright test tests/search.spec.ts
# ✘ 1 failing → fix keyboard navigation
$ npx playwright test tests/search.spec.ts
# ✔ 4 tests passed — Exit Code 0
```

### Topology influence
The **frontend topology** enforces:
- Every component handles all 5 states (empty, loading, success, error, partial)
- No `useEffect` for data fetching if the project uses React Query/SWR
- Semantic HTML and keyboard accessibility
- No layout shift or unnecessary re-renders

### Output files
```
src/app/search/page.tsx                      # New search page
src/components/search-bar.tsx                # SearchBar component
src/components/search-results.tsx            # SearchResults component
velite.config.ts                             # Updated with search index
src/components/nav.tsx                       # Updated with search link
.agent/STATUS.md                             # [STATE: READY_FOR_AUDIT]
```

---

## Step 4: `/step4-audit` (The Jury)

**Roles:** Security Engineer + SDET
**Phases:** Test, Review, Audit

### What happens

Fresh context window. The agents have never seen the Builder's code before.

The **SDET** runs systematic attack patterns:
- Empty/null input in search box
- Extremely long input (10,000 characters)
- Special characters (`<script>`, SQL injection strings)
- Rapid typing (no debounce bypass)
- Browser back/forward during search

The **Security Engineer** checks:
- XSS risk: is search input sanitized before rendering in results?
- No sensitive data in the client-side search index
- No API keys or secrets in the build-time index

### Output
```
.agent/AUDIT_FINDINGS.md

## Findings

### [MEDIUM] Search input not sanitized
The search results component renders `dangerouslySetInnerHTML` for highlighting
matched terms. A user could inject `<script>` tags via the search query.

**Fix:** Use a text-based highlighter that escapes HTML entities, not innerHTML.

### [LOW] Search index includes draft posts
The Velite search index builder doesn't filter `draft: true` posts.

**Fix:** Add `where: { draft: false }` to the index query.
```

### Routing Loop
Issues found → spawn `/step3-build` to fix them → re-run audit until clean.

---

## Step 5: `/step5-ship` (The Gatekeeper)

**Roles:** DevOps Engineer + Principal Engineer
**Phases:** Integrate, Ship

### What happens

1. **Integrate:** Strip any stub data (none in this case — frontend-only with build-time data)
2. Merge the feature branch into main
3. Run the full test suite one final time
4. Deploy (e.g., Vercel auto-deploy on merge)
5. Clean up: move design/plan docs to `docs/archive/search-page/`
6. Reset `STATUS.md` to idle

### Output files
```
docs/archive/search-page/                   # Archived feature docs
.agent/STATUS.md                             # Reset to idle
```

---

## Standalone Phase: `/fix`

**Two weeks later**, a user reports that searching for posts with apostrophes in titles (e.g., "What's New in Next.js") returns no results.

Instead of the full 5-step, you invoke `/fix`:

```
/fix

Bug: Searching for "what's" returns no results, but "whats" works fine.
The search index strips apostrophes during indexing but the query
doesn't strip them, causing a mismatch.
```

The agent:
1. **Diagnoses:** Reads the search index builder and query logic
2. **Patches:** Normalizes both the index and query to strip punctuation
3. **Verifies:** Runs the existing test suite + adds a regression test
4. **Done.** No Spec, no Trap, no Audit ceremony needed.
