---
name: tech-blueprint
description: Run the technical blueprint workflow
---
# Workflow: Technical Blueprint

**Goal:** Take the UX spec and turn it into API contracts, data models, and an actionable implementation task list.

## Composition
This workflow composes:
- **Roles:** `Architect`, `Principal Backend Engineer`, `Principal Frontend Engineer`
- **Phases:** `Design (Architecture)`, `Plan`

## Process

1. **Step 1: Architecture Design (Architect)**
   - Act as the **Architect**. Read the UX spec and define the system boundaries, data models, and **exact API contracts**.
   - Write the architecture design document to `docs/designs/YYYY-MM-DD-architect-{feature}.md` and update `.agent/ARCHITECTURE.md`.
   - Update `.agent/STATUS.md` with your progress.

2. **Step 2: Implementation Planning (Principal Engineers)**
   - Act as the **Principal Engineers**. Read the architecture and UX specs.
   - Break down the work into an ordered list of implementable tasks. Identify parallelization opportunities and branch dependencies.
   - Write the backend plan to `docs/plans/YYYY-MM-DD-principal-backend-engineer-{feature}.md`.
   - Write the frontend plan to `docs/plans/YYYY-MM-DD-principal-frontend-engineer-{feature}.md`.
   - Update `.agent/STATUS.md` with your progress.

## Code Writing Policy
**STRICTLY PROHIBITED.** You are operating in a planning and design capacity. You only write Markdown (`.md`) files. Do not implement the code you are planning.