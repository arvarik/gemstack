---
name: step3-build
description: "Step 3: Autonomous code factory — implement and loop until tests pass"
---
# Workflow: Build (The Autonomous Factory)

**Goal:** Read the plan, write the application code, and run the test suite in the Antigravity terminal until it passes.

## Composition
This workflow composes:
- **Roles:** `Principal Backend Engineer`, `Principal Frontend Engineer`
- **Phases:** `Build`

## Process

1. **Implementation (Principal Engineer):**
   - Read the plan and the contracts.
   - Write the application code to fulfill the tasks.

2. **Static Analysis First:**
   - Before running the test suite, run the project's type-checker and linter first (e.g., `tsc --noEmit`, `go vet ./...`, `ruff check .`). Fix all static errors before executing the heavier test suite. This saves significant time and compute.

3. **Compiler-in-the-Loop Feedback:**
   - **Crucial Rule:** Your prompt must explicitly state: "Run the test suite in the Antigravity terminal. You are locked in this phase until the terminal outputs Exit Code 0. Read stderr, fix the code, and retry autonomously."
   - Do not ask the human for help. The bash terminal is the objective, unyielding referee.
   - Do not shortcut or hardcode the "happy path" just to pass the tests. Write robust code.

4. **Circuit Breaker (Bounded Reflexion):**
   - You may loop the build-test-fix cycle a maximum of **3 attempts**. If after 3 full attempts the test suite still fails, you must **STOP**.
   - Revert your changes to the last known-good state (`git checkout -- .` or `git stash`).
   - Write a `<reflection>` block explaining: what you tried, why it failed, and whether the test itself may be flawed or the contract may be ambiguous.
   - Output a `### SYSTEM ROUTING` block yielding to the SDET for test review.

5. **Update Lifecycle State:**
   - After all tests pass (Exit Code 0), you **MUST** update `.agent/STATUS.md` before yielding:
     - Mark the Build checkbox: `- [x] Build — <summary of what was built>`
     - Update the `**Phase:**` line to `Build → Audit`
     - Update test suite counts (e.g., "33 tests (33 passing)")
     - Mark any resolved Known Issues with ~~strikethrough~~ and **Fixed** annotations
   - This is **not optional**. The lifecycle router reads these checkboxes to determine the next step. If you skip this, the router will get stuck on `/step3-build` indefinitely.

## Accuracy Check
The human does not intervene. You must loop execution autonomously until Exit Code 0, up to the circuit breaker limit of 3 attempts.

## ROUTING PROTOCOL (Yield & Prompt)
At the end of your execution, or if you hit a blocker you cannot resolve, you must output a `### SYSTEM ROUTING` block. Explicitly tell the human orchestrator exactly what slash command to run next in a New Chat, or what human action is required.

**Example:**
```markdown
### SYSTEM ROUTING
[🛑] BLOCKED: I am building the frontend, but the backend `Interaction` schema is missing from ARCHITECTURE.md. I am yielding.
🟠 NEXT ACTION: Open a New Chat, run `/step1-spec`, and instruct the Architect to define the Interaction schema.
```