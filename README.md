# 💎 Gemstack

**The high-velocity AI agent orchestration framework, natively optimized for Antigravity.**

[![CI Status](https://img.shields.io/github/actions/workflow/status/arvarik/gemstack/test.yml?branch=main&style=flat-square)](https://github.com/arvarik/gemstack/actions)
[![Version](https://img.shields.io/github/v/release/arvarik/gemstack?style=flat-square)](https://github.com/arvarik/gemstack/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](LICENSE)

---

## 🚀 Gemstack 2.0: The Antigravity Release

Gemstack has evolved. Version 2.0 is a fundamental architectural shift that moves beyond simple prompt-stitching into **Native Agentic Orchestration**. It is designed specifically to harness the full power of the **Antigravity (`agy`) CLI**.

### What makes 2.0 different?

*   **🧠 XML-Structured Mindsets**: Every expert role (Architect, SDET, DevOps, etc.) now uses a high-precision XML-tagged mindset. This ensures perfect instruction following and eliminates "Logic Drift" when working with Gemini 1.5 Pro and 2.0.
*   **🤖 Autonomous Subagents**: Roles are now **Subagent-Aware**. The framework no longer just tells the AI what to do; it gives the AI the tools to delegate. The Architect can now autonomously spawn a Security subagent to audit a schema before it ever reaches your codebase.
*   **📊 Native Artifact Integration**: We've deprecated manual planning files in favor of native Antigravity artifacts. `IMPLEMENTATION_PLAN.md`, `task.md`, and `walkthrough.md` are now the living, breathing heart of your project, providing real-time visual progress tracking.
*   **📐 Modern Topology Guardrails**: Topologies have been refreshed for the 2025 stack. 
    *   **Backend**: Drizzle ORM + Playwright integration.
    *   **Frontend**: Next.js 15 Server Components & Server Actions.
    *   **Infrastructure**: Proxmox/LXC resource limits and Caddy DNS-01 automation.
*   **🔍 Deterministic Phase Routing**: The new `agy` routing engine replaces the old status-file check with a high-fidelity artifact monitor, ensuring you never skip a step in the lifecycle.

---

## 🏗️ The 5-Step Lifecycle

Gemstack enforces a rigorous, contract-driven engineering process:

1. **Step 1: Spec** → Define the feature, design UX, and lock in executable contracts (Architect).
2. **Step 2: Trap** → Write failing automated tests that "trap" the requirement before coding (SDET).
3. **Step 3: Build** → Implement the logic until the "traps" pass (Principal Engineers).
4. **Step 4: Audit** → Security, performance, and accessibility review (Security Engineer).
5. **Step 5: Ship** → Deployment, infrastructure provisioning, and post-flight checks (DevOps Engineer).

---

## 📦 Installation

```bash
# Recommended: Install everything (AI, MCP, TUI)
pipx install "gemstack[all]"

# Or via uv (fastest)
uv tool install "gemstack[all]"
```

---

## 📖 Documentation

*   [Getting Started](docs/getting-started.md) — From zero to your first v2.0 workflow.
*   [The 5-Step Lifecycle](docs/the-5-step-lifecycle.md) — How the orchestration engine works.
*   [Topology Guardrails](docs/topologies.md) — Domain-specific rules for every project type.
*   [MCP Server & IDE Integration](docs/mcp-server.md) — Connecting Gemstack to Cursor and Claude.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for our v2.0 XML prompting standards and development guidelines.

---

## ⚖️ License

Apache 2.0. See [LICENSE](LICENSE) for details.
