# The Context Compiler

The Context Compiler is the engine that makes Gemstack work. It performs **JIT (Just-In-Time) prompt assembly** — dynamically stitching together exactly the right combination of project context, role definitions, phase instructions, and topology guardrails for any workflow step.

---

## How It Works

When you run `gemstack compile step3-build` (or when `gemstack run` calls it internally), the compiler executes 8 stages in sequence:

```text
┌─────────────────────────────────────────────────────────┐
│                   CONTEXT COMPILER                       │
│                                                          │
│  1. Parse Workflow    →  Extract required roles/phases   │
│  2. Load Roles        →  Bundle expert personas          │
│  3. Load Phases       →  Attach behavioral rules         │
│  4. Load Guardrails   →  Inject topology constraints     │
│  5. Compile .agent/   →  Read project context files      │
│  6. Include Sources   →  Pull in referenced source code  │
│  7. Fire Hooks        →  Let plugins modify sections     │
│  8. Apply Budget      →  Truncate if over token limit    │
│                                                          │
│  Output: A single, self-contained prompt string          │
└─────────────────────────────────────────────────────────┘
```


---

## The 8 Compilation Stages

### Stage 1: Parse Workflow

The compiler reads the workflow definition file (e.g., `step3-build.md`) and extracts:
- **Required roles** — Which expert personas the step needs (e.g., `Principal Backend Engineer`, `Principal Frontend Engineer`)
- **Required phases** — Which behavioral phase rules apply (e.g., `build`)
- **Workflow goal** — The step's purpose and acceptance criteria

### Stage 2: Load Role Definitions

Each role is a markdown file containing an expert persona definition. For `step3-build`, the compiler loads:
- `principal-backend-engineer.md` — Server-side implementation expertise
- `principal-frontend-engineer.md` — Client-side implementation expertise

Roles define the AI's professional identity, responsibilities, decision-making principles, and behavioral boundaries.

### Stage 3: Load Phase Instructions

Phase instructions are behavioral rules for the current phase. The `build` phase enforces:
- "Loop until Exit Code 0" — run tests in the terminal, fix errors, repeat
- Static analysis first — run the type-checker before the test suite
- No shortcuts — never hardcode values or mutate tests
- Bounded Reflexion — maximum 3 attempts before circuit breaker

### Stage 4: Apply Topology Guardrails

The compiler reads your topology declaration from `ARCHITECTURE.md`:

```markdown
**Topology:** [frontend, backend]
```

And loads the corresponding guardrail documents. For `[frontend, backend]`, it injects:
- `backend.md` — Data integrity, anti-mocking discipline, N+1 prevention, deterministic testing
- `frontend.md` — Component state matrix, hydration safety, accessibility, no raw fetch loops

Multiple topologies are combined additively — all guardrails from all declared topologies apply simultaneously.

### Stage 5: Compile `.agent/` Context

Your project's 5 context files are read and included:
- `ARCHITECTURE.md` — Tech stack, data models, API contracts
- `STYLE.md` — Coding conventions, forbidden anti-patterns
- `TESTING.md` — Test strategy, commands, coverage matrices
- `PHILOSOPHY.md` — Product soul, core beliefs
- `STATUS.md` — Current lifecycle state, active feature, relevant files

### Stage 6: Include Source Files

Files listed in `STATUS.md` under "Relevant Files" are read from disk and included as raw source code. This gives the AI direct visibility into the files it needs to modify:

```markdown
<!-- In STATUS.md -->
## Relevant Files
- src/api/routes/users.ts
- src/components/UserSearch.tsx
- tests/api/users.test.ts
```

These files are included verbatim in the compiled prompt.

### Stage 7: Fire Plugin Hooks

Two plugin hooks fire during compilation:

1. **`gemstack_pre_compile(step, sections)`** — Plugins can add, remove, or reorder sections before assembly
2. **`gemstack_post_compile(step, compiled)`** — Plugins can modify the final compiled string

See [Building Custom Plugins](plugins.md) for hook implementation details.

### Stage 8: Apply Token Budget

If you specified a `--token-budget`, the compiler truncates sections by priority (removing lowest-priority first):

| Priority | Section | Behavior |
|----------|---------|----------|
| 1 (never removed) | Workflow Goal | Always included |
| 2 | Role Definitions | Removed last — the AI needs its persona |
| 3 | Phase Instructions | Behavioral rules for the current phase |
| 4 | `.agent/` Files | Your project context |
| 5 | Topology Guardrails | Domain-specific constraints |
| 6 | Workflow Protocol / Source Files | Removed first if space is tight |

This ensures your most critical context — the workflow goal, the AI's expert persona, and your project architecture — is always preserved, even in small context windows.


---

## Viewing Compiled Output

### Full Output

```bash
# View the compiled prompt for any step
gemstack compile step1-spec
gemstack compile step3-build
gemstack compile step4-audit
```

The output is the complete prompt string that would be sent to the Gemini API.

### With Token Budget

```bash
# Compile with a tight budget — see what gets truncated
gemstack compile step3-build --token-budget 50000

# Compile with a generous budget
gemstack compile step3-build --token-budget 200000
```

### Export to File or Clipboard

```bash
# Save to a file
gemstack compile step3-build > /tmp/context.md

# Copy to clipboard (macOS)
gemstack compile step3-build | pbcopy

# Export as structured JSON
gemstack export --format json > context.json
```

---

## Understanding the Output

A compiled prompt has this general structure:

```text
═══════════════════════════════════════════
 WORKFLOW: Step 3 — Build
═══════════════════════════════════════════

## Goal
Implement the feature code and loop against the terminal
until every test passes with Exit Code 0.

═══════════════════════════════════════════
 ROLES
═══════════════════════════════════════════

### Principal Backend Engineer
[Full role definition...]

### Principal Frontend Engineer
[Full role definition...]

═══════════════════════════════════════════
 PHASE: Build
═══════════════════════════════════════════

[Build phase behavioral rules...]

═══════════════════════════════════════════
 TOPOLOGY GUARDRAILS
═══════════════════════════════════════════

### Backend Guardrails
[Anti-mocking, data integrity, N+1 prevention...]

### Frontend Guardrails
[Component state matrix, hydration safety...]

═══════════════════════════════════════════
 PROJECT CONTEXT
═══════════════════════════════════════════

[ARCHITECTURE.md, STYLE.md, TESTING.md, STATUS.md content...]

═══════════════════════════════════════════
 RELEVANT SOURCE FILES
═══════════════════════════════════════════

[Raw source code of files listed in STATUS.md...]
```

---

## Practical Tips

1. **Populate "Relevant Files" in `STATUS.md`** — This is how the compiler knows which source files to include. Be specific — list only the files relevant to your current feature.

2. **Use `--token-budget` to control costs** — Larger contexts cost more but give the AI more information. Start with `100000` tokens and adjust.

3. **Check compilation before running** — Always `gemstack compile step3-build | head -20` before `gemstack run` to verify the context looks correct.

4. **Use plugins for company-wide standards** — If your organization has coding standards, inject them via `gemstack_pre_compile` so every developer gets them automatically.

---

## Next Steps

- 🤖 Learn how compiled context is used in [Autonomous Execution](autonomous-execution.md)
- 📐 Understand what guardrails are loaded in [Topology-Aware Guardrails](topologies.md)
- 🧩 Extend the compiler via [Building Custom Plugins](plugins.md)
