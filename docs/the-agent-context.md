# The `.agent/` Context System

The `.agent/` directory is the **single source of truth** that gives every AI agent — regardless of vendor — deterministic, project-specific context before it modifies your code. Instead of re-explaining your project in every conversation, you define it once and Gemstack ensures it's always injected.

---

## The 5 Context Files

Every Gemstack project stores its essential instructions in 5 structured markdown files inside `.agent/`. Each file has a specific purpose and truncation priority (used when context windows are limited):

| File | Purpose | Truncation Priority |
|------|---------|-------------------|
| **`ARCHITECTURE.md`** | The complete technical specification of your project | High (kept long) |
| **`STYLE.md`** | Coding conventions, design tokens, and forbidden anti-patterns | Medium |
| **`TESTING.md`** | Test strategy, commands, scenario tables, and coverage matrices | Medium |
| **`PHILOSOPHY.md`** | Product soul — core beliefs, anti-goals, and decision principles | Medium |
| **`STATUS.md`** | Current lifecycle state, active feature, and blocking issues | **Never truncated** |

### `ARCHITECTURE.md` — The Technical Anchor

This is the most important file. It acts as the definitive reference for your system's design, technology choices, and boundaries. It contains:

- **Project Topology** — Declares `[backend]`, `[frontend, backend]`, `[ml-ai]`, etc., which triggers topology-specific guardrails
- **Tech Stack & Infrastructure** — Exact technology choices with pinned major versions and rationale
- **System Boundaries & Data Flow** — How requests traverse your stack; concurrency and threading models
- **Data Models & Database Schema** — Core entities, relationships, migration processes, and critical rules (e.g., "never hard-delete users")
- **API Contracts** — The source of truth for communication between services (HTTP endpoints, request/response shapes, error formats)
- **External Integrations / AI** — Third-party services, LLM integrations, caching strategies, and the Model Ledger (for ML/AI topologies)
- **Invariants & Safety Rules** — Load-bearing constraints that must never be violated (e.g., "never expose API keys in client components")
- **Error Handling Patterns** — How the system handles and reports errors at each layer
- **Directory Structure** — Purpose of every key directory
- **Local Development** — Exact copy-paste commands (install, build, dev server, seed, database setup)
- **Environment Variables** — Full inventory synced with `.env.example`

Gemstack ships with a comprehensive **template** for each of these sections, pre-filled with rich examples for Node.js, Python, Go, Rust, infrastructure, and bash projects. When you run `gemstack init --ai`, the Gemini API replaces these templates with real, concrete details from your codebase.

### `STYLE.md` — Coding Conventions

Defines **how** code should be written in this project. Includes:

- Naming conventions (files, variables, functions, components)
- File organization patterns (barrel exports, co-location, separation)
- Design system tokens (colors, spacing, typography — for frontend projects)
- **FORBIDDEN** anti-patterns — explicitly banned patterns that agents must avoid
- Framework-specific idioms (e.g., "always use React Server Components, never use `useEffect` for data fetching")

### `TESTING.md` — Test Strategy

Specifies **what** and **how** to test. Topology-aware content includes:

- **Test commands** — Exact commands per topology (e.g., `uv run pytest`, `npm test`, `go test -race ./...`)
- **Scenario tables** — Feature-by-feature test requirements
- **Coverage matrices** — Vary by topology:
  - **Backend**: Route coverage matrix (every API endpoint → tested/untested)
  - **Frontend**: Component state matrix (each component × empty/loading/success/error/partial)
  - **ML/AI**: Evaluation threshold matrix (model × metric × minimum threshold)
- **Bug regression list** — Known bugs with their test coverage status

### `PHILOSOPHY.md` — Product Soul

Captures the **why** behind decisions. This anchors the AI's judgment on ambiguous tradeoffs:

- Product soul (one-sentence vision)
- Core user beliefs and anti-goals
- Decision principles for resolving conflicts
- Tone and communication style

### `STATUS.md` — Live State Tracker

The only file that changes frequently. It tracks:

- **`[STATE: ...]`** — Current lifecycle state (`INITIALIZED`, `IN_PROGRESS`, `READY_FOR_BUILD`, `READY_FOR_AUDIT`, `READY_FOR_SHIP`, `SHIPPED`, `BLOCKED`)
- **Active feature** — What feature is currently being worked on
- **Lifecycle checkboxes** — `[x] Spec  [ ] Trap  [ ] Build  [ ] Audit  [ ] Ship`
- **Relevant files** — Source files the AI should focus on (these get included in the compiled context)
- **Blocking issues** — Problems that require human intervention
- **Active worktrees** — Parallel development branches (populated by `gemstack worktree`)
- **Stub Audit Tracker** — Tracks placeholder/todo items across the codebase
- **Prompt Versioning Changelog** — History of prompt template changes (ML/AI topology)

The **deterministic phase router** (`gemstack route`) reads `STATUS.md` to calculate the next step. Because `STATUS.md` is never truncated during context compilation, the router always has full state visibility.

---

## Context Compilation

During execution, Gemstack's **Context Compiler** performs JIT (Just-In-Time) prompt assembly — dynamically stitching together exactly the right combination of project context, role definitions, phase instructions, and topology guardrails for a given workflow step.

### What Gets Compiled

For a command like `gemstack compile step3-build`, the compiler assembles:

1. **Workflow Goal** — The step's description and objectives
2. **Role Definitions** — Expert personas required by the step (e.g., `Principal Backend Engineer`, `Principal Frontend Engineer` for the Build step)
3. **Phase Instructions** — Behavioral rules for the active phase (e.g., the `build` phase enforces "loop until Exit Code 0" discipline)
4. **Topology Guardrails** — Domain-specific constraints loaded from your topology declaration (e.g., the `backend` topology injects anti-mocking rules and deterministic test discipline)
5. **`.agent/` Context** — Your project's `ARCHITECTURE.md`, `STYLE.md`, `TESTING.md`, and `STATUS.md`
6. **Relevant Source Files** — Actual source code referenced in `STATUS.md`'s "Relevant Files" section
7. **Plugin-injected sections** — Any sections added by third-party plugins via `gemstack_pre_compile` / `gemstack_post_compile` hooks
8. **Workflow Protocol** — Full routing and yield protocol for the step

### Viewing Compiled Output

```bash
# View the full compiled prompt for any step
gemstack compile step1-spec
gemstack compile step3-build
gemstack compile step4-audit

# With a token budget (truncates lowest-priority sections first)
gemstack compile step3-build --token-budget 100000
```

### Truncation Priorities

When you specify a token budget that the full context exceeds, the compiler truncates sections in this order (removing lowest-priority first):

| Priority | Section | Behavior |
|----------|---------|----------|
| 1 (never removed) | Workflow Goal | Always included |
| 2 | Role Definitions | Removed last — the AI needs its persona |
| 3 | Phase Instructions | Behavioral rules for the current phase |
| 4 | `.agent/` Files | Your project context |
| 5 | Topology Guardrails | Domain-specific constraints |
| 6 | Workflow Protocol / Source Files | Removed first if space is tight |

This means your most critical context — the workflow goal, the AI's expert persona, and your project architecture — is always preserved, even in small context windows.

---

## Drift Detection

Over time, your codebase may drift from what's documented in `.agent/`. Gemstack's **Context Differ** catches this:

```bash
gemstack diff
```

This analyzes three categories of drift:

1. **Dependency drift** — New packages added to `package.json` / `pyproject.toml` / `go.mod` that aren't documented in `ARCHITECTURE.md`, or documented packages that have been removed
2. **Environment variable drift** — Variables in `.env.example` that aren't documented in `ARCHITECTURE.md`, or documented variables that no longer exist
3. **Stale file references** — Files listed in `STATUS.md` under "Relevant Files" that no longer exist on disk

The drift report is also available as an MCP tool (`gemstack_diff`), so your IDE agent can proactively detect drift during its work.

---

## Best Practices

1. **Keep `STATUS.md` current** — Update the `[STATE: ...]` tag and lifecycle checkboxes as you progress. The phase router depends on accurate state.
2. **Update `ARCHITECTURE.md` during reviews** — Whenever you add a new API route, change a database schema, or introduce a new dependency, reflect it in the architecture doc.
3. **Use `gemstack check` regularly** — Validates that your `.agent/` directory is well-formed and all required files exist.
4. **Run `gemstack diff` before starting new features** — Catch drift early before it compounds.
5. **Populate "Relevant Files" in `STATUS.md`** — This is how the compiler knows which source files to include in the context. Be specific — list only the files relevant to your current feature.
