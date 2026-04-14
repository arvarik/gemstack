---
name: implement-frontend
description: Run the frontend implementation workflow
---
# Workflow: Implement Frontend

**Goal:** Read the frontend plan, write the code, and fix any localized bugs as they arise.

## Composition
This workflow composes:
- **Roles:** `Principal Frontend Engineer`
- **Phases:** `Build`, `Fix`

## Process

1. **Step 1: Build**
   - Act as the **Principal Frontend Engineer**. Read your assigned tasks from the frontend plan in `docs/plans/`.
   - Implement the tasks step-by-step. Match the existing UI design patterns and follow the API contracts.
   - After completing each task, check it off in the plan document and update `.agent/STATUS.md`.
   - Add newly implemented features to `.agent/TESTING.md`.

2. **Step 2: Fix (If necessary)**
   - If you encounter implementation errors, styling issues, or regressions, immediately switch to the **Fix** phase.
   - Surgically repair the bug without rewriting unrelated components.
   - Resume the **Build** phase once resolved.

## Code Writing Policy
**ALLOWED.** You are expected to write, modify, and execute frontend application code, as well as update tracking Markdown files.