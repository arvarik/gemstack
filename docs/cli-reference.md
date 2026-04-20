# CLI Reference

Gemstack ships with **28 commands** organized across 7 functional categories. Every command supports `--help` for full documentation. This reference provides an overview of each command's purpose, key flags, and usage examples.

---

## Setup Commands

Commands for project initialization, CLI registration, and environment validation.

### `gemstack init`

Initialize a Gemstack project by creating the `.agent/` directory with project-specific context files.

```bash
gemstack init                              # Template-only (auto-detects stack)
gemstack init --ai                         # AI-powered deep analysis via Gemini
gemstack init --topology "frontend,backend" # Explicit topology override
gemstack init --from-legacy                # Absorb .cursorrules, GEMINI.md, etc.
gemstack init --no-ai                      # Force template-only mode
```

**What it does:**
1. Scans your project to detect language, framework, package manager, topology, tests, CI, and database usage
2. Generates 5 `.agent/*.md` files (ARCHITECTURE, STYLE, TESTING, PHILOSOPHY, STATUS)
3. Creates `docs/explorations/`, `docs/designs/`, `docs/plans/`, `docs/archive/` directories
4. Fires the `gemstack_post_init` plugin hook

### `gemstack install`

Symlink Gemstack's workflow, role, and phase files into your system's global agent workflow directory (e.g., `~/.gemini/antigravity/global_workflows/`).

```bash
gemstack install
```

After installation, you can invoke Gemstack workflows as slash commands (`/architect`, `/sdet`, `/step1-spec`, etc.) directly in Gemini CLI, Antigravity, and other compatible tools.

### `gemstack uninstall`

Remove all Gemstack symlinks from the global workflow directory.

```bash
gemstack uninstall
```

### `gemstack doctor`

Run environment diagnostics to verify your setup is correct.

```bash
gemstack doctor
```

Checks: Python version, Git availability, API key configuration, optional dependencies (MCP, AI, plugins), and common misconfigurations.

### `gemstack config`

Manage global Gemstack configuration (stored in `~/.config/gemstack/config.toml`).

```bash
gemstack config set api-key YOUR_GEMINI_API_KEY
gemstack config set model gemini-2.5-pro      # Default: gemini-2.5-flash
gemstack config show                          # View settings (keys masked)
```

---

## Workflow Commands

Commands for lifecycle management and autonomous execution.

### `gemstack status`

Display the current project status — lifecycle state, active feature, completion checkboxes, and blocking issues.

```bash
gemstack status
```

Reads `STATUS.md` and presents a formatted summary including the current `[STATE:]` value, which lifecycle steps have been completed, and any active worktrees.

### `gemstack route`

Get the deterministic next-action recommendation based on current project state.

```bash
gemstack route
```

Evaluates `STATUS.md` and `AUDIT_FINDINGS.md` to output the exact command you should run next. See [The 5-Step Lifecycle](the-5-step-lifecycle.md#using-gemstack-route) for the full routing decision tree.

### `gemstack start`

Initialize a new feature lifecycle — sets the active feature in `STATUS.md` and transitions to `[STATE: IN_PROGRESS]`.

```bash
gemstack start "Add user search"
gemstack start "OAuth2 authentication"
```

### `gemstack phase`

View or set the current phase explicitly.

```bash
gemstack phase              # Show current phase
gemstack phase build        # Set phase to build
```

### `gemstack run`

**The autonomous executor.** Compiles context, calls Gemini, writes results to disk, and tracks costs — all in one command.

```bash
gemstack run step1-spec --feature "Add user search"
gemstack run step3-build --feature "Add user search"
gemstack run step4-audit --feature "Add user search"
gemstack run step5-ship --feature "Add user search"

# Dry run — compile context without making an API call
gemstack run step1-spec --feature "..." --dry-run

# Cost controls
gemstack run step3-build --feature "..." --max-cost 5.00      # USD limit per feature
gemstack run step3-build --feature "..." --max-tokens 500000  # Token limit per step
```

**Execution pipeline:**
1. Validate step transition via the phase router
2. Compile context via the Context Compiler
3. Check cost budget (if limits configured)
4. Fire `gemstack_pre_run` plugin hook
5. Call Gemini API via `asyncio.to_thread()`
6. Parse structured response into file operations
7. Write results via atomic file writes (with path traversal prevention)
8. Record costs to `.agent/costs.json`
9. Fire `gemstack_post_run` plugin hook
10. Return execution summary with cost, duration, and next-step guidance

**Safety features:** Per-project lockfile prevents concurrent executions. All AI-generated file paths are validated against the project root to prevent path traversal. Cost circuit breaker halts execution when limits are exceeded.

---

## Context Commands

Commands for prompt compilation, drift detection, and format exports.

### `gemstack compile`

View the full compiled context prompt for any workflow step.

```bash
gemstack compile step1-spec
gemstack compile step3-build
gemstack compile step3-build --token-budget 100000  # With token limit
```

Outputs the complete JIT-assembled prompt including role definitions, phase instructions, topology guardrails, `.agent/` context, and relevant source files.

### `gemstack diff`

Detect drift between `.agent/` documentation and actual codebase state.

```bash
gemstack diff
```

Checks 3 categories: dependency drift (new/removed packages vs. `ARCHITECTURE.md`), environment variable drift (`.env.example` vs. `ARCHITECTURE.md`), and stale file references (files in `STATUS.md` that no longer exist).

### `gemstack export`

Export your `.agent/` context in different formats.

```bash
gemstack export               # Export as markdown
gemstack export --format json  # Export as JSON
```

### `gemstack snapshot`

Create a point-in-time snapshot of your `.agent/` directory.

```bash
gemstack snapshot              # Create snapshot
gemstack snapshot --list       # List existing snapshots
gemstack snapshot --restore    # Restore from snapshot
```

### `gemstack migrate`

Migrate an older Gemstack project to use topologies.

```bash
gemstack migrate
```

Detects topologies, adds the declaration to `ARCHITECTURE.md`, and inserts topology-specific matrices into `TESTING.md` and `STATUS.md`.

---

## Analysis Commands

Commands for validation, benchmarking, and cross-project analysis.

### `gemstack check`

Validate the `.agent/` directory integrity.

```bash
gemstack check
```

Verifies: all required files exist, `STATUS.md` has a valid `[STATE:]` tag, topology is declared in `ARCHITECTURE.md`, and custom plugin checks pass.

### `gemstack compare`

Benchmark or compare context across projects.

```bash
gemstack compare              # Compare current project against baseline
gemstack compare --project-b /path/to/other  # Compare two projects
```

### `gemstack replay`

Replay a past execution for retrospective analysis.

```bash
gemstack replay              # Replay the last execution
gemstack replay --step step3-build  # Replay a specific step
```

### `gemstack matrix`

Cross-project dashboard — view the status of all Gemstack projects.

```bash
gemstack matrix
```

Scans for Gemstack projects and displays their lifecycle state, topology, and last activity.

---

## Tooling Commands

Commands for MCP server, git hooks, parallel development, CI generation, and scaffolding.

### `gemstack mcp`

Run and register the MCP server. See [MCP Server & IDE Integration](mcp-server.md) for full details.

```bash
gemstack mcp serve                           # Start stdio server
gemstack mcp serve --transport sse --port 8765  # Start SSE server
gemstack mcp register --cursor               # Register with Cursor
gemstack mcp register --claude-desktop       # Register with Claude Desktop
gemstack mcp register --gemini-cli           # Register with Gemini CLI
gemstack mcp register --cline                # Register with Cline
```

### `gemstack hook`

Manage git hooks for automated context checking.

```bash
gemstack hook install    # Install pre-commit hooks
gemstack hook remove     # Remove hooks
```

### `gemstack worktree`

Manage git worktrees for **parallel agent execution** — run frontend and backend builds simultaneously in separate worktrees.

```bash
gemstack worktree create --backend feat/oauth-api --frontend feat/oauth-ui
gemstack worktree status    # List active worktrees
gemstack worktree merge     # Merge all worktree branches
gemstack worktree cleanup   # Remove all non-main worktrees
```

The worktree manager integrates with `STATUS.md` to track active worktrees and supports parallel execution via `asyncio.TaskGroup` (Python 3.11+) with sequential fallback on 3.10.

### `gemstack ci`

Generate CI pipeline configuration.

```bash
gemstack ci generate          # Generate GitHub Actions workflow
gemstack ci generate --gitlab # Generate GitLab CI
```

### `gemstack scaffold`

Generate project scaffolding and boilerplate.

```bash
gemstack scaffold component MyButton    # Scaffold a component
gemstack scaffold api /api/v1/users     # Scaffold an API route
gemstack scaffold test MyButton         # Scaffold tests
```

---

## ML/AI Commands

Commands specific to ML/AI topology projects.

### `gemstack prompt`

Manage prompt template versioning.

```bash
gemstack prompt list             # List all versioned prompts
gemstack prompt show my-prompt   # Show a specific prompt
gemstack prompt diff v1 v2       # Diff between versions
```

### `gemstack eval`

Run evaluation suites against a holdout dataset.

```bash
gemstack eval run my-eval        # Run an evaluation suite
gemstack eval results            # Show evaluation results
```

---

## DX Commands

Developer experience commands.

### `gemstack tail`

Live TUI dashboard powered by [Textual](https://textual.textualize.io/) — watch your project's lifecycle state, costs, and execution logs in real-time.

```bash
gemstack tail
```

Requires the `tail` extra: `pipx install 'gemstack[tail]'`

### `gemstack teach`

Interactive tutorial that walks you through Gemstack's concepts and commands.

```bash
gemstack teach
```

---

## Global Flags

These flags are available on every command:

| Flag | Description |
|------|-------------|
| `--verbose` / `-v` | Enable verbose output |
| `--debug` | Enable debug logging (most detailed) |
| `--version` / `-V` | Show version and exit |
| `--help` | Show help for any command |
