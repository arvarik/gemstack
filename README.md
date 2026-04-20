# Gemstack

**Opinionated AI agent orchestration framework for [Gemini CLI](https://github.com/google-gemini/gemini-cli) and [Antigravity](https://github.com/google-gemini/antigravity).**

[![PyPI](https://img.shields.io/pypi/v/gemstack?style=flat-square&logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/gemstack/)
[![Python](https://img.shields.io/pypi/pyversions/gemstack?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/gemstack/)
[![CI](https://img.shields.io/github/actions/workflow/status/arvarik/gemstack/ci.yml?style=flat-square&logo=github&label=CI)](https://github.com/arvarik/gemstack/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/arvarik/gemstack?style=flat-square)](LICENSE)
[![Typed](https://img.shields.io/badge/typed-py.typed-blue?style=flat-square&logo=python&logoColor=white)](https://peps.python.org/pep-0561/)

> Gemstack gives your Gemini-powered agents architectural memory, topology-aware guardrails, and a 5-step lifecycle that forces them to *verify their own work* against your terminal — not just hallucinate a solution and tell you it's done.
>
> Built for **Gemini CLI** and **Google Antigravity**. Also works with Cursor, Claude Desktop, and Cline via [MCP](docs/mcp-server.md).

---

## The Problem

Every AI coding tool on the market today — Cursor, Copilot, Aider, Cline — is **bottom-up**. You highlight a file, say "write this function," and the agent does its best. Here's what goes wrong at scale:

- 🧠 **Architecture amnesia** — The agent forgets your tech stack, reinvents design patterns, and introduces conflicting libraries across sessions.
- 🔁 **Silent rewrites** — It overwrites perfectly good files to suit new logic, mutating critical path variables without testing.
- ✅ **Self-reported success** — It tells you "Done!" but never actually ran the test suite. You discover failures 3 commits later.
- 🎭 **One-size-fits-all prompting** — A React SPA and a Go microservice get the same generic instructions. No guardrails for your specific topology.

## The Solution

**Gemstack is top-down.** It acts as the orchestrator *above* your editor, purpose-built for **Gemini CLI** and **Google Antigravity** — Google's agentic AI coding platforms. Gemstack gives your Gemini agent the exact context, constraints, and verification loops it needs to produce production-quality code.

```
┌───────────────────────────────────────────────────────────────┐
│                          GEMSTACK                             │
│                                                               │
│   ┌──────────┐  ┌────────────┐  ┌─────────┐  ┌────────────┐   │
│   │ Context  │  │  Topology  │  │  Phase  │  │ Autonomous │   │
│   │ Compiler │─▶│ Guardrails │─▶│ Router  │─▶│  Executor  │   │
│   └────┬─────┘  └────────────┘  └─────────┘  └─────┬──────┘   │
│        │                                           │          │
│   .agent/ files                        Terminal verification  │
│   (ARCHITECTURE, STYLE,              (Exit Code 0 or retry)   │
│    TESTING, STATUS)                                           │
└───────────────────────────────────────────────────────────────┘
          ↕                  ↕                    ↕
     Gemini CLI         Antigravity      Cursor / Claude / Cline
      (native)           (native)          (via MCP Server)
```

Gemstack's workflows install as **slash commands** (`/architect`, `/step1-spec`, `/step3-build`, etc.) directly into Gemini CLI and Antigravity. When you type `/step3-build` in a new Antigravity conversation, the full compiled context — roles, phases, topology guardrails, and your project's `.agent/` files — is loaded automatically. For other AI IDEs, the built-in [MCP server](docs/mcp-server.md) provides the same capabilities.

---

## Key Features

### 🏛️ Architectural Memory via `.agent/` Files
Define your entire project context **once** — tech stack, API contracts, database schemas, coding style, test strategy, and anti-patterns — in 5 structured markdown files. Every AI agent reads these before touching your code. No more repeating yourself across sessions.

```bash
gemstack init --ai    # AI analyzes your codebase and auto-populates .agent/
```

### 🔄 The 5-Step Verified Lifecycle
Every feature flows through **Spec → Trap → Build → Audit → Ship**, with each step running in a **fresh context window**. The Auditor can't be influenced by the Builder's justifications. Tests are written before code. This is how you crush hallucination.

```
Step 1: Spec  → Define the feature, lock API contracts    (Product Visionary + Architect)
Step 2: Trap  → Write the failing test suite + task plan  (SDET + Planner)
Step 3: Build → Implement until Exit Code 0               (Principal Engineer)
Step 4: Audit → Fresh-eyes security & logic review        (Security Engineer)
Step 5: Ship  → Integrate, merge, deploy, archive         (DevOps Engineer)
```

### 📐 Topology-Aware Guardrails
Instead of generic prompts, Gemstack loads **domain-specific guardrails** based on your project's detected topology. A Next.js app with a Go backend gets different rules than a Python ML pipeline.

| Topology | Example Guardrails |
|----------|-------------------|
| **Backend** | Deterministic test discipline, anti-mocking rules, N+1 query detection |
| **Frontend** | Component state coverage matrix (empty/loading/success/error), hydration safety |
| **ML/AI** | Evaluation-Driven Development, cost circuit breakers, prompt versioning |
| **Infrastructure** | YAML validation, no-auto-apply policy, configuration drift detection |
| **Library/SDK** | API surface snapshot diffing, semver enforcement, backward compatibility |

### 🤖 Autonomous Execution with `gemstack run`
Go beyond copy-pasting prompts. Gemstack compiles your full project context, calls Gemini, writes the results to disk, and tracks costs — all in a single command:

```bash
gemstack run step1-spec --feature "Add user notifications"   # Define the spec
gemstack run step3-build --feature "Add user notifications"  # Build until tests pass
gemstack run step4-audit --feature "Add user notifications"  # Fresh-context audit
```

Each execution includes: **per-project lockfile** (prevents concurrent corruption), **cost tracking** with configurable circuit breakers, **path traversal prevention** on AI-generated file writes, and **structured result summaries**.

### 🔌 Native IDE Integration via MCP
Gemstack exposes your `.agent/` context to **any MCP-compatible agent** (Cursor, Claude Desktop, Gemini CLI, Cline) as a Model Context Protocol server — with read-only resources, actionable tools, and reusable prompt templates:

```bash
gemstack mcp serve                           # Start stdio server
gemstack mcp register --cursor --claude-desktop  # Auto-register with your IDEs
```

**Exposed MCP tools:** `gemstack_status`, `gemstack_route`, `gemstack_compile`, `gemstack_check`, `gemstack_diff`, `gemstack_run`, `gemstack_costs`

### 🧩 Extensible Plugin System
Add custom topologies, roles, validation checks, or intercept compilation events with the stable `pluggy`-based plugin API (backward-compatible through the 1.x series):

```python
from gemstack.plugins.hooks import hookimpl

class MobilePlugin:
    @hookimpl
    def gemstack_register_topologies(self):
        return [{"name": "mobile", "description": "iOS/Android", "content": "..."}]

    @hookimpl
    def gemstack_post_init(self, project_root, profile):
        (project_root / ".agent" / "MOBILE.md").write_text("# Mobile Context")
```

### 🔍 Context Drift Detection
Catch when your codebase drifts from what's documented. Gemstack compares your actual dependencies, environment variables, and file references against your `.agent/` context:

```bash
gemstack diff    # Detect new deps, removed env vars, stale file refs
gemstack check   # Validate .agent/ directory integrity
```

### 📊 28 CLI Commands Across 7 Categories

| Category | Commands | Purpose |
|----------|----------|---------|
| **Setup** | `init`, `install`, `uninstall`, `doctor`, `config` | Project bootstrapping, CLI registration, environment validation |
| **Workflow** | `status`, `route`, `start`, `phase`, `run` | Lifecycle management, autonomous execution |
| **Context** | `compile`, `diff`, `export`, `snapshot`, `migrate` | Prompt compilation, drift detection, format exports |
| **Analysis** | `check`, `compare`, `replay`, `matrix` | Validation, benchmarking, retrospectives, cross-project dashboards |
| **Tooling** | `mcp`, `hook`, `worktree`, `ci`, `scaffold` | MCP server, git hooks, parallel worktrees, CI generation |
| **ML/AI** | `prompt`, `eval` | Prompt template versioning, evaluation runner with holdout boundary |
| **DX** | `tail`, `teach` | Live TUI dashboard, interactive tutorial |

---

## Quickstart

```bash
# 1. Install (with AI bootstrapping + MCP server support)
pipx install "gemstack[ai,mcp]"

# 2. Initialize your project (AI auto-detects stack, topology, and commands)
cd your-project/
gemstack init --ai

# 3. See your current lifecycle state
gemstack status

# 4. Get the recommended next action
gemstack route

# 5. Start a new feature lifecycle
gemstack start "Add user search"

# 6. Execute Step 1 autonomously via Gemini
gemstack run step1-spec --feature "Add user search"
```

### Alternative Install Methods

```bash
uv tool install "gemstack[all]"          # uv (fastest)
pip install "gemstack[all]"              # Standard pip
pipx install gemstack                    # Minimal (no AI, no MCP)
```

---

## How It Works: The Context Compiler

The **Context Compiler** is the engine that makes Gemstack work. When you run a workflow step, it performs **JIT (Just-In-Time) prompt assembly**:

1. **Parses the workflow** — Extracts required roles and phases from the step definition
2. **Loads role definitions** — Bundles expert personas (Architect, SDET, Security Engineer, etc.)
3. **Loads phase instructions** — Attaches phase-specific behavioral rules (Ideate, Design, Build, etc.)
4. **Applies topology guardrails** — Detects your project topology from `ARCHITECTURE.md` and injects domain-specific constraints
5. **Compiles `.agent/` context** — Reads your project's architecture, style, testing, and status files
6. **Includes relevant source files** — Pulls in files referenced in `STATUS.md`
7. **Fires plugin hooks** — Lets plugins modify sections before/after compilation
8. **Applies token budgeting** — Truncates lowest-priority sections first if you exceed your context window

```bash
gemstack compile step3-build                   # View the full compiled prompt
gemstack compile step3-build --max-tokens 100000  # With token limits
```

---

## Compatibility

| | Supported |
|---|-----------|
| **Python** | 3.10, 3.11, 3.12, 3.13 |
| **OS** | macOS, Linux, Windows (WSL) |
| **AI Backend** | Google Gemini (via `google-genai`) |
| **MCP Transport** | stdio, SSE |
| **Project Languages** | TypeScript/JavaScript, Python, Go, Rust (auto-detected) |
| **Package Managers** | npm, pnpm, yarn, bun, pip, uv, poetry, cargo, go mod |

---

## Documentation

| | |
|---|---|
| 📚 [Getting Started](docs/getting-started.md) | Installation, initialization, and your first workflow |
| ⚙️ [The `.agent/` Context System](docs/the-agent-context.md) | How the 5 context files drive AI behavior |
| 🔄 [The 5-Step Lifecycle](docs/the-5-step-lifecycle.md) | Spec → Trap → Build → Audit → Ship in depth |
| 📐 [Topology-Aware Guardrails](docs/topologies.md) | Domain-specific guardrails for every project type |
| 🔌 [MCP Server & IDE Integration](docs/mcp-server.md) | Connecting Gemstack to Cursor, Claude, and Cline |
| 🧩 [Building Custom Plugins](docs/plugins.md) | Extending Gemstack with custom topologies, roles, and hooks |
| 🔧 [Full CLI Reference](docs/cli-reference.md) | All 28 commands with usage and examples |
| 🛠️ [Configuration & Integrations](docs/configuration-and-integrations.md) | Global config, API keys, and Gemini CLI integration |

---

## Project Links

| | |
|---|---|
| 📋 [Changelog](CHANGELOG.md) | 🤝 [Contributing](CONTRIBUTING.md) |
| 🔒 [Security Policy](SECURITY.md) | 📜 [Code of Conduct](CODE_OF_CONDUCT.md) |
| 🐛 [Report a Bug](https://github.com/arvarik/gemstack/issues/new?template=bug_report.md) | 💡 [Request a Feature](https://github.com/arvarik/gemstack/issues/new?template=feature_request.md) |
| ⚖️ [License — Apache 2.0](LICENSE) | 🎓 Run `gemstack teach` for an interactive tutorial |
