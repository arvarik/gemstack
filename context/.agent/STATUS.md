# {Project Name} Status
Last updated: YYYY-MM-DD

_This file tracks the detailed explore/plan/build/test sub-phases per feature. It is the single source of truth for "where am I?" Agents should update this file after completing tasks or making progress._

## Current Focus
_One-sentence description of the active feature or bug fix phase._
Example: Reconnect Reminders - backend complete, frontend build next

## Current Milestone Tracking
_How does the current focus map to broader goals (Sprint, Quarter, Release)?_
- **Target**: e.g., "v1.2 Launch (End of Q3)"
- **Progress**: "4 of 7 features merged, currently working on [Feature X] downstream."

## State of Work
_List the lifecycle phases for the current feature and check them off as you progress. Remove lines that don't apply (e.g., if no frontend, delete the Frontend lines; if no ML, delete the ML line)._
- [ ] Ideate: `docs/explorations/YYYY-MM-DD-{topic}.md`
- [ ] Design (UX): `docs/designs/YYYY-MM-DD-{feature}-ux.md`
- [ ] Design (Architecture): `docs/designs/YYYY-MM-DD-{feature}-architecture.md`
- [ ] Design (ML): `docs/designs/YYYY-MM-DD-{feature}-ml.md`
- [ ] Plan (Backend): `docs/plans/YYYY-MM-DD-{feature}-backend.md`
- [ ] Plan (Frontend): `docs/plans/YYYY-MM-DD-{feature}-frontend.md`
- [ ] Plan (ML): `docs/plans/YYYY-MM-DD-{feature}-ml.md`
- [ ] Build (Backend)
- [ ] Build (Frontend)
- [ ] Build (ML)
- [ ] Test
- [ ] Review
- [ ] Ship

## Recently Completed
_Bullet points of features or major tasks that were recently shipped. Move items here after the "Ship" phase._
- [Feature 1] (shipped YYYY-MM-DD)
- [Feature 2]

## Known Issues
_List any persistent bugs or architectural debt that isn't blocking the current release but needs to be tracked. Do NOT list "blocks release" bugs here (those go in TESTING.md)._
- Example: OAuth token refresh occasionally fails silently
- Example: Reminder query does full scan (fine now, index later if needed)

## What's Next
_What feature or task should be picked up after the current focus is complete? Reference the exploration doc recommendation._

## Relevant Files for Current Task
_List ONLY the files the agent needs to read or modify for the immediate next task. This prevents agents from wasting tokens reading the entire project context._
- `src/components/...` (modify)
- `src/lib/...` (read-only)
- `docs/designs/...` (spec)

## Blockers & Upstream Dependencies
_List items actively preventing progress on Current Focus._
- Example: **BLOCKED** on `#PR-123` (Auth service updates).
- Example: waiting for updated Figma specs for mobile nav behavior.
- N/A — no current blockers.

## Feature Rollout State
_Track which environments have what features enabled (Feature Flags, A/B tests)._
- Example: `ENABLE_EXPERIMENTAL_DEDUPE` — Dev (ON), Staging (ON), Prod (OFF).

## Review Results
_Populated during the Review phase. Keep the most recent review here; archive older ones with shipped features._

### Review Results — YYYY-MM-DD
- **Architecture**: pass / concerns noted
- **Security**: pass / findings with severity
- **Product fit**: pass / gaps identified

### Action Items
_For each item, specify severity and routing._

| Item | Severity | Route To | Status |
|------|----------|----------|--------|
| _Example: GET /api/reminders has no auth check_ | recommended | Backend Eng (fix phase) | OPEN |
| _Example: Card max-width missing at 1440px_ | cosmetic | Frontend Eng (fix phase) | OPEN |
| _Example: Data model violates single-responsibility_ | blocks ship | Architect → plan + build | OPEN |

## Active Worktrees
_Track parallel agent work when using git worktrees. Remove entries during Ship phase cleanup._

| Worktree | Branch | Port | Status | Owner |
|----------|--------|------|--------|-------|
| _Example: ../project-feat-backend_ | `feat/reconnect-backend` | :3001 | In progress | Backend Eng |
| _Example: ../project-feat-frontend_ | `feat/reconnect-frontend` | :3002 | Blocked on BE merge | Frontend Eng |

_If no parallel worktrees are active, write "(none — sequential execution)"._