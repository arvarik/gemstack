---
name: build
description: Adopt the build phase
---
# Phase: Build

Purpose: Write the code.

## Primary Roles
- Principal Backend Engineer
- Principal Frontend Engineer
- ML Engineer

## Inputs
- Plan doc from the plan phase
- .agent/STATUS.md for which task to pick up next
  (read "Relevant Files" section first - only read the files listed
  there, not the entire .agent/ directory)
- API contracts in .agent/ARCHITECTURE.md (for frontend
  building against backend contracts)

## Process
1. Read STATUS.md - check the "Relevant Files" section
2. Read only the files listed as relevant, plus the plan doc
3. Identify your current task from the plan
4. Implement the task following existing patterns
5. After completing each task:
   - Mark it done in the plan doc
   - Update STATUS.md with current state and update "Relevant Files"
     for the next task
   - Add test scenarios to TESTING.md for what you built
   - If something deviated from the plan, note why

## Rules
- Implement what the plan says. If the plan is wrong, update
  the plan first, then implement the updated version. Don't
  silently deviate.
- One task at a time. Finish and verify before starting the next.
- Don't refactor unrelated code. Don't add features not in the plan.
- If you hit an unknown from the plan phase, document it in
  STATUS.md and stop. Don't guess your way through.
- Yield on blockers: if you reach a task that depends on another
  branch being merged (e.g., the Integration Task that removes
  stubs), check if that branch exists locally (git branch --list
  feat/{dependency}). If it is NOT merged, STOP. Mark the task
  as BLOCKED in your plan doc and inform the human you are yielding
  until the dependency is ready. Do NOT hallucinate the merge,
  mock the dependency, or skip ahead.

## Worktree Rules
If building in a git worktree:
- Before starting, check that all branch dependencies from the
  plan are merged into your worktree
- If the plan says "Depends on: Backend Task 1" and that task is
  in another branch, run: git merge feat/{that-branch}
- Run dependency installs after checkout/merge (npm install, pip
  install, etc.) to avoid stale dependency states
- After completing your tasks, commit and push your branch so
  dependent worktrees can merge your changes

## State Isolation (Parallel Worktrees)
If you are building in a parallel worktree alongside other agents:
- Do NOT update .agent/STATUS.md - it is owned by the
  primary agent or will be updated after branch merge
- Track your task progress exclusively in your plan doc
  (docs/plans/{feature}-{type}.md) via task checkboxes
- Maintain your own "Relevant Files for Current Task" list at the
  top of your plan doc, since you cannot read/write STATUS.md:
  ```
  ## Relevant Files (live tracking)
  Task 2: src/components/interactions/log-form.tsx (create),
  src/lib/schemas/interaction.ts (read), .agent/STYLE.md
  ```
- Write new test scenarios to a temporary file:
  .agent/TESTING-{your-type}.md (e.g., TESTING-frontend.md)
  These will be merged into the global TESTING.md before the test phase
- Respect resource boundaries from the plan: use your assigned port,
  don't touch the database if another worktree owns it

## Frontend Building Against Contracts
When backend isn't ready yet but API contracts exist in
ARCHITECTURE.md:
- Build components using the exact types from the contracts
- Use hardcoded stub data matching the contract response shapes
- Wire up the actual API calls with the real endpoints
- Add a // TODO: remove stub data comment where stubs are used
- When backend merges, removing stubs is a trivial task

## Output
- Working code committed to the branch
- Updated plan doc with completed task checkboxes
- Updated state tracking files (depends on sequential vs parallel - see table)

## Files Updated

### If sequential (single agent, no parallel worktrees):
| File | Change |
|------|--------|
| (source code files) | Created / modified per plan |
| docs/plans/{feature}-{type}.md | Task checkboxes updated |
| .agent/STATUS.md | Progress + relevant files for next task |
| .agent/TESTING.md | New scenarios added (status: UNTESTED) |

### If in a parallel worktree:
| File | Change |
|------|--------|
| (source code files) | Created / modified per plan |
| docs/plans/{feature}-{type}.md | Task checkboxes updated + Relevant Files tracked here |
| .agent/TESTING-{type}.md | New scenarios added (temporary file, merged before test phase) |
| .agent/STATUS.md | DO NOT TOUCH - owned by primary agent |
| .agent/TESTING.md | DO NOT TOUCH - use TESTING-{type}.md instead |

## Transition
A task is done when the code works for the happy path locally.
It does NOT need to be fully tested yet - that's the test phase.
Move to test after completing a testable milestone from the plan.