# Gemstack: Agentic Development Framework

A complete framework for standardizing AI Agent orchestration across all your software projects. Whether you are using Gemini CLI, Antigravity, Claude Code, or any LLM-based coding tool, Gemstack defines a unified system of composable **roles** (how the agent thinks), **phases** (what process the agent follows), and **project context** (the boundaries and rules of the specific codebase).

This repository serves as your **single source of truth**. By defining roles, phases, and templates here, you ensure consistent, high-quality, and non-hallucinated AI output across multiple projects and tech stacks. 

For setup and installation instructions, please refer to [SETUP.md](SETUP.md).

## Directory Structure

*   `roles/`: Contains markdown files defining agent mindsets (e.g., `architect.md`, `product-visionary.md`).
*   `phases/`: Contains markdown files defining the workflow steps (e.g., `plan.md`, `build.md`).
*   `workflows/`: Contains composed workflows that combine multiple roles and phases (e.g., `product-definition.md`).
*   `context/`: Contains the master templates for project-specific rules (e.g., `ARCHITECTURE.md`, `STYLE.md`, `TESTING.md`) and the AI bootstrapping script.
*   `roles_phases.md`: The original master document containing all definitions.

---

## 1. Global Skills: Roles & Phases

The `roles/`, `phases/`, and `workflows/` folders act as global commands. You edit the markdown files here, and they become instantly available as slash commands (`/`) in both **Gemini CLI** and **Antigravity**.

### How It Works
*   **Antigravity:** Uses the `.md` files directly via symlinks. It requires a YAML frontmatter block (e.g., `--- name: architect ---`) at the top of each file.
*   **Gemini CLI:** Uses `.toml` wrappers that dynamically read (inject) the contents of your `.md` files using the `!{cat ...}` shell command.

Because both tools reference the files in this repository, **any edits you make here will instantly apply globally across all your projects.**

### Usage Example
In Gemini CLI (namespaced):
> `/roles:principal-frontend-engineer /phases:build Help me implement the UI component defined in the plan.`

In Antigravity (flat):
> `/principal-frontend-engineer /build Help me implement the UI component defined in the plan.`

---

## 2. Composed Workflows

To reduce manual prompt interventions and keep the LLM's cognitive load focused, Gemstack includes composed workflows. These workflows group roles and phases by cognitive boundaries.

1. **The `Product Definition` Workflow (`/workflows:product-definition`)**
   *   **Composes:** `Product Visionary` + `UI/UX Designer` + `Ideate Phase` + `Design Phase (UX)`
   *   **Goal:** Go from a raw idea to a concrete feature proposal and UX specification.
2. **The `Technical Blueprint` Workflow (`/workflows:tech-blueprint`)**
   *   **Composes:** `Architect` + `Engineers (Advisory)` + `Design Phase (Arch)` + `Plan Phase`
   *   **Goal:** Take the UX spec and turn it into API contracts, data models, and an actionable implementation task list.
3. **The `Implementation Loop` Workflows (`/workflows:implement-backend` & `/workflows:implement-frontend`)**
   *   **Composes:** `Principal Engineer` + `Build Phase` + `Fix Phase`
   *   **Goal:** Read the plan, write the code, and fix localized bugs.
4. **The `Release Gatekeeper` Workflow (`/workflows:release-gatekeeper`)**
   *   **Composes:** `QA Engineer` + `Security Engineer` + `DevOps Engineer` + `Test`, `Review`, `Ship` Phases
   *   **Goal:** Break the app, log evidence, do a final sanity check, deploy, and clean up the archive folders.

---

## 3. Project Boundaries: The `.agent/` Context

While roles and phases are global, every project has unique rules. The `context/` folder in this repository solves the "context drift" problem by providing a standardized `.agent/` directory for all your repos.

### The Standardized Structure
Every repository you build should contain this structure at its root:
```text
.agent/
├── STATUS.md           # where we are, what to do next, relevant file pointers
├── ARCHITECTURE.md     # how the system is built, data models, API contracts
├── STYLE.md            # code and visual patterns, explicit anti-patterns
├── TESTING.md          # test methods, scenarios, results with evidence
└── PHILOSOPHY.md       # product soul - why this exists, core beliefs

.env.example            # all required env vars with placeholder values and comments

docs/
├── explorations/       # ideate phase output
├── designs/            # design phase output
├── plans/              # plan phase output
└── archive/            # shipped feature docs
```

### Feature Lifecycle Flow
```
ideate --> design --> plan --> build --> test ----> review --> ship
                       ^        ^         |          |
                       |        |         v          |
                       |        +------ fix  <-------+ (localized bugs)
                       |        (scoped bug fixes
                       |         return to test)
                       |                             |
                       +-----------------------------+ (architectural issues
                        (structural problems go back    skip fix, return to
                         to plan + build, not fix)      plan + build)
```

### Role x Phase Matrix
*(📝 = Produces/Updates Markdown files | 💻 = Produces/Modifies Code or Infra)*

| Role | Ideate | Design | Plan | Build | Fix | Test | Review | Ship |
|---|---|---|---|---|---|---|---|---|
| Product Visionary | 📝 Primary | | | | | | 📝 Periodic | |
| UI/UX Designer | 📝 Secondary | 📝 Primary | | | | | | |
| Architect | | 📝 Primary | 📝 Advisory | | | | 📝 Primary | |
| Backend Engineer | 📝 Secondary | 📝 Secondary | 📝 Primary | 💻 Primary | 💻 Primary | | | |
| Frontend Engineer | 📝 Secondary | 📝 Secondary | 📝 Primary | 💻 Primary | 💻 Primary | | | |
| ML Engineer | 📝 Secondary | 📝 Primary | 📝 Primary | 💻 Primary | 💻 Primary | 💻/📝 Primary | | |
| QA Engineer | | | | | | 💻/📝 Primary | | |
| Security Engineer | | | | | | | 📝 Primary | 📝 Advisory |
| DevOps Engineer | | | | | | | | 💻 Primary |
