---
name: build
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

2. **Compiler-in-the-Loop Feedback:**
   - **Crucial Rule:** Your prompt must explicitly state: "Run the test suite in the Antigravity terminal. You are locked in this phase until the terminal outputs Exit Code 0. Read stderr, fix the code, and retry autonomously."
   - Do not ask the human for help. The bash terminal is the objective, unyielding referee.
   - Do not shortcut or hardcode the "happy path" just to pass the tests. Write robust code.

## Accuracy Check
The human does not intervene. You must loop execution autonomously until Exit Code 0 is achieved.

## ROUTING PROTOCOL (Yield & Prompt)
At the end of your execution, or if you hit a blocker you cannot resolve, you must output a `### SYSTEM ROUTING` block. Explicitly tell the human orchestrator exactly what slash command to run next in a New Chat, or what human action is required.

**Example:**
```markdown
### SYSTEM ROUTING
[🛑] BLOCKED: I am building the frontend, but the backend `Interaction` schema is missing from ARCHITECTURE.md. I am yielding.
🟠 NEXT ACTION: Open a New Chat, run `/workflow:spec`, and instruct the Architect to define the Interaction schema.
```