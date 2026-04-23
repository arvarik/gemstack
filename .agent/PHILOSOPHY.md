# Philosophy

_The core principles that should guide every design, code, and product decision in this project. Agents and developers: read this before writing any code._

## Core Mission

Gemstack exists to make AI coding agents *actually useful* at scale — not just for one-off code completions, but for sustained, multi-session, production-grade software development.

## Principles

### 1. Top-Down, Not Bottom-Up

Most AI coding tools are bottom-up: highlight a file, say "write this function." Gemstack is top-down: it provides the orchestration layer *above* the editor. The agent gets full architectural context, not just the file it's looking at.

**Implication:** Never build features that only work at the file level. Every feature should be aware of the project's architecture, topology, and lifecycle state.

### 2. Deterministic Over Probabilistic

AI outputs are inherently probabilistic. Gemstack wraps them in deterministic processes — phase routing, exit-code verification, cost circuit breakers — to produce predictable outcomes.

**Implication:** Every workflow step must have a verifiable success condition (test pass, lint pass, exit code 0). "It looks right" is never a valid acceptance criterion.

### 3. Context Is King

The quality of an AI agent's output is a direct function of the context it receives. Gemstack's `.agent/` files are the single source of truth that prevents architecture amnesia across sessions.

**Implication:** Invest heavily in context quality. A well-written ARCHITECTURE.md is worth more than a clever prompt. Never generate low-quality context — it poisons every downstream step.

### 4. Topology-Aware, Not One-Size-Fits-All

A React SPA and a Go microservice need fundamentally different guardrails. Gemstack detects what kind of software you're building and loads domain-specific rules.

**Implication:** Every guardrail, testing matrix, and workflow step should be scoped to the project's declared topology. Generic advice is worse than no advice.

### 5. Verification Over Trust

Never trust the AI's self-reported "Done!" Always verify against the terminal. Tests must pass. Linters must pass. Builds must succeed.

**Implication:** Every `gemstack run` execution must compile, test, and verify. The cost circuit breaker exists to prevent runaway API calls when the agent is stuck in a loop.

### 6. Minimal Core, Extensible Surface

The core CLI should be dependency-light (8 runtime deps). Advanced features (AI, MCP, TUI, plugins) are optional extras. No user should install `torch` to run `gemstack check`.

**Implication:** Never promote an optional dependency to a core requirement. Use the extras system (`pip install gemstack[ai]`) to keep the install footprint minimal.

### 7. Dogfood Everything

If gemstack can't manage its own development, it can't manage anyone else's. The framework must be used to build the framework.

**Implication:** This `.agent/` directory exists because gemstack should eat its own dog food. Every feature should be validated by using it on the gemstack repo itself.

## Product Boundaries

### What Gemstack IS:
- An orchestration framework that sits above the editor
- A context management system for AI agents
- A lifecycle enforcer with deterministic phase routing
- A topology-aware guardrail engine

### What Gemstack IS NOT:
- A code editor or IDE
- An AI model or inference engine
- A replacement for git, CI/CD, or testing frameworks
- A project management tool
