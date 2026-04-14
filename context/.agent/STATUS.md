# {Project Name} Status
Last updated: YYYY-MM-DD

_This file tracks the detailed explore/plan/build/test sub-phases per feature. It is the single source of truth for "where am I?" Agents should update this file after completing tasks or making progress._

## Current Focus
_One-sentence description of the active feature or bug fix phase._
Example: Reconnect Reminders - backend complete, frontend build next

## State of Work
_List the lifecycle phases for the current feature and check them off as you progress._
- [ ] Ideate: `docs/explorations/...`
- [ ] Design (UX/Arch): `docs/designs/...`
- [ ] Plan (BE/FE): `docs/plans/...`
- [ ] Build
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

## What's Next
_What feature or task should be picked up after the current focus is complete? Reference the exploration doc recommendation._

## Relevant Files for Current Task
_List ONLY the files the agent needs to read or modify for the immediate next task. This prevents agents from wasting tokens reading the entire project context._
- `src/components/...` (modify)
- `src/lib/...` (read-only)
- `docs/designs/...` (spec)