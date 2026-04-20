# The 5-Step Lifecycle

Gemstack prevents AI hallucination through two core principles: **separation of concerns** (each step runs in a fresh context window) and **terminal-verified execution** (the agent must prove its work against your actual test suite, not just claim it's done).

---

## Overview

```text
Step 1          Step 2          Step 3          Step 4          Step 5
 Spec      →     Trap      →    Build      →    Audit      →    Ship
Define it     Write tests     Implement      Verify it      Merge & deploy
              that fail       until pass     (fresh eyes)
                                 ↑               │
                                 └──── fix ←─────┘
                                (if audit finds issues)
```

Every feature you build flows through these 5 steps. Each step uses entirely fresh context — the Auditor never sees the Builder's internal reasoning, and the SDET writes tests before any implementation code exists.

---

## Step 1: Spec — *"The Contract"*

**Command:** `gemstack run step1-spec --feature "..."`

**Goal:** Define the feature, design the UX, and lock in *executable contracts* before anyone writes implementation code.

**Roles Composed:**
| Role | Responsibility |
|------|---------------|
| Product Visionary | Defines what the feature is, who it's for, and why it matters |
| UI/UX Designer | Designs the user experience, interactions, and information architecture |
| Architect | Exports strict TypeScript/OpenAPI interfaces, database schemas, and API contracts to `ARCHITECTURE.md` |

**Process:**
1. The human provides a feature description (the `--feature` flag)
2. The Product Visionary and UI/UX Designer define what the feature should look like from the user's perspective
3. The Architect translates UX requirements into formal contracts — API endpoints, request/response shapes, database schema changes, environment variables
4. These contracts are written to `ARCHITECTURE.md` and optionally to `docs/explorations/`

**Accuracy Check:** No application code or feature logic is written in this step. The contracts MUST be locked in before proceeding.

**Status Transition:** `[STATE: INITIALIZED]` → `[STATE: IN_PROGRESS]` (Spec checkbox marked)

---

## Step 2: Trap — *"The Test-First Trap"*

**Command:** `gemstack run step2-trap --feature "..."`

**Goal:** Write the task plan and a **failing test suite** that defines exactly what "done" means — before any implementation exists.

**Roles Composed:**
| Role | Responsibility |
|------|---------------|
| Planner | Breaks the feature into an ordered task list with clear acceptance criteria |
| SDET | Writes the failing test suite based on the contracts locked in Step 1 |

**Process:**
1. Read the contracts from `ARCHITECTURE.md` and any exploration documents from Step 1
2. Create a detailed, ordered task plan in `docs/plans/`
3. Write test cases that validate every contract — happy paths, edge cases, error conditions
4. **All tests MUST fail** at this point (there's no implementation yet). If any test passes, it's probably testing the wrong thing
5. The test suite becomes the objective, unyielding definition of "done"

**Why "Trap"?** The test suite is a trap for the Builder AI in Step 3. The Builder can't claim success — it must make every test pass. This prevents the single most common AI failure mode: generating code that *looks* correct but doesn't actually work.

**Status Transition:** `[STATE: IN_PROGRESS]` → `[STATE: READY_FOR_BUILD]`

---

## Step 3: Build — *"The Autonomous Factory"*

**Command:** `gemstack run step3-build --feature "..."`

**Goal:** Implement the feature code and **loop against the terminal** until every test passes with Exit Code 0.

**Roles Composed:**
| Role | Responsibility |
|------|---------------|
| Principal Backend Engineer | Implements server-side logic, API routes, database queries |
| Principal Frontend Engineer | Implements UI components, state management, client-side logic |

**Process:**
1. Read the task plan and contracts from Steps 1–2
2. Write the application code to fulfill each task
3. **Static analysis first** — Run the type-checker and linter before the test suite (e.g., `tsc --noEmit`, `ruff check .`, `go vet ./...`). This catches errors faster and saves compute
4. **Compiler-in-the-Loop** — Run the full test suite in the terminal. The AI is locked in this phase until `Exit Code 0`. It reads `stderr`, fixes the code, and retries autonomously
5. **No shortcuts** — The AI must not hardcode happy-path values or mutate tests to make them pass. The tests from Step 2 are immutable

**Circuit Breaker (Bounded Reflexion):**
The build-test-fix cycle is bounded to a maximum of **3 attempts**. If the test suite still fails after 3 full loops:
1. Revert changes to last known-good state (`git checkout -- .`)
2. Write a `<reflection>` block explaining what was tried and why it failed
3. Yield back to the SDET for test review (the test itself may be flawed or the contract ambiguous)

**Status Transition:** `[STATE: READY_FOR_BUILD]` → `[STATE: READY_FOR_AUDIT]`

---

## Step 4: Audit — *"Fresh Eyes"*

**Command:** `gemstack run step4-audit --feature "..."`

**Goal:** Independent security review, SAST linting, and logic verification by an AI that **never saw the Builder's reasoning**.

**Roles Composed:**
| Role | Responsibility |
|------|---------------|
| Security Engineer | Reviews for vulnerabilities, injection attacks, auth bypass, data exposure |
| SDET | Validates edge cases, boundary conditions, and integration correctness |

**Process:**
1. This step starts in a **completely fresh context window** — no carry-over from the Build step
2. Read the implementation, the contracts, and the test results
3. Perform a structured security audit:
   - Input validation and sanitization
   - Authentication and authorization boundaries
   - SQL injection, XSS, CSRF, path traversal
   - Sensitive data exposure (API keys, tokens, PII)
   - Rate limiting and resource exhaustion
4. Perform a logic audit:
   - Contract compliance (does the code actually implement what was specified?)
   - Error handling completeness
   - Edge cases not covered by the existing test suite
5. Write findings to `.agent/AUDIT_FINDINGS.md`

**Why "Fresh Eyes" Matters:**
The Builder AI has an inherent bias — it believes its own code works. By running the audit in a fresh context, the Auditor cannot be influenced by the Builder's justifications, internal commentary, or rationalization. It evaluates the code purely on its merits.

**Routing After Audit:**
- **No findings** → Proceed to Step 5: Ship (`[STATE: READY_FOR_SHIP]`)
- **Findings exist** → The phase router automatically reroutes back to Step 3: Build with the audit findings attached as context, creating a fix loop until the audit passes clean

---

## Step 5: Ship — *"Close the Loop"*

**Command:** `gemstack run step5-ship --feature "..."`

**Goal:** Integrate, merge, deploy, and archive — then reset `STATUS.md` for the next feature.

**Roles Composed:**
| Role | Responsibility |
|------|---------------|
| DevOps Engineer | Handles integration, merge strategy, deployment pipeline, and post-deployment verification |

**Process:**
1. Final integration check — ensure all branches are merged cleanly
2. Verify CI pipeline passes (if configured)
3. Deploy to staging/production (project-specific)
4. Archive feature documents to `docs/archive/`
5. Remove `AUDIT_FINDINGS.md` (findings have been addressed)
6. Reset `STATUS.md` — clear the active feature, uncheck lifecycle boxes, set `[STATE: SHIPPED]`

**Status Transition:** `[STATE: READY_FOR_SHIP]` → `[STATE: SHIPPED]`

---

## The Routing Protocol

Every step ends with a **`### SYSTEM ROUTING`** block — a structured handoff that tells the human orchestrator exactly what to do next. This is not optional; it's enforced by every workflow template:

```markdown
### SYSTEM ROUTING
✅ COMPLETED: Step 1 Spec — contracts locked in ARCHITECTURE.md
🟢 NEXT ACTION: Open a New Chat, run `/step2-trap`, and instruct the SDET to
   write the failing test suite based on the contracts in ARCHITECTURE.md.
```

Or, if blocked:

```markdown
### SYSTEM ROUTING
[🛑] BLOCKED: Backend `Interaction` schema is missing from ARCHITECTURE.md.
🟠 NEXT ACTION: Open a New Chat, run `/step1-spec`, and instruct the
   Architect to define the Interaction schema before proceeding.
```

This protocol ensures you always have a clear, actionable next step — even across context window boundaries.

---

## Using `gemstack route`

At any point, you can ask Gemstack what to do next:

```bash
gemstack route
```

The deterministic phase router reads `STATUS.md` and `AUDIT_FINDINGS.md` to output a routing decision. It evaluates the following rules in order:

1. If `AUDIT_FINDINGS.md` exists with content → **Reroute to Build** (fix issues first)
2. `INITIALIZED` → `/step1-spec`
3. `IN_PROGRESS` → Continue with the current uncompleted step (inferred from lifecycle checkboxes)
4. `READY_FOR_BUILD` → `/step3-build`
5. `READY_FOR_AUDIT` → `/step4-audit`
6. `READY_FOR_SHIP` → `/step5-ship`
7. `SHIPPED` → Run `gemstack start <feature>` to begin a new cycle
8. Unknown state → **Blocked** — manual intervention required

---

## Cognitive Airgaps: Why Fresh Context Matters

The most important architectural decision in Gemstack's lifecycle is that **every step starts in a completely fresh context window**. Here's why:

| Failure Mode | How Airgaps Prevent It |
|-------------|----------------------|
| **Hallucination accumulation** | An agent's hallucinations compound over long conversations. Fresh context resets the error budget to zero. |
| **Sycophantic bias** | The Auditor would be biased if it could see the Builder's explanations. Fresh context makes the audit genuinely independent. |
| **Context window exhaustion** | Long conversations degrade quality as older context is pushed out. Each step gets the full window dedicated to a single concern. |
| **Rationalization loops** | An agent that wrote bad code will defend it. A fresh agent evaluates it objectively. |

This is the same principle behind code review in human teams: the reviewer should evaluate the code on its own merits, not be swayed by the author's reasoning in a Slack thread.
