# Getting Started with Gemstack 2.0

Gemstack 2.0 is designed for high-velocity software delivery using the **Antigravity (`agy`) CLI**. This guide covers how to initialize your project and run your first v2.0 workflow.

## Prerequisites

- **Python 3.10+**
- **Git**
- **Antigravity CLI (`agy`)** — Ensure `agy` is installed and on your PATH.
- **Google Gemini API Key** — For autonomous execution (`/step1-spec`, etc.).

---

## Installation

```bash
# Isolated install via pipx
pipx install "gemstack[all]"

# Or via uv
uv tool install "gemstack[all]"
```

---

## Initializing a Project

Navigate to your codebase and run:

```bash
gemstack init --ai
```

This will:
1. **Detect your stack** (Language, Framework, Topology).
2. **Generate the `.agent/` directory** with 5 core context files (`ARCHITECTURE.md`, `STYLE.md`, etc.).
3. **Set up the Gemstack Plugin** for your Antigravity environment.

---

## Running Your First v2.0 Workflow

In Gemstack 2.0, the lifecycle is managed natively within `agy` using artifacts.

### 1. Start a Feature
Initialize a new feature lifecycle:
```bash
agy "start a new feature: [Feature Name]"
```

### 2. Step 1: Spec
Run the Spec phase to define requirements and lock in contracts:
```bash
/step1-spec
```
This invokes the **Product Visionary** and **Architect** subagents. They will update the `implementation_plan.md` artifact and write executable contracts (e.g., Drizzle schemas) to your repo.

### 3. Step 2: Trap
Lay the failing tests:
```bash
/step2-trap
```
The **SDET** and **Principal Engineer** will create a `task.md` and write failing tests that "trap" the requirements.

### 4. Step 3: Build
Implement the logic:
```bash
/step3-build
```
The **Principal Engineers** will build the feature until all tests in the "Trap" suite pass.

### 5. Step 4: Audit
Run the final quality checks:
```bash
/step4-audit
```
The **Security Engineer** and **SDET** will audit the code and document the results in the `walkthrough.md` artifact.

### 6. Step 5: Ship
Deploy to production:
```bash
/step5-ship
```
The **DevOps Engineer** will handle the deployment and perform post-flight checks.

---

## Key Differences in v2.0

| Feature | v1.x (Legacy) | v2.0 (Native) |
|---------|---------------|---------------|
| **Primary Interface** | `gemstack` CLI | `agy` CLI / Slash Commands |
| **Status Tracking** | `.agent/STATUS.md` | Native `task.md` Artifact |
| **Planning** | `docs/plans/` | `implementation_plan.md` Artifact |
| **Role Prompts** | Standard Markdown | High-precision XML Tags |
| **Delegation** | Manual context switching | Autonomous Subagents |

---

## Next Steps

- 📐 Explore [Topology Guardrails](topologies.md) for your project type.
- 🧠 Learn how the [Context Compiler](context-compiler.md) assembles prompts.
- 🔍 Set up [Drift Detection](drift-detection.md) to keep docs in sync.
