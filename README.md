# Gemstack: Agentic Development Framework

A complete framework for standardizing AI Agent orchestration across all your software projects. Built on the principles of **Contract-Driven Development (CDD)** and **Compiler-in-the-Loop Feedback**, Gemstack defines a unified system of composable **roles** (how the agent thinks), **phases** (what process the agent follows), **topologies** (domain-specific guardrails), and an **Optimized 5-Step Sequence** to eliminate "Logic Drift" and hallucinations.

This repository serves as your **single source of truth**. By defining roles, phases, topologies, and workflows here, you ensure consistent, high-accuracy, and non-hallucinated AI output across multiple projects and tech stacks.

For setup and installation instructions, please refer to [SETUP.md](SETUP.md).

---

## Repository Structure

```text
gemstack/
├── roles/                  # 9 agent mindset definitions
│   ├── product-visionary.md
│   ├── ui-ux-designer.md
│   ├── architect.md
│   ├── principal-backend-engineer.md
│   ├── principal-frontend-engineer.md
│   ├── ml-engineer.md
│   ├── sdet.md
│   ├── security-engineer.md
│   └── devops-engineer.md
│
├── phases/                 # 10 process step definitions
│   ├── ideate.md
│   ├── design.md
│   ├── contract-and-plan.md
│   ├── build.md
│   ├── fix.md
│   ├── test.md
│   ├── review.md
│   ├── integrate.md
│   ├── audit.md
│   └── ship.md
│
├── workflows/              # 5 composed multi-role sequences
│   ├── step1-spec.md       # Step 1: Product + UX + Architect
│   ├── step2-trap.md       # Step 2: Planner + SDET
│   ├── step3-build.md      # Step 3: Principal Engineer
│   ├── step4-audit.md      # Step 4: Security + SDET
│   └── step5-ship.md       # Step 5: DevOps + Principal Eng
│
├── topologies/             # 6 domain-specific guardrail profiles
│   ├── backend.md
│   ├── frontend.md
│   ├── ml-ai.md
│   ├── infrastructure.md
│   ├── library-sdk.md
│   └── llm-failure-modes.md
│
├── examples/               # Walkthrough per topology type
│   ├── frontend.md         # [frontend] — blog search feature
│   ├── full-stack.md       # [frontend, backend] — dashboard feature
│   ├── library-sdk.md      # [library-sdk, backend] — new SDK methods
│   ├── backend-ml-ai.md    # [backend, ml-ai] — ML pipeline feature
│   ├── full-stack-ai.md    # [frontend, backend, ml-ai] — AI CRM feature
│   └── infrastructure.md   # [infrastructure] — new service
│
├── context/                # Bootstrapping templates for new projects
│   ├── .agent/
│   │   ├── ARCHITECTURE.md
│   │   ├── STYLE.md
│   │   ├── TESTING.md
│   │   ├── PHILOSOPHY.md
│   │   └── STATUS.md
│   ├── docs/
│   │   ├── explorations/
│   │   ├── designs/
│   │   ├── plans/
│   │   └── archive/
│   ├── context_prompt.md   # AI bootstrapping script
│   └── .env.example
│
├── README.md               # This file
└── SETUP.md                # Installation and setup instructions
```

### How Distribution Works

All files in `roles/`, `phases/`, `workflows/`, and `topologies/` are **symlinked** into `~/.gemini/antigravity/global_workflows/`. This makes every role, phase, workflow, and topology available as a global slash command (`/role-name`, `/phase-name`, etc.) across **all repositories** in both Antigravity and Gemini CLI.

You edit the source `.md` files here in gemstack → the symlinks propagate the changes instantly → every project sees the update.

> **Note:** `.agent/workflows/` in each individual repo is for **repo-local** slash commands only (project-specific workflows). The global distribution from gemstack uses the `~/.gemini/antigravity/global_workflows/` path exclusively.

---

## 1. Roles (9 Total)

Roles define **mindset**. They are stack-agnostic — the same role works whether the project is Go, Python, TypeScript, or a shell script.

| Role | Mindset | Code Policy |
|------|---------|-------------|
| **Product Visionary** | Thinks like a founder. Focuses on user pain points, product workflows, and vision. | Markdown only |
| **UI/UX Designer** | The user's advocate. Focuses on information hierarchy, interaction states, and accessibility. | Markdown only |
| **Architect** | The author of Executable Truth. Defines strict API contracts, DB schemas, and system boundaries. | Markdown only |
| **Principal Backend Engineer** | Focuses on reliability, API design, data correctness, and system performance. | Application code |
| **Principal Frontend Engineer** | Focuses on UI implementation, accessibility, visual consistency, and client-side performance. | Application code |
| **ML / Data Engineer** | Works at the intersection of research and production. Model selection, pipeline design, LLM integration. | Application code |
| **SDET (Contract Enforcer)** | Writes automated, failing test suites *before* code is built, based on the Architect's contracts. | Test code only |
| **Security Engineer** | An attacker with a conscience. Assesses threat models, prompt injection, cost exhaustion, and logic drift. | Markdown only |
| **DevOps & Infrastructure Engineer** | Focuses on repeatable deployments, infrastructure hardening, and cost control. | Infrastructure code only |

---

## 2. Phases (10 Total)

Phases define **process**. Each phase has clear inputs, outputs, and a transition condition.

| Phase | Purpose | Key Output |
|-------|---------|------------|
| **Ideate** | Generate and prioritize what to build next. | `docs/explorations/` feature proposal |
| **Design** | Define the UX and architecture with executable contracts. | `docs/designs/` spec + `ARCHITECTURE.md` contracts |
| **Contract & Plan** | Break the design into an ordered, implementable task list. | `docs/plans/` task list |
| **Build** | The Autonomous Factory. Write code, loop against terminal until Exit Code 0. | Passing application code |
| **Fix** | Scoped bug fixes. Diagnose → fix → verify. Does not expand scope. | Bug resolution |
| **Test** | Systematic verification. Backend via CLI, frontend via headless Playwright. | `TESTING.md` results with execution evidence |
| **Review** | Read-only architectural and code quality review. | Review findings |
| **Integrate** | Strip mock data (`// TODO: remove stub`) and wire real systems together. | Production-wired code |
| **Audit** | Read-only SAST, edge cases, and "Logic Drift" detection. | `AUDIT_FINDINGS.md` |
| **Ship** | Merge, deploy, clean up artifacts, and reset `STATUS.md`. | Deployed feature |

### Feature Lifecycle Flow

```
ideate → design → contract & plan → build → test → review → ship
                       ↑              ↑       |        |
                       |              |       v        |
                       |              +---- fix ←------+ (localized bugs)
                       |                               |
                       +-------------------------------+ (architectural issues
                        go back to plan + build)
```

---

## 3. Topology-Aware Guardrails

Topologies are **domain-specific behavioral modifiers** that layer on top of roles and phases. Each project declares its topology attributes (e.g., `[frontend, backend, ml-ai]`) in `ARCHITECTURE.md` under `## 0. Project Topology`, and agents read the corresponding guardrail profiles before executing any workflow.

A project can have multiple topology attributes. A Next.js app with a Go backend is `[frontend, backend]`. A Go API with a RAG pipeline is `[backend, ml-ai]`.

| Topology | Key Guardrails |
|----------|----------------|
| **Backend** | Data integrity testing, anti-mocking rules, N+1 query detection, deterministic test discipline. |
| **Frontend** | Component state coverage matrix (empty/loading/success/error/partial), hydration safety, state management discipline. |
| **ML/AI** | Evaluation-Driven Development (EDD), circuit breaker for cost control, prompt versioning, eval/holdout boundary enforcement. |
| **Infrastructure** | YAML validation, no-auto-apply policy, port isolation, configuration drift detection. |
| **Library/SDK** | API surface stability (snapshot diffing), backward compatibility, zero-dependency discipline, semver enforcement. |

The `llm-failure-modes.md` profile is a supplementary reference catalog documenting 20+ known LLM agent failure patterns and mitigations, available for any agent to consult.

---

## 4. The Optimized 5-Step Workflow Sequence

To maximize accuracy and eliminate LLM hallucination, Gemstack uses a 5-step sequence with **"New Chat" airgaps** between each step. Each step runs in a fresh context window with a focused set of roles, forcing the LLM to prove its work against the terminal — not against its prior assumptions.

### 🟢 Step 1: `/step1-spec` (The Contract)
- **Roles:** Product Visionary + UI/UX Designer + Architect
- **Phases:** Ideate, Design
- **Action:** The human defines the feature. The agents design the UX. The Architect exports strict TypeScript/OpenAPI interfaces and DB schemas to `ARCHITECTURE.md`.
- **Accuracy Check:** No application code is written. We are locking in the exact boundaries.
- **ML/AI Topology:** When active, the ML Engineer joins this step for model selection, pipeline design, and performance target setting.

### 🟢 Step 2: `/step2-trap` (Setting the Trap)
- **Roles:** Principal Engineer + SDET
- **Phases:** Contract & Plan
- **Action:** The Planner writes the step-by-step task list. The SDET reads the API contracts from Step 1 and writes the **failing test suite**.
- **Accuracy Check:** The definition of "done" is now mathematically locked in code. The Builder's biases cannot corrupt the process.
- **ML/AI Topology:** When active, the ML Engineer defines evaluation thresholds and creates baseline eval sets.

### 🟢 Step 3: `/step3-build` (The Autonomous Factory)
- **Roles:** Principal Engineer (BE/FE)
- **Phases:** Build
- **Action:** The Builder reads the plan and writes the code. They are **locked in this phase** running the test suite in the terminal until it outputs Exit Code 0.
- **Accuracy Check:** The bash terminal is the objective, unyielding referee. The human does not intervene.
- **ML/AI Topology:** When active, the ML Engineer implements ML features and verifies eval scores meet thresholds.

### 🟢 Step 4: `/step4-audit` (The Jury)
- **Roles:** Security Engineer + SDET
- **Phases:** Test, Review, Audit
- **Action:** Fresh context window in read-only mode. They run SAST linters, test edge cases, and look for shortcuts the Builder took to pass the tests. Findings are written to `.agent/AUDIT_FINDINGS.md`.
- **Routing Loop:** If issues are found, a new `/step3-build` is spawned to fix them.
- **ML/AI Topology:** When active, the ML Engineer verifies eval scores haven't regressed and checks for cost overruns.

### 🟢 Step 5: `/step5-ship` (The Gatekeeper)
- **Roles:** DevOps Engineer + Principal Engineer
- **Phases:** Integrate, Ship
- **Action:** Merges branches, runs the **Integrate** phase to strip stubs and wire real systems, deploys, cleans up artifacts, and resets `STATUS.md`.

### State Machine Routing: Zero-Blocker Guarantee

To prevent agents from hanging on unknown variables, Gemstack implements a strict **Yield & Prompt Protocol**:
- **The Mutex Lock:** The Architect manages `.agent/STATUS.md` using explicit ENUM states (e.g., `[STATE: READY_FOR_BUILD]`). Agents must halt if the state does not match their phase.
- **The Routing Directive:** If an agent hits an unresolvable blocker, it outputs a `### SYSTEM ROUTING` block telling the human orchestrator the exact slash command to run next — completely eliminating orchestration ambiguity.

### Standalone Utility: `/fix`

Not every change needs the full 5-step ceremony. The `/fix` phase is a scoped shortcut for isolated bug fixes: **diagnose → patch → verify → done.** It does not expand scope, does not introduce new features, and returns the codebase to a known-good state. Use it when you find a bug that doesn't warrant Spec → Trap → Build.

---

## 5. Project Boundaries: The `.agent/` Context

While roles, phases, and topologies are **global** (shared across all projects), every project has unique rules. The `context/` folder in this repository provides a standardized `.agent/` directory template for all your repos.

### The Standardized Structure

Every repository you build should contain this structure at its root:

```text
.agent/
├── STATUS.md           # where we are, what to do next
├── ARCHITECTURE.md     # executable API contracts and architecture (includes topology declaration)
├── STYLE.md            # code and visual patterns
├── TESTING.md          # test methods, scenarios, and results with execution evidence
├── PHILOSOPHY.md       # product soul
└── AUDIT_FINDINGS.md   # created on-demand during Step 4 (Audit) — not a template

.env.example            # env vars with placeholder values

docs/
├── explorations/       # ideate phase output
├── designs/            # design phase output
├── plans/              # plan phase output
└── archive/            # shipped feature docs
```

### Bootstrapping

You don't fill these out manually. Copy the templates from `context/` into your new project and let the AI analyze your codebase and populate them with concrete, project-specific facts. See [SETUP.md § Bootstrapping a New Project](SETUP.md#bootstrapping-a-new-project-with-ai) for details.
