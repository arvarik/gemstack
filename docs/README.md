# Gemstack Documentation

**Opinionated AI agent orchestration framework for [Gemini CLI](https://github.com/google-gemini/gemini-cli) and [Antigravity](https://github.com/google-gemini/antigravity).**

Gemstack gives your Gemini-powered agents architectural memory, topology-aware guardrails, and a 5-step lifecycle that forces them to verify their work against your terminal — not just hallucinate a solution and tell you it's done.

---

## Getting Started

New to Gemstack? Start here:

- 📚 **[Getting Started](getting-started.md)** — Installation, initialization, and your first workflow

---

## Core Concepts

Understand the ideas that make Gemstack work. Read them in order:

1. ⚙️ **[The `.agent/` Context System](the-agent-context.md)** — How the 5 context files (ARCHITECTURE, STYLE, TESTING, PHILOSOPHY, STATUS) drive all AI behavior
2. 🔄 **[The 5-Step Lifecycle](the-5-step-lifecycle.md)** — Spec → Trap → Build → Audit → Ship explained in depth
3. 📐 **[Topology-Aware Guardrails](topologies.md)** — Domain-specific guardrails for backend, frontend, ML/AI, infrastructure, and library/SDK projects
4. 🧠 **[The Context Compiler](context-compiler.md)** — How Gemstack assembles JIT prompts from roles, phases, guardrails, and your `.agent/` files

---

## Feature Guides

Deep dives into Gemstack's major capabilities:

| Guide | What You'll Learn |
|-------|-------------------|
| 🤖 **[Autonomous Execution](autonomous-execution.md)** | The `gemstack run` command — compile context, call Gemini, write files, track costs |
| 🔍 **[Drift Detection](drift-detection.md)** | Catch when your codebase drifts from your `.agent/` documentation |
| 🔌 **[MCP Server & IDE Integration](mcp-server.md)** | Connect Gemstack to Cursor, Claude Desktop, Gemini CLI, and Cline |
| 🧩 **[Building Custom Plugins](plugins.md)** | Extend Gemstack with custom topologies, roles, and hooks |

---

## Reference

| Reference | Description |
|-----------|-------------|
| 🔧 **[Full CLI Reference](cli-reference.md)** | All 28 commands with usage, flags, and examples |
| 🛠️ **[Configuration & Integrations](configuration-and-integrations.md)** | Global config, API keys, cost tracking, Gemini CLI integration |

---

## Example Walkthroughs

End-to-end examples showing the complete 5-step lifecycle for different project types:

| Example | Topology | Description |
|---------|----------|-------------|
| [Full-Stack](../examples/full-stack.md) | `[frontend, backend]` | Go backend + Next.js frontend — sleep trends dashboard |
| [Frontend](../examples/frontend.md) | `[frontend]` | React SPA — component library with design system |
| [Backend + ML/AI](../examples/backend-ml-ai.md) | `[backend, ml-ai]` | Python API with LLM integration |
| [Full-Stack + AI](../examples/full-stack-ai.md) | `[frontend, backend, ml-ai]` | Full-stack app with AI-powered features |
| [Infrastructure](../examples/infrastructure.md) | `[infrastructure]` | Docker Compose + Terraform homelab |
| [Library/SDK](../examples/library-sdk.md) | `[library-sdk]` | Python package published to PyPI |

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup, code style, testing requirements, and pull request guidelines.
