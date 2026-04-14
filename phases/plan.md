---
name: plan
description: Adopt the plan phase
---
# Phase: Plan

Purpose: Break a design into an ordered, implementable task list.

## Primary Roles
- Principal Backend Engineer
- Principal Frontend Engineer
- ML Engineer

## Inputs
- Design doc(s) from the design phase
- .agent/ARCHITECTURE.md for current structure + API contracts
- .agent/STATUS.md for what's currently in progress

## Process
1. Read the full design spec
2. Identify every piece of work needed to implement it
3. Order tasks by dependency (what blocks what)
4. For each task, specify:
   - What files need to change or be created
   - What the change actually is (specific, not vague)
   - Estimated complexity: trivial / moderate / complex
   - Dependencies on other tasks
5. Identify what can be parallelized (separate worktrees)
6. Identify the first task that produces something testable

## Parallelization Rules for Worktrees
When planning tasks for parallel worktrees:
- Each worktree task must list its branch dependencies explicitly
- Before starting work in a worktree, the agent MUST merge the
  dependency branch into the worktree:
  `cd worktree-dir && git merge feat/{dependency-branch}`
- Frontend tasks that depend on backend API contracts should build
  against the typed contracts from ARCHITECTURE.md. Use stub/mock
  data matching the contract shapes until the real backend is merged.
- After completing work in a worktree, merge back to the feature
  branch before dependent worktrees begin

### Resource Isolation
When parallel worktrees will run simultaneously:
- Assign distinct local ports (e.g., backend worktree on :3000,
  frontend worktree on :3001). Document this in the plan.
- If a database schema change is in progress, the backend worktree
  owns the database. The frontend worktree MUST use stub data or
  a separate database instance - never share a DB during migrations.
- Run dependency installs (npm install, pip install, etc.) in each
  worktree after checkout. Worktrees share the git repo but can
  have stale node_modules or lockfile mismatches.

### Integration Task (Required When Stubs Are Used)
If the frontend plan includes tasks that build against API contract
stubs (// TODO: remove stub data), the plan MUST include a final
integration task that:
- Depends on: the backend branch being merged
- Removes all // TODO: remove stub data comments and stub data
- Wires up real API calls to the actual endpoints
- Verifies the integration works end-to-end
This task is not optional. LLMs will not proactively clean up TODOs
unless explicitly planned.

### State Isolation (Critical)
When parallel worktrees are active, agents MUST NOT write to the
same global files simultaneously. Follow these rules:
- **STATUS.md**: only the primary/sequential agent updates it.
  Parallel agents track progress in their own plan doc
  (docs/plans/YYYY-MM-DD-{role}-{feature}.md) via task checkboxes.
- **TESTING.md**: parallel agents write to temporary files
  (.agent/TESTING-{backend|frontend|ml}.md). These are
  merged into the global TESTING.md when branches are unified.
- The merge of temporary state files into global files happens
  when worktree branches are merged back to the feature branch.

## Output
Write to docs/plans/YYYY-MM-DD-{role}-{feature}.md (Replace `{role}` with your current role name in lowercase, e.g., `principal-backend-engineer`):

### Overview
One line: what we're implementing

### Task Breakdown
Ordered list:
1. **[Task name]** - [specific description]
   - Files: [paths]
   - Depends on: [nothing / task N / backend task N]
   - Branch dependency: [none / feat/{branch} must be merged first]
   - Complexity: [trivial / moderate / complex]

### Parallelization Opportunities
Which tasks can run in separate worktrees simultaneously.
Include explicit merge-order instructions.

### First Testable Milestone
The earliest point where we can verify something works
end-to-end, even if incomplete

### Unknowns
Things that might change the plan once implementation starts

## Context Pointers
After creating the plan, update STATUS.md with a "Relevant Files"
section listing only the files the build agent needs for the
current task. Example:

> ## Relevant Files for Current Task
> - src/app/actions/interactions.ts (create this)
> - src/lib/schemas/interaction.ts (create this)
> - prisma/schema.prisma (modify - add Interaction model)
> - .agent/STYLE.md (code conventions)

This prevents the build agent from reading the entire .agent/
directory when it only needs one or two files.

## Files Updated
| File | Change |
|------|--------|
| docs/plans/YYYY-MM-DD-{role}-{feature}.md | Created |
| .agent/STATUS.md | Updated with plan ref, current task, relevant file pointers |

## Transition
Done when an engineer can pick up task 1 and start building without
needing to ask "what should I do first?"