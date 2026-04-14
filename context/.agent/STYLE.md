# Style Guide & Code Conventions

_This document enforces the visual identity and coding patterns of the project. It prevents context drift as multiple agents work on the codebase. Agents MUST follow these rules strictly._

## 1. Visual Language & Tokens
_Define the core color palette, spacing, and typography rules. If this project has no frontend UI, write "N/A — CLI / backend-only project" and skip to Section 3._

### Colors
- **Primary Color**: `#XXXXXX` (Used for main CTAs)
- **Backgrounds**: e.g., Use `bg-surface` for base layers, `bg-surface-container` for elevated cards.
- **Borders**: e.g., "Lines are a failure of hierarchy. In this system, 1px solid borders are strictly prohibited for sectioning. Boundaries must be defined solely through background color shifts."
- **Off-Palette (FORBIDDEN)**: List any specific color tokens that agents must never use (e.g., `violet-*`, `indigo-*` — replaced by `primary` tokens).

### Typography
- **Font Families**: e.g., Manrope (headlines), Inter (body) — or Newsreader (editorial serif)
- **Scale**: e.g., `h1`: `text-6xl font-bold tracking-tighter`, `body`: `text-sm leading-relaxed`
- **Special Rules**: e.g., "ALL headings must use `text-balance`. ALL paragraphs must use `text-pretty`."

### Spacing & Layout
- **Border Radius**: e.g., `rounded-2xl` for cards — or `0px` for brutalist design
- **Grid System**: e.g., 12-column architectural grid, or standard flex-based layout
- **Responsive Breakpoints**: e.g., Mobile-first: 375px → 768px → 1440px

## 2. Component Patterns
_Specify how common UI elements should be built. If no frontend, write "N/A"._
- **Buttons**: e.g., `bg-primary text-on-primary font-bold rounded-xl px-5 py-2.5`
- **Cards**: e.g., `bg-surface-container shadow-sm rounded-2xl p-6`
- **Inputs**: e.g., Focus states must use `focus:ring-2 focus:ring-primary/30`.
- **Animations**: e.g., "Animate `transform` and `opacity` only. Use spring physics for interactive islands: `transition={{ type: 'spring', stiffness: 200, damping: 20 }}`"

## 3. Code Conventions
_Define how logic should be structured. These apply to all projects regardless of stack._

### Architecture Patterns
- Example (Web): "Server-First Execution: maximize React Server Components. The `'use client'` directive should only be used in isolated interactive components."
- Example (Web): "Always use React Query for client-side fetching. Never write raw `useEffect` fetch loops."
- Example (Backend): "Service layer pattern: routes are thin controllers. Business logic lives in `server/services/`."
- Example (Pipeline): "All blocking inference must be offloaded to `loop.run_in_executor()`. Never block the asyncio event loop."
- Example (Go): "Standard project layout: `cmd/` for entrypoints, `internal/` for private packages. Business logic lives in `internal/service/`. Handlers in `internal/handler/` are thin HTTP adapters."
- Example (Go): "Database access via sqlc-generated code ONLY. Never write raw SQL in handler or service code."
- Example (Bash): "Script follows a phased execution pattern: host bootstrap → self-re-invocation (Docker or native) → worker payload. Each phase is clearly delimited with header comments."

### State Management
- Example (Web): "Quarantine client state. `'use client'` components manage only local UI state. Server-side data is fetched via React Query."
- Example (Pipeline): "All state tracked via async SQLite. Update DB state immediately when work begins (EXTRACTING/INFERENCING), not when it ends."
- Example (Go): "Application state stored in PostgreSQL. In-memory state limited to caches with TTL. No global mutable singletons."

### Strict Typing
- Example (TypeScript): "The codebase maintains 0 TypeScript errors and 0 ESLint warnings. No `any` types. Use Zod for runtime validation."
- Example (Python): "All code MUST pass `mypy src/ tests/ --strict`. No `Any` types unless absolutely necessary."
- Example (Go): "All code MUST pass `golangci-lint run ./...` with zero warnings. Use custom error types (not raw `errors.New` in handlers). Emit JSON struct tags on all API response types."

## 4. Naming Conventions
_Define consistent naming patterns for files, variables, and exports._
- **Files**: e.g., `kebab-case.ts` for modules, `PascalCase.tsx` for React components — or `snake_case.py` for Python — or `snake_case.go` for Go files
- **Variables / Functions**: e.g., `camelCase` in TypeScript, `snake_case` in Python, `camelCase` (unexported) / `PascalCase` (exported) in Go (compiler-enforced)
- **Constants**: e.g., `UPPER_SNAKE_CASE` in TS/Python — or `PascalCase` in Go (idiomatic)
- **Database columns**: e.g., `camelCase` (Drizzle) or `snake_case` (sqlc / SQLAlchemy)
- **Exports**: e.g., "Named exports only. No default exports except for page components." / "Go exports are PascalCase by definition."
- **Packages**: e.g., "Go packages are lowercase, single-word. Never use underscores or camelCase in Go package names."
- **Bash functions**: e.g., `snake_case` for functions, `UPPER_SNAKE_CASE` for config variables.

## 5. Import Ordering
_Define the canonical import order for consistency across all files._
- Example (TypeScript):
  1. Node built-ins (`path`, `fs`)
  2. External packages (`react`, `@tanstack/react-query`)
  3. Internal aliases (`@/lib/`, `@/components/`)
  4. Relative imports (`./utils`, `../types`)
  5. Type-only imports last (`import type { ... }`)
- Example (Python):
  1. Standard library (`os`, `asyncio`, `pathlib`)
  2. Third-party (`pydantic`, `aiosqlite`, `faster_whisper`)
  3. Local modules (`from .extractor import AudioExtractor`)
- Example (Go — enforced by `goimports`):
  1. Standard library (`fmt`, `net/http`, `context`)
  2. Third-party (`github.com/go-chi/chi/v5`)
  3. Internal packages (`github.com/arvarik/project/internal/service`)

## 6. Documentation Standards
_How should code be documented?_
- **Docstrings**: e.g., "Use Google-style docstrings for all classes and public methods" — or "JSDoc for exported functions" — or "godoc-compatible comments on all exported types and functions (`// FunctionName does X.`)"
- **Comments**: e.g., "Comments explain *why*, not *what*. Self-documenting code is preferred."
- **Type Hints**: e.g., "All function signatures must include type annotations." / "Go is statically typed — leverage the type system instead of comments."
- **README**: e.g., "Keep README focused on setup and usage. Architecture details go in `.agent/ARCHITECTURE.md`."

## 7. Anti-Patterns (FORBIDDEN)
_Explicitly list approaches that agents should NEVER use. Be specific — cite the exact class, function, or pattern._
- ❌ NEVER use `overflow-hidden` on flex containers that have children with focus rings. (Use `ring-inset` instead)
- ❌ NEVER inline SVG icons directly in components; use the designated Icon component.
- ❌ NEVER hallucinate styles or invent generic Tailwind utility classes unless permitted by the visual system.
- ❌ NEVER disable ESLint, TypeScript, mypy, or golangci-lint checks.
- ❌ NEVER write `.wav` or temp files to disk (pipeline projects with zero-disk constraints).
- ❌ NEVER use `useEffect` for data fetching (React projects using React Query).
- ❌ NEVER expose API keys in client-side code.
- ❌ NEVER use `interface{}` / `any` in Go where a concrete type or generic constraint exists.
- ❌ NEVER write raw SQL in Go handler/service code — always go through sqlc-generated functions.
- ❌ NEVER store OAuth tokens in plaintext — always encrypt at rest with application-level AES-256-GCM.
- ❌ NEVER use global mutable singletons in Go — pass dependencies via constructor injection.
