# Gemstack

**Opinionated AI agent orchestration framework for software engineering.**

[![PyPI version](https://img.shields.io/pypi/v/gemstack)](https://pypi.org/project/gemstack/)
[![Python](https://img.shields.io/pypi/pyversions/gemstack)](https://pypi.org/project/gemstack/)
[![License](https://img.shields.io/github/license/arvarik/gemstack)](LICENSE)
[![Typed](https://img.shields.io/badge/typing-typed-blue)](https://peps.python.org/pep-0561/)

![Gemstack Demo](https://raw.githubusercontent.com/arvarik/gemstack/main/docs/assets/demo-placeholder.png)

Gemstack gives your AI coding agents **structure, memory, and guardrails**. 

Instead of starting every conversation with *"here's my project…"* and hoping the AI remembers your arbitrary style rules, you define your architecture, test strategy, and coding philosophy exactly once in `.agent/` files. Gemstack compiles them into deterministic prompts, tracks token-budgets, automatically runs verification tasks in your terminal against a 5-step lifecycle, and forces AI models to write properly integrated code.

---

## Why Gemstack?

If you already use an AI IDE like Cursor or an agent like Aider, why do you need Gemstack? 

### Gemstack vs. Bottom-Up Agents (Aider, Copilot, Cursor)
Standard coding agents shine at "bottom-up" coding—you highlight a file and say "write this function." The downside? They suffer from serious architecture-amnesia. They often reinvent design patterns, rewrite perfectly good files to suit new logic, introduce conflicting libraries, and silently mutate critical path variables without testing.

**Gemstack is top-down.** It acts as the orchestrator *above* your editor.
1. **Architectural Guardrails**: Prevents the agent from rewriting your stack rules.
2. **Terminal Verified Execution**: It doesn't rely entirely on an agent saying it's done; it explicitly runs pipelines until `Exit Code 0` clears.
3. **Cognitive Airgaps**: Gemstack handles large features across 5 distinct lifecycle steps (Spec, Trap, Build, Audit, Ship) using completely fresh context windows, absolutely crushing hallucination rates.

If you want code completion, use an AI IDE. If you want structural engineering orchestration where an agent designs, tests, builds, and audits its own work securely, use **Gemstack**.

---

## Features at a Glance

* 🔧 **28 CLI Commands** — Full lifecycle management from `init` to `ship`.
* 📋 **The 5-Step Workflow** — Spec → Trap → Build → Audit → Ship.
* 🧠 **Context Compiler** — Token budgeting & truncation priorities.
* 🤖 **Autonomous Execution** — `gemstack run` writes files and loops against the terminal.
* 🔌 **Cursor/Claude Integrations** — Native [MCP Server](docs/mcp-server.md) support!
* 🧩 **Extensibility** — [Plugins](docs/plugins.md) to define new topologies and guardrails.

---

## Quickstart

```bash
# 1. Install recommended dependencies
pipx install "gemstack[ai,mcp]"

# 2. Bootstraps the framework + runs Gemini AI to inspect your project
cd your-project/
gemstack init --ai

# 3. Check what stage you should be in
gemstack route

# 4. Have the Gemini AI autonomously plan out Step 1.
gemstack run step1-spec --feature "Add user search"
```

---

## Documentation Deep Dives

Ready to master Gemstack? Head straight into the official documentation:

* 📚 [Getting Started](docs/getting-started.md)
* ⚙️ [The `.agent/` Context System](docs/the-agent-context.md)
* 🔄 [The 5-Step Lifecycle Breakdown](docs/the-5-step-lifecycle.md)
* 📐 [Topology-Aware Guardrails](docs/topologies.md)
* 🔌 [MCP Server (Cursor/Claude Integrations)](docs/mcp-server.md)
* 🧩 [Building Custom Plugins](docs/plugins.md)
* 🔧 [Full CLI Reference](docs/cli-reference.md)
* 🛠️ [Configurations & Integrations](docs/configuration-and-integrations.md)

---

## Compatibility

| | Supported |
|---|-----------|
| **Python** | 3.10, 3.11, 3.12, 3.13 |
| **OS** | macOS, Linux, Windows (WSL) |
| **AI Backend** | Google Gemini (via `google-genai`) |
| **MCP Transport** | stdio, SSE |

---

## Project Links

| | |
|---|---|
| 📋 [Changelog](CHANGELOG.md) | 🤝 [Contributing](CONTRIBUTING.md) |
| 🔒 [Security Policy](SECURITY.md) | 📜 [Code of Conduct](CODE_OF_CONDUCT.md) |
| 🐛 [Report a Bug](https://github.com/arvarik/gemstack/issues/new?template=bug_report.md) | 💡 [Request a Feature](https://github.com/arvarik/gemstack/issues/new?template=feature_request.md) |
| ⚖️ [License — Apache 2.0](LICENSE) | 🎓 Run `gemstack teach` for an interactive tutorial |
