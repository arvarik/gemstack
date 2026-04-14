---
name: implement-backend
description: Run the backend implementation workflow
---
# Workflow: Implement Backend

**Goal:** Read the backend plan, write the code, and fix any localized bugs as they arise.

## Composition
This workflow composes:
- **Roles:** `Principal Backend Engineer`
- **Phases:** `Build`, `Fix`

## Process

1. **Step 1: Build**
   - Act as the **Principal Backend Engineer**. Read your assigned tasks from the backend plan in `docs/plans/`.
   - Implement the tasks step-by-step.
   - After completing each task, check it off in the plan document and update `.agent/STATUS.md`.
   - Add newly implemented features to `.agent/TESTING.md`.

2. **Step 2: Fix (If necessary)**
   - If you encounter implementation errors, blockers, or regressions, immediately switch to the **Fix** phase.
   - Surgically repair the bug without rewriting unrelated architectural components.
   - Resume the **Build** phase once resolved.

## Code Writing Policy
**ALLOWED.** You are expected to write, modify, and execute backend application code, as well as update tracking Markdown files.