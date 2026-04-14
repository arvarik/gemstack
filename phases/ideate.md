---
name: ideate
description: Adopt the ideate phase
---
# Phase: Ideate

Purpose: Generate and prioritize what to build next.

## Primary Roles
- Product Visionary (what do users need?)
- UI/UX Designer (what existing UX problems need solving?)
- Engineers (what technical debt or opportunities exist?)

## Inputs
- .agent/STATUS.md for current project state
- .agent/ARCHITECTURE.md for what exists today
- .agent/PHILOSOPHY.md for product principles
- docs/explorations/ for past explorations (to avoid retreading)
  NOTE: only read file names and headers, not full content,
  to conserve tokens

## Process
1. Survey the current state of the project
2. Identify gaps, pain points, and opportunities
3. Generate ideas without filtering for feasibility
4. Prioritize by: frequency of pain x severity of pain
5. Select top 1-3 items to move forward

## Output
Write to docs/explorations/YYYY-MM-DD-{topic}.md:

### Context
What prompted this exploration

### Ideas Considered
For each idea:
- **The pain**: what sucks without this
- **The opportunity**: what gets better with this
- **Rough size**: small / medium / large
- **Priority**: must-have / should-have / nice-to-have

### Recommendation
Top 1-2 items to move to the design phase and why.
Reference PHILOSOPHY.md to justify alignment.

### Open Questions
Decisions that need human input before proceeding

## Files Updated
| File | Change |
|------|--------|
| docs/explorations/YYYY-MM-DD-{topic}.md | Created |
| .agent/STATUS.md | Updated current focus |

## Transition
Done when you have a clear recommendation with user approval.
Hand the recommendation to the design phase.

## What This Phase Is NOT
- Not technical planning (that's the plan phase)
- Not UI mockup creation (that's the design phase)
- Not implementation (that's the build phase)