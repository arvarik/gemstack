# Getting Started with Gemstack

This guide covers everything you need to go from zero to running your first AI-orchestrated workflow step.

## Prerequisites

- **Python 3.10+** (verify with `python3 --version`)
- **Git** (required for worktree features and version tracking)
- **An existing codebase** — Gemstack wraps around your project; it doesn't generate greenfield apps

For autonomous execution features (`gemstack run`), you also need:
- A **Google Gemini API key** — get one free at [aistudio.google.com](https://aistudio.google.com)

---

## Installation Methods

Gemstack is primarily a CLI tool, so an isolated global install is recommended over project-local `pip install`.

### pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) installs Gemstack in its own isolated environment while making the `gemstack` command available globally:

```bash
# Minimal install (context compiler, CLI, drift detection)
pipx install gemstack

# With AI bootstrapping (gemini-powered `init --ai` and `run`)
pipx install 'gemstack[ai]'

# With MCP server support (Cursor, Claude Desktop, Cline integration)
pipx install 'gemstack[mcp]'

# Everything — AI, MCP, TUI dashboard, plugins
pipx install 'gemstack[all]'
```

### uv (Fastest)

If you use [uv](https://docs.astral.sh/uv/), it provides the fastest install experience:

```bash
uv tool install gemstack
uv tool install 'gemstack[ai,mcp]'
uv tool install 'gemstack[all]'
```

### Standard pip

If you prefer to install directly (e.g., in a virtual environment):

```bash
pip install gemstack
pip install "gemstack[all]"
```

### Available Extras

| Extra | What It Adds | When You Need It |
|-------|-------------|-----------------|
| `ai` | `google-genai` SDK | `gemstack init --ai`, `gemstack run` |
| `mcp` | `mcp` SDK (FastMCP) | `gemstack mcp serve`, IDE integration |
| `tail` | `textual` + `watchdog` | `gemstack tail` live TUI dashboard |
| `plugins` | `pluggy` | Third-party plugin development |
| `all` | Everything above | Full experience |

---

## Verifying Your Installation

After installing, verify everything is working:

```bash
gemstack --version       # Print the installed version
gemstack doctor          # Run environment diagnostics
```

The `doctor` command checks for:
- Python version compatibility
- Git availability
- Gemini API key configuration
- Optional dependency availability (MCP, AI, plugins)
- Common misconfigurations

---

## Initializing a Project

Navigate to the root of your existing codebase and run:

```bash
cd your-project/
gemstack init
```

This performs the following operations:

1. **Project Detection** — Scans your filesystem to detect:
   - Language and runtime (TypeScript/Node.js, Python, Go, Rust)
   - Framework (Next.js, FastAPI, Django, Vite, chi, etc.)
   - Package manager (npm, pnpm, yarn, bun, pip, uv, poetry, cargo, go mod)
   - Topologies (backend, frontend, ml-ai, infrastructure, library-sdk)
   - Existing test infrastructure, CI configuration, and database usage
   - Legacy context files (`.cursorrules`, `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`)

2. **`.agent/` Directory Creation** — Generates 5 structured markdown files populated with detected project details:
   - `ARCHITECTURE.md` — Tech stack, data models, API contracts, system boundaries
   - `STYLE.md` — Coding conventions, design tokens, forbidden anti-patterns
   - `TESTING.md` — Test strategy, coverage matrices, scenario tables
   - `PHILOSOPHY.md` — Product soul, core beliefs, anti-goals
   - `STATUS.md` — Current lifecycle state, active feature, blocking issues

3. **`docs/` Lifecycle Directories** — Creates empty directories for feature lifecycle artifacts:
   - `docs/explorations/` — Discovery and research documents
   - `docs/designs/` — UX specs and technical designs
   - `docs/plans/` — Task plans and implementation checklists
   - `docs/archive/` — Completed feature summaries

### AI-Powered Initialization

If you installed with the `ai` extra, upgrade your initialization with deep Gemini analysis:

```bash
gemstack init --ai
```

This sends your key source files to the Gemini API, which returns accurately populated `.agent/` files filled with **real, concrete details** about your project — actual API routes, actual database schemas, actual test commands — rather than placeholder templates you'd have to manually fill in.

You can also provide an explicit topology override:

```bash
gemstack init --topology "frontend,backend,ml-ai"
```

Or absorb existing legacy context files into the `.agent/` structure:

```bash
gemstack init --from-legacy
```

---

## Your First Workflow

After initialization, explore the full lifecycle:

```bash
# 1. Check project status — see the current lifecycle state
gemstack status

# 2. Get routing guidance — what should you do next?
gemstack route

# 3. Validate the setup — ensure .agent/ is well-formed
gemstack check

# 4. Start a new feature lifecycle
gemstack start "Add user search"

# 5. View the compiled context for Step 1
gemstack compile step1-spec

# 6. Execute Step 1 autonomously via Gemini
gemstack run step1-spec --feature "Add user search"

# 7. Detect drift between .agent/ docs and your actual codebase
gemstack diff
```

### Understanding `gemstack route`

The `route` command reads your `STATUS.md` (which tracks `[STATE: ...]`) and any existing audit findings to deterministically tell you what to do next. It never guesses — it evaluates a fixed decision tree:

- `INITIALIZED` → Start with Step 1: Spec
- `IN_PROGRESS` → Continue with the current uncompleted step
- `READY_FOR_BUILD` → Proceed to Step 3: Build
- `READY_FOR_AUDIT` → Proceed to Step 4: Audit
- `READY_FOR_SHIP` → Proceed to Step 5: Ship
- `SHIPPED` → Start a new feature with `gemstack start`
- Audit findings exist → Reroute to Build to fix issues

This is the **deterministic phase router** — it ensures you never skip a step or lose track of where you are in the lifecycle.

---

## Configuring AI Access

To use `gemstack run` (autonomous execution), configure your Gemini API key:

```bash
# Option 1: Via gemstack config
gemstack config set gemini-api-key YOUR_GEMINI_API_KEY
gemstack config set default-model gemini-2.5-flash  # Default: gemini-3.1-pro-preview

# Option 2: Via environment variable
export GEMINI_API_KEY=YOUR_GEMINI_API_KEY

# Verify your configuration
gemstack config list    # Keys are masked for security
```

---

## Next Steps

- 📖 Learn how the [`.agent/` Context System](the-agent-context.md) drives all AI behavior
- 🔄 Understand the [5-Step Lifecycle](the-5-step-lifecycle.md) in depth
- 📐 Explore [Topology-Aware Guardrails](topologies.md) for your project type
- 🔌 Connect your IDE via the [MCP Server](mcp-server.md)
- 🔧 Browse the [Full CLI Reference](cli-reference.md) for all 28 commands
