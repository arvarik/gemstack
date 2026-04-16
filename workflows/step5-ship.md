---
name: step5-ship
description: "Step 5: Integrate, merge, deploy, and reset for the next feature"
---
# Workflow: Ship (The Gatekeeper)

**Goal:** Merge branches, remove mocks, deploy, clean up artifacts, and reset.

## Composition
This workflow composes:
- **Roles:** `DevOps Engineer`, `Principal Engineer`
- **Phases:** `Integrate`, `Ship`

## Process

1. **Integrate Phase (Principal Engineer):**
   - Strictly strip all mock data (`// TODO: remove stub`).
   - Wire the real systems (frontend to backend) together.

2. **Cleanup & Finalize (DevOps Engineer):**
   - Move all feature-specific markdown files from `docs/` (e.g., explorations, designs, plans) into a new folder `docs/archive/{feature-name}`.
   - Reset `.agent/STATUS.md` to clear completed feature state and prepare for the next feature.
   - Clean `.agent/TESTING.md` by archiving completed feature-specific test scenarios.
   - Commit all final cleanup changes (code, docs archive, and `.agent` files) to the feature branch in a single commit.

3. **Merge & Deploy (DevOps Engineer):**
   - Merge the feature branch into the main branch (or create/merge PR).
   - Execute deployment scripts safely.

## Accuracy Check
The application is not shipped until all stubs are verifiably removed and the systems are fully integrated.

## ROUTING PROTOCOL (Yield & Prompt)
At the end of your execution, or if you hit a blocker you cannot resolve, you must output a `### SYSTEM ROUTING` block. Explicitly tell the human orchestrator exactly what slash command to run next in a New Chat, or what human action is required.

**Example:**
```markdown
### SYSTEM ROUTING
[🛑] BLOCKED: I am building the frontend, but the backend `Interaction` schema is missing from ARCHITECTURE.md. I am yielding.
🟠 NEXT ACTION: Open a New Chat, run `/step1-spec`, and instruct the Architect to define the Interaction schema.
```