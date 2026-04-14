# Agent Context Bootstrapping Instructions

You are an expert Software Architect and Tech Lead. Your objective is to bootstrap the `.agent/` context directory for this repository. 

The `.agent/` directory acts as the permanent memory and rules engine for all future AI agents operating in this codebase. By establishing strict architectural boundaries, style rules, and testing strategies, you ensure that agents do not drift, hallucinate styles, or break conventions as the project scales.

## Your Task

The user has placed template files in the `.agent/` directory of this project. Your job is to systematically analyze the existing codebase, read the templates, and **overwrite the templates with highly specific, concrete details extracted from the project.**

---

## Phase 1: Deep Codebase Analysis

Before writing any files, you MUST use your search and read tools to investigate the target project:

1. **Tech Stack & Configs**: Read `package.json`, `next.config.js` (or similar), `vite.config.ts`, `tailwind.config.js`, and `tsconfig.json`. Understand the exact versions and build tooling.
2. **Architecture & Routing**: Examine the structure of `src/app`, `src/pages`, or backend routing directories. Understand how requests flow (e.g., RSCs to Server Actions, or Express routes to controllers).
3. **Database & State**: Review ORM schemas (e.g., `prisma/schema.prisma`, `src/db/schema.ts`, `models/*.py`). Identify the primary entities and relationships. Check how data fetching is handled on the client (e.g., React Query, Apollo, Redux, native fetch).
4. **Styling & UI**: Analyze core UI components (e.g., `src/components/ui/`). Understand the color token usage, class naming conventions, and layout rules. Identify if a component library (e.g., Shadcn, Radix) is used.
5. **Testing**: Check testing configs (`vitest.config.ts`, `playwright.config.ts`, `jest.config.js`) and read a few existing test files to determine the testing paradigms and commands.
6. **AI & External Integrations**: Look for AI SDKs, third-party API clients, and adapter patterns.

---

## Phase 2: Template Population & Overwrite

Now, read the template files currently located in the `.agent/` directory. Use their exact structure and headers as your baseline, but **replace the placeholder text with the concrete facts you discovered in Phase 1.** Write the finalized content back to the same files, overwriting the templates.

### 1. `.agent/ARCHITECTURE.md`
- **Goal**: The definitive anchor for system design.
- **Instructions**: Detail the exact tech stack. Map out the data flow (e.g., "Client Components -> Server Actions -> Drizzle -> SQLite"). Document all core database entities and their relational rules (e.g., cascading deletes). Define the API contracts (methods, paths, request/response shapes) for the primary endpoints. Note any AI providers, external APIs, or complex integrations (like vector embeddings or Cron jobs).

### 2. `.agent/STYLE.md`
- **Goal**: Enforce visual identity and structural code patterns.
- **Instructions**: Extract the exact design system rules. Define the primary colors, surface hierarchy, and spacing tokens used in the repo. Document concrete component patterns (e.g., show the exact Tailwind classes used for a primary button). 
- **CRITICAL**: Formulate explicit "Anti-Patterns (FORBIDDEN)" based on what the codebase avoids (e.g., "NEVER use `useEffect` for data fetching", "NEVER use `border-gray-200` for sectioning").

### 3. `.agent/TESTING.md`
- **Goal**: Track test methods and execution evidence.
- **Instructions**: Document the exact CLI commands to run tests (e.g., `npm run test:ui`). Keep the "Execution Evidence Rules" from the template intact. Setup the empty scenario tables ready for the first feature.

### 4. `.agent/PHILOSOPHY.md`
- **Goal**: The soul of the product.
- **Instructions**: Read the project's `README.md`. Infer the core pain point the project solves. Synthesize 3-5 core beliefs that drive technical and product decisions (e.g., "Speed over features", "Offline-first"). Define explicit anti-goals (What This Is NOT). *If the product purpose is completely ambiguous, stop and ask the user for a 1-paragraph description before writing this file.*

### 5. `.agent/STATUS.md`
- **Goal**: The single source of truth for progress.
- **Instructions**: Initialize the tracking state. Set "Current Focus" to "Project Bootstrapped". Leave the lifecycle checkboxes (Ideate, Design, Plan, etc.) unchecked. Leave "Relevant Files" empty.

---

## Phase 3: Docs Scaffolding Verification

Ensure the following directory structure exists in the project root to support the roles/phases workflow. Create them with `.gitkeep` files if they are missing:
- `docs/explorations/.gitkeep`
- `docs/designs/.gitkeep`
- `docs/plans/.gitkeep`
- `docs/archive/.gitkeep`

---

## Execution Rules for the LLM
- **No Hallucinations**: If a project does not have a database, simply write "N/A - No database utilized" in the database section. Do not invent details.
- **Extreme Specificity**: Do not write generic statements like "Uses Tailwind for styling." Write "Uses Tailwind CSS v4 with a strict tokenized surface hierarchy (`bg-surface`, `bg-surface-container`)."
- **Do not delete template sections**: If a section from the template is not applicable, keep the header and write "N/A - [Reason]".
- **Completion**: Once all 5 files are successfully overwritten and the `docs/` folders are verified, inform the user that the project is bootstrapped and ready for the `/ideate` phase.