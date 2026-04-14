# Agent Context Bootstrapping Instructions

You are an expert Software Architect and Tech Lead. Your objective is to bootstrap the `.agent/` context directory for this repository.

The `.agent/` directory acts as the permanent memory and rules engine for all future AI agents operating in this codebase. By establishing strict architectural boundaries, style rules, and testing strategies, you ensure that agents do not drift, hallucinate styles, or break conventions as the project scales.

## Your Task

The user has placed template files in the `.agent/` directory of this project. Your job is to systematically analyze the existing codebase, read the templates, and **overwrite the templates with highly specific, concrete details extracted from the project.**

---

## Phase -1: New vs Existing Project Detection

Before doing anything else, determine whether this is a **new project** (empty or near-empty repo) or an **existing project** with code already present.

### How to detect:
- If `package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, `Makefile`, `docker-compose.yml`, OR any `src/`, `cmd/`, `internal/`, `lib/` source directories exist → **Existing project**. Proceed to Phase 0.
- If the repo is empty or contains only a README and/or license → **New project**. Continue below.

### New Project Setup:
If this is a brand-new project with no code yet:

1. **Generate `.gitignore`** for the planned tech stack. At minimum include:
   ```
   node_modules/
   .env
   .env.local
   .venv/
   __pycache__/
   .DS_Store
   dist/
   build/
   .next/
   *.pyc
   ```
   Adapt to the specific stack (add `.vercel/`, `coverage/`, `bin/`, `vendor/`, `tmp/` as relevant).
   This MUST happen before the first commit to prevent secrets and build artifacts from entering git history.

2. **Create `.env.example`** with initial placeholder variables:
   ```
   # Copy this file to .env and fill in the values
   # DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   # (add environment variables as features require them)
   ```

3. **Initialize git** if not already done: `git init`

4. After completing the rest of the bootstrapping process, create an initial commit with the scaffold.

5. Set STATUS.md "Current Focus" to: "Project just bootstrapped. Ready for first feature ideation."

Then proceed to Phase 1 (skip Phase 0 and 0.5 — there is no legacy content to ingest).

---

## Phase 0: Legacy Context Ingestion

Before analyzing the codebase from scratch, check if existing AI agent context files already exist. These contain valuable rules that should be absorbed into the standardized `.agent/` structure:

1. **Check for legacy files**: Scan the repo root for any of these:
   - `.cursorrules` — Cursor/Copilot rules
   - `GEMINI.md` — Gemini CLI context
   - `AGENTS.md` — Generic agent instructions
   - `CLAUDE.md` — Claude Code context
   - `CONTRIBUTING.md` — Contributing guidelines (often contain code standards)
   - `DESIGN.md` / `design.md` — Design system or architecture documentation
   - Any existing `.agent/` files with project-specific content (NOT the templates you just placed)
2. **Absorb, don't discard**: Read each legacy file. Extract the rules, constraints, and patterns they define. Weave them into the appropriate `.agent/` template (e.g., DESIGN.md rules → STYLE.md, architectural boundaries → ARCHITECTURE.md invariants, code quality rules → STYLE.md anti-patterns).
3. **Deduplicate**: If the same rule appears in multiple legacy files, include it once in the most appropriate `.agent/` file.

---

## Phase 0.5: Pre-existing Content Migration

If this project already has content in `.agent/` or `docs/` from before the Gemstack bootstrapping, handle it as follows:

### Existing `.agent/` Directory
If the project already has an `.agent/` directory with **project-specific content** (not the templates you are about to populate):
1. Read and absorb ALL rules, patterns, and constraints from the existing files into your analysis notes.
2. **Delete the existing `.agent/` files** after reading them — they will be fully replaced by the new standardized versions you are creating.
3. **Exception**: Do NOT delete `.agent/workflows/` if it exists — these are project-specific slash commands that live alongside the context files.

### Existing `docs/` Directory
If the project already has a `docs/` directory with files:
1. **Identify the type of content** in the existing `docs/`:
   - **Agent/feature documentation** (design docs, architecture analyses, exploration notes, feature specs, strategy docs, implementation plans):
     → **Move** these files to `docs/archive/pre-gemstack/`. Create this directory if needed.
     → This preserves the content as historical reference while making room for the standardized lifecycle structure.
   - **Auto-generated content** (Swagger/OpenAPI specs like `swagger.json`/`docs.go`, JSDoc output, godoc pages, images, API reference):
     → **Leave in place**. These are build artifacts or assets, not agent documentation.
     → Create the Gemstack subdirectories (`docs/explorations/`, `docs/designs/`, etc.) alongside them.
2. **When in doubt**: If a file could be either, err on the side of moving it to `docs/archive/pre-gemstack/`. It's safer to archive than to accidentally overwrite.

---

## Phase 1: Deep Codebase Analysis

Before writing any files, you MUST use your search and read tools to investigate the target project:

### For All Projects:
1. **Tech Stack & Configs**: Read `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or equivalent to identify the exact language, runtime, framework versions, and dependencies.
2. **Build & Dev Tooling**: Read `vite.config.ts`, `next.config.js`, `tsconfig.json`, `tailwind.config.js`, `Dockerfile`, `docker-compose.yml`, `Makefile`, `.golangci.yml`, `sqlc.yaml`, or equivalent. Understand how the project is built, tested, and run.
3. **Architecture & Routing**: Examine the structure of `src/app`, `src/pages`, `server/routes`, `cmd/`, `internal/handler/`, or backend routing directories. Understand how requests flow.
4. **Database & State**: Review ORM schemas (e.g., `prisma/schema.prisma`, `src/db/schema.ts`, `models/*.py`, `migrations/`, `queries/query.sql`, Drizzle migrations). Identify primary entities, relationships, and critical constraints. Check for virtual tables, search indexes, hypertables, continuous aggregates, or vector stores.
5. **Error Handling**: Search for centralized error patterns (`AppError`, `asyncHandler`, error middleware, `if err != nil` patterns, custom error types, try/catch wrappers).
6. **Environment Variables**: Read `.env.example` (if it exists) to understand required configuration. Catalog all variables.

### For Frontend / Full-Stack Projects:
7. **Styling & UI**: Analyze core UI components (e.g., `src/components/ui/`). Understand color token usage, class naming conventions, and layout rules. Identify if a component library (e.g., Shadcn, Radix, Material UI) is used.
8. **State Management**: Identify the data fetching pattern (React Query, SWR, Apollo, Redux, Zustand, native fetch) and client state strategy.

### For Backend / CLI / Pipeline Projects:
9. **Concurrency Model**: Identify threading, async patterns, queue bounds, worker pools, goroutines, channels, mutexes, or event-loop constraints.
10. **Safety Invariants**: Search for "NEVER", "MUST", "CRITICAL" comments in the codebase — these reveal load-bearing constraints.

### For Go Projects:
11. **Project Layout**: Check for `cmd/`, `internal/`, `pkg/` standard Go project layout. Identify the binary entrypoints in `cmd/`.
12. **Build System**: Read `Makefile` targets — these are the primary dev interface (build, test, lint, setup, docker-up/down).
13. **Code Generation**: Check for `sqlc.yaml` (SQL-to-Go), `protobuf` definitions, `go generate` directives, or Swagger generation configs (`.swaggo`, `swag init`).
14. **Concurrency Patterns**: Look for goroutine usage, `sync.Mutex`, `sync.WaitGroup`, `context.Context` propagation, advisory locks, and channel patterns.

### For All Projects:
15. **Testing**: Check testing configs (`vitest.config.ts`, `playwright.config.ts`, `jest.config.js`, `pytest.ini`, `pyproject.toml [tool.pytest]`, `Makefile test target`) and read a few existing test files to determine testing paradigms, commands, and coverage expectations.
16. **AI & External Integrations**: Look for AI SDKs, third-party API clients, adapter patterns, rate limiters, OAuth2 flows, and caching layers.

---

## Phase 2: Template Population & Overwrite

Now, read the template files currently located in the `.agent/` directory. Use their exact structure and headers as your baseline, but **replace the placeholder text with the concrete facts you discovered during your analysis (Phases 0 through 1).** Write the finalized content back to the same files, overwriting the templates.

### 1. `.agent/ARCHITECTURE.md`
- **Goal**: The definitive anchor for system design.
- **Instructions**: Detail the exact tech stack with pinned versions. Map out the data flow (e.g., "Client Components → React Query → Express → Drizzle → SQLite" or "CLI → asyncio.TaskGroup → bounded queues → GPU worker" or "HTTP → go-chi middleware → handler → service → sqlc → PostgreSQL"). Document all core database entities and their relational rules (cascading deletes, virtual tables, hypertables, manual cleanup requirements). Define API contracts (methods, paths, request/response shapes) for primary endpoints. For SDK libraries, document the exported public API surface and versioning guarantees. Note any AI providers, external APIs, or complex integrations. Document the concurrency/threading model (goroutines, asyncio, Node.js event loop). List all environment variables from `.env.example`. Include exact local development commands. Document invariants and safety rules found in the codebase.

### 2. `.agent/STYLE.md`
- **Goal**: Enforce visual identity and structural code patterns.
- **Instructions**: Extract the exact design system rules. Define primary colors, surface hierarchy, and spacing tokens. Document concrete component patterns (show exact CSS classes or Tailwind utilities). Define naming conventions (file naming, variable casing, Go export rules, package naming). Define import ordering rules (goimports standard for Go, ESLint for TS). Document docstring/comment standards (godoc, JSDoc, Google-style).
- **CRITICAL**: Formulate explicit "Anti-Patterns (FORBIDDEN)" based on what the codebase avoids (e.g., "NEVER use `useEffect` for data fetching", "NEVER use `border-gray-200` for sectioning", "NEVER write temp files to disk", "NEVER use `Any`/`interface{}` types", "NEVER write raw SQL outside sqlc queries").

### 3. `.agent/TESTING.md`
- **Goal**: Track test methods, execution evidence, and local dev setup.
- **Instructions**: Document the exact steps to get the app running locally (prerequisites, install, start, seed, database, code generation). Document the exact CLI commands to run tests, type checking, and linting (including `go test -race`, `golangci-lint`, `shellcheck` where applicable). Keep the "Execution Evidence Rules" from the template intact. Set up the empty scenario tables ready for the first feature. Initialize the empty Regression Scenarios table.

### 4. `.agent/PHILOSOPHY.md`
- **Goal**: The soul of the product.
- **Instructions**: Read the project's `README.md` and any existing context files. Infer the core pain point the project solves. Define the target user persona. Synthesize 3-5 core beliefs that drive technical and product decisions. Document design/UX principles (applies to CLI, web, SDK, and headless projects). Define explicit anti-goals (What This Is NOT). *If the product purpose is completely ambiguous, stop and ask the user for a 1-paragraph description before writing this file.*

### 5. `.agent/STATUS.md`
- **Goal**: The single source of truth for progress.
- **Instructions**: Initialize the tracking state. Set "Current Focus" to "Project Bootstrapped". Leave the lifecycle checkboxes unchecked. Leave "Relevant Files" empty. Leave "Review Results" empty. Set "Active Worktrees" to "(none — sequential execution)".

---

## Phase 2.5: Handling Non-Standard Project Types

Some projects don't fit the traditional "application" mold. Adapt the templates as follows:

### Shell Script Repos (e.g., a single Bash utility)
- **ARCHITECTURE.md**: Document the script's execution phases, safety mechanisms (lockfiles, duration checks, dry-run), CLI flags, and external tool dependencies (ffmpeg, ffprobe, Docker).
- **STYLE.md**: Cover shell conventions (`set -euo pipefail`, quoting rules, function naming as `snake_case`, config variables as `UPPER_SNAKE_CASE`, `shellcheck` compliance).
- **TESTING.md**: Document `shellcheck` linting and manual dry-run testing procedures. Most scenarios are manual.
- **PHILOSOPHY.md**: Focus on the tool's purpose and safety guarantees.
- **STATUS.md**: Standard — track features and improvements like any project.

### Docker Compose / Infrastructure Repos (e.g., NAS stack definitions)
- **ARCHITECTURE.md**: Document the stack topology (service map, port allocations, network bridges), data flow between services, volume mounts, and security boundaries. This IS the architecture.
- **STYLE.md**: Cover YAML formatting conventions, service naming, volume path standards, label conventions. Visual sections are "N/A".
- **TESTING.md**: Document `docker compose config --quiet` for YAML validation, `docker compose up -d` for smoke testing, and Uptime Kuma / health checks.
- **PHILOSOPHY.md**: Focus on infrastructure goals (self-hosted, zero-trust, data sovereignty).
- **STATUS.md**: Standard — track stack additions, service upgrades, security hardening.

### Documentation-Only Repos (e.g., Proxmox setup guides, runbooks)
- Most technical sections are "N/A — Documentation repository, no application code".
- **PHILOSOPHY.md**: Define the documentation's audience and purpose.
- **STATUS.md**: Track documentation coverage and accuracy.
- **STYLE.md**: Cover Markdown formatting conventions, heading hierarchy, link standards.

### SDK / Library Repos (e.g., Go API client wrappers)
- **ARCHITECTURE.md**: The "API Contracts" section documents the exported public API surface (types, functions, interfaces). Include versioning strategy and backward compatibility guarantees.
- **STYLE.md**: Heavy focus on naming conventions, godoc standards, and API design consistency.
- **TESTING.md**: Focus on `go test -race ./...`, example tests, and coverage thresholds.
- **PHILOSOPHY.md**: Focus on API ergonomics, zero-dependency philosophy, and consumer-friendliness.

---

## Phase 3: Docs Scaffolding Verification

Ensure the following directory structure exists in the project root to support the roles/phases workflow. Create them with `.gitkeep` files if they are missing:
- `docs/explorations/.gitkeep`
- `docs/designs/.gitkeep`
- `docs/plans/.gitkeep`
- `docs/archive/.gitkeep`

If you moved pre-existing docs to `docs/archive/pre-gemstack/` in Phase 0.5, ensure that directory exists and the files were moved correctly.

---

## Execution Rules for the LLM
- **No Hallucinations**: If a project does not have a database, simply write "N/A — No database utilized" in the database section. Do not invent details.
- **Extreme Specificity**: Do not write generic statements like "Uses Tailwind for styling." Write "Uses Tailwind CSS v4 with a strict tokenized surface hierarchy (`bg-surface`, `bg-surface-container`). 1px borders are FORBIDDEN for sectioning."
- **Absorb Legacy Rules**: If `.cursorrules`, `GEMINI.md`, or similar files exist, their rules MUST be reflected in the appropriate `.agent/` file. Do not ignore them.
- **Clean Up After Absorbing**: After absorbing existing `.agent/` files (Phase 0.5), delete the old files. The new standardized files replace them entirely.
- **Do not delete template sections**: If a section from the template is not applicable, keep the header and write "N/A — [Reason]".
- **Respect auto-generated content**: Do NOT move or modify auto-generated files in `docs/` (Swagger, godoc, images). Only move human-written documentation to the archive.
- **Completion**: Once all 5 files are successfully overwritten, the `docs/` folders are verified, and any pre-existing content is properly archived, inform the user that the project is bootstrapped and ready for the `/ideate` phase.