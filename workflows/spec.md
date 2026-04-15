---
name: spec
description: Run the spec workflow (Step 1)
---
# Workflow: Spec (The Contract)

**Goal:** Define the feature, design the UX, and lock in the exact boundaries with executable contracts.

## Composition
This workflow composes:
- **Roles:** `Product Visionary`, `UI/UX Designer`, `Architect`
- **Phases:** `Ideate`, `Design`

## Process

1. **Product & UX (Product Visionary + UI/UX Designer):**
   - The human defines the feature.
   - Design the user experience and interactions. Define what the feature should be before anyone writes code. Write UX specs.

2. **Architecture & Contracts (Architect):**
   - Act as the Architect. Read the UX spec.
   - **CRUCIAL:** Export strict TypeScript/OpenAPI interfaces and Database schemas to `ARCHITECTURE.md` (e.g., `schema.prisma`, `types/api.ts`, `openapi.yaml`).
   - Do not write application code yet. We are locking in the exact boundaries.

## Accuracy Check
No application logic or feature code is written in this phase. The definitions and executable contracts MUST be locked in before proceeding to Step 2.

## ROUTING PROTOCOL (Yield & Prompt)
At the end of your execution, or if you hit a blocker you cannot resolve, you must output a `### SYSTEM ROUTING` block. Explicitly tell the human orchestrator exactly what slash command to run next in a New Chat, or what human action is required.

**Example:**
```markdown
### SYSTEM ROUTING
[🛑] BLOCKED: I am building the frontend, but the backend `Interaction` schema is missing from ARCHITECTURE.md. I am yielding.
🟠 NEXT ACTION: Open a New Chat, run `/workflow:spec`, and instruct the Architect to define the Interaction schema.
```