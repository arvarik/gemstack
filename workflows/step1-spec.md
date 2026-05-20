---
name: step1-spec
description: "Step 1: Define the feature, design UX, and lock in executable contracts"
---
# Workflow: Spec (The Contract)

<thinking_process>
The Spec phase is about creating the "Architectural Truth." Think about:
1. Which stakeholders (Product, UX, Architect) need to weigh in.
2. What are the "Locked-In" deliverables (Plan, Contracts, Schemas).
</thinking_process>

**Goal:** Define the feature, design the UX, and lock in the exact boundaries with executable contracts.

## Composition
- **Roles:** `Product Visionary`, `UI/UX Designer`, `Architect`
- **Phases:** `Ideate`, `Design`
- **Native Tools:** Uses `implementation_plan.md` artifact.

## Process

1.  **Ideate**: The **Product Visionary** defines the user story and success metrics.
2.  **Design**: The **UI/UX Designer** drafts the interface and flow.
3.  **Lock Contracts**: The **Architect** defines the API types, DB schemas, and system boundaries.

## Accuracy Checks
- [ ] Does the `implementation_plan.md` clearly define the "Happy Path" and "Edge Cases"?
- [ ] Are all API boundaries defined in code (Typescript types, Protobuf, etc.)?
- [ ] Is the database schema locked and verified?

[STATE: READY_FOR_TRAP]