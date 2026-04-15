---
name: trap
description: "Step 2: Write the task plan and lay the failing test suite trap"
---
# Workflow: Trap (Setting the Trap)

**Goal:** Write the step-by-step task list and lay the failing test suite trap.

## Composition
This workflow composes:
- **Roles:** `Principal Engineer`, `SDET`
- **Phases:** `Contract & Plan`

## Process

1. **Implementation Planning (Principal Engineer):**
   - Act as the Planner. Write the step-by-step implementable task list based strictly on the Architect's contracts from Step 1.
   - Write the plan to the `docs/plans/` directory.

2. **Contract Enforcement (SDET):**
   - Act as the SDET. Read the API contracts from Step 1.
   - Write the **failing test suite** based on these contracts (e.g., `tests/api.spec.ts`).
   - Test for edge cases, nulls, and rapid state changes. Ensure the test fails right now because the code hasn't been written.

## Accuracy Check
The definition of "done" is now mathematically locked in code. The Builder's biases cannot corrupt the process. The test suite MUST fail before proceeding to Step 3.

## ROUTING PROTOCOL (Yield & Prompt)
At the end of your execution, or if you hit a blocker you cannot resolve, you must output a `### SYSTEM ROUTING` block. Explicitly tell the human orchestrator exactly what slash command to run next in a New Chat, or what human action is required.

**Example:**
```markdown
### SYSTEM ROUTING
[🛑] BLOCKED: I am building the frontend, but the backend `Interaction` schema is missing from ARCHITECTURE.md. I am yielding.
🟠 NEXT ACTION: Open a New Chat, run `/workflow:spec`, and instruct the Architect to define the Interaction schema.
```