# Gemstack: Agentic Development Framework

A complete framework for standardizing AI Agent orchestration across all your software projects. Built on the principles of **Contract-Driven Development (CDD)** and **Compiler-in-the-Loop Feedback**, Gemstack defines a unified system of composable **roles** (how the agent thinks), **phases** (what process the agent follows), **topologies** (domain-specific guardrails), and an **Optimized 5-Step Sequence** to eliminate "Logic Drift" and hallucinations.

This repository serves as your **single source of truth**. By defining roles, phases, topologies, and workflows here, you ensure consistent, high-accuracy, and non-hallucinated AI output across multiple projects and tech stacks. 

For setup and installation instructions, please refer to [SETUP.md](SETUP.md).

## Directory Structure

*   `roles/`: Contains markdown files defining agent mindsets (e.g., `architect.md`, `sdet.md`).
*   `phases/`: Contains markdown files defining the workflow steps (e.g., `contract-and-plan.md`, `build.md`).
*   `workflows/`: Contains the strict 5-step sequence that combines multiple roles and phases (e.g., `spec.md`, `build.md`).
*   `topologies/`: Contains domain-specific guardrail profiles (e.g., `backend.md`, `frontend.md`, `ml-ai.md`) and the LLM failure modes reference.
*   `context/`: Contains the master templates for project-specific rules (e.g., `ARCHITECTURE.md`, `STYLE.md`, `TESTING.md`) and the AI bootstrapping script.
*   `roles_phases.md`: The original master document containing all definitions.

---

## 1. Global Skills: Roles & Phases

The `roles/`, `phases/`, and `workflows/` folders act as global commands. You edit the markdown files here, and they become instantly available as slash commands (`/`) in both **Gemini CLI** and **Antigravity**.

### The Roles
Roles define **mindset**. Roles are stack-agnostic.
*   **Product Visionary**: Thinks like a founder. Focuses on user pain points, product workflows, and vision.
*   **UI/UX Designer**: The user's advocate. Focuses on information hierarchy and interaction states.
*   **Architect**: The author of Executable Truth. Defines strict, executable API contracts (`schema.prisma`, `types/api.ts`) to ensure boundaries.
*   **Principal Backend Engineer**: Focuses on reliability, API design, and data correctness.
*   **Principal Frontend Engineer**: Focuses on UI implementation, accessibility, and client-side performance.
*   **SDET (Contract Enforcer)**: Formally QA. Writes automated, failing test suites *before* code is built based on the Architect's contracts.
*   **Security Engineer**: An attacker with a conscience. Assesses threat models and logic drift.
*   **DevOps & Infrastructure Engineer**: Focuses on repeatable deployments and robust infrastructure.

### The Phases
Phases define **process**. Each phase has clear inputs, outputs, and a transition condition.
*   **Ideate**: Generate and prioritize what to build next.
*   **Design**: Define the UX and architecture.
*   **Contract & Plan**: Enforce executable contracts and break the design into an ordered task list.
*   **Build**: The Autonomous Factory. Write the code and loop against the terminal until the test suite passes with Exit Code 0.
*   **Integrate**: Strictly tasked to strip mock data (`// TODO: remove stub`) and wire real systems together.
*   **Audit**: A read-only phase for SAST, edge cases, and catching "Logic Drift".
*   **Ship**: Merge, deploy, and clean up.

### Topology-Aware Guardrails
Topologies are domain-specific behavioral modifiers that layer on top of roles and phases. Each project declares its topology attributes (e.g., `[frontend, backend, ml-ai]`) in `ARCHITECTURE.md`, and agents automatically load the corresponding guardrail profiles. Available topologies:
*   **Backend**: Data integrity testing, anti-mocking rules, N+1 query detection.
*   **Frontend**: Component state coverage matrix, hydration safety, state management discipline.
*   **ML/AI**: Evaluation-Driven Development (EDD), circuit breaker for cost control, prompt versioning.
*   **Infrastructure**: Configuration validation, no-auto-apply policy, port isolation.
*   **Library/SDK**: API surface stability, backward compatibility, zero-dependency discipline.

---

## 2. The Optimized 5-Step Workflow Sequence

To maximize absolute accuracy and eliminate LLM hallucination, Gemstack uses a highly accurate, blocker-free 5-step sequence. This sequence provides "New Chat" airgaps and forces the LLM to prove its work mathematically against the terminal.

### 🟢 Step 1: `/workflow:spec` (The Contract)
*   **Roles:** Product Visionary + UI/UX Designer + Architect
*   **Action:** The human defines the feature. The agents design the UX. Crucially, the Architect exports strict TypeScript/OpenAPI interfaces and DB schemas to `ARCHITECTURE.md`.
*   **Accuracy Check:** No application code is written yet. We are locking in the exact boundaries.

### 🟢 Step 2: `/workflow:trap` (Setting the Trap)
*   **Roles:** Planner (Principal Eng) + SDET
*   **Action:** The Planner writes the step-by-step task list. The SDET reads the API contracts from Step 1 and writes the failing test suite.
*   **Accuracy Check:** The definition of "done" is now mathematically locked in code. The Builder's biases cannot corrupt the process.

### 🟢 Step 3: `/workflow:build` (The Autonomous Factory)
*   **Roles:** Principal Engineer (BE/FE)
*   **Action:** The Builder reads the plan and writes the code. They are locked in this phase running the test suite in the terminal until it outputs Exit Code 0.
*   **Accuracy Check:** The bash terminal is the objective, unyielding referee. The human does not intervene.

### 🟢 Step 4: `/workflow:audit` (The Jury)
*   **Roles:** Security Engineer + SDET
*   **Action:** Fresh context window in read-only mode. They run SAST linters, test edge cases, and look for shortcuts the Builder took to pass the tests. Findings are written to `.agent/AUDIT_FINDINGS.md`.
*   **Routing Loop:** If issues are found, a new `/workflow:build` is spawned to fix them.

### 🟢 Step 5: `/workflow:ship` (The Gatekeeper)
*   **Roles:** DevOps Engineer + Principal Eng
*   **Action:** Merges branches, runs the **Integrate** phase to strip stubs and wire systems, deploys, cleans up artifacts, and resets `STATUS.md`.

### State Machine Routing: Guaranteeing Zero Blockers
To prevent agents from hanging when they hit unknown variables, Gemstack implements a strict **Yield & Prompt Protocol**:
*   **The Mutex Lock**: The Architect manages `.agent/STATUS.md` using explicit ENUM states (e.g., `[STATE: READY_FOR_BUILD]`). Agents must halt if the state does not match their phase.
*   **The Routing Directive**: If an agent hits an unresolvable blocker, it outputs a `### SYSTEM ROUTING` block telling the human orchestrator the exact slash command to run next, completely eliminating orchestration ambiguity.

---

## 3. Project Boundaries: The `.agent/` Context

While roles and phases are global, every project has unique rules. The `context/` folder in this repository solves the "context drift" problem by providing a standardized `.agent/` directory for all your repos.

### The Standardized Structure
Every repository you build should contain this structure at its root:
```text
.agent/
├── STATUS.md           # where we are, what to do next
├── ARCHITECTURE.md     # executable API contracts and architecture
├── STYLE.md            # code and visual patterns
├── TESTING.md          # test methods and results
└── PHILOSOPHY.md       # product soul

.env.example            # env vars with placeholder values

docs/
├── explorations/       # ideate phase output
├── designs/            # design phase output
├── plans/              # plan phase output
└── archive/            # shipped feature docs
```