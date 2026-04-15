---
name: contract-and-plan
description: Define executable contracts, schemas, and break the design into an ordered task list
---
# Phase: Contract & Plan

Purpose: Enforce executable contracts and break a design into an ordered, implementable task list.

## Primary Roles
- Architect
- Principal Backend Engineer
- Principal Frontend Engineer

## Inputs
- UX Design doc(s) from the spec phase
- .agent/ARCHITECTURE.md
- .agent/STATUS.md

## Process
1. **Enforce Executable Contracts (Architect):** Before any implementation planning begins, the Architect MUST generate strict executable interface files (e.g., `schema.prisma`, `types/api.ts`, `openapi.yaml`). If these files do not exist or are just Markdown bullet points, **STOP**. Instruct the Architect to create the actual code files.
2. **Read the Specs:** Read the full design spec and the executable contracts.
3. **Breakdown (Principal Engineers):** Identify every piece of work needed to implement the feature based strictly on the contracts.
4. **Order Tasks:** Order tasks by dependency (what blocks what).
5. **Specify Tasks:** For each task, specify:
   - What files need to change or be created
   - What the change actually is (specific, not vague)
   - Estimated complexity: trivial / moderate / complex
   - Dependencies on other tasks

## Transition
Done when the Architect has provided executable contracts AND the Principal Engineers have an ordered task list that can be handed to the SDET to lay the test traps.