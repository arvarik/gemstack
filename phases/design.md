---
name: design
description: Adopt the design phase
---
# Phase: Design

Purpose: Define what the thing should be before anyone writes code.
This phase produces TWO outputs: a UX spec and an architecture spec
with API contracts that enable parallel frontend/backend work.

## Primary Roles
- UI/UX Designer (user flows, screen layouts, interaction patterns)
- Architect (system boundaries, data flow, API contracts)
- ML Engineer (model selection, pipeline design, performance targets)

## Inputs
- Recommendation from the ideate phase
- .agent/ARCHITECTURE.md for existing system context
- .agent/STYLE.md for existing visual/code patterns
- .agent/PHILOSOPHY.md for product soul and tone

## Process

### If UI/UX Designer:
1. Define the user journey end-to-end for this feature
2. Specify every screen/view: layout, hierarchy, content
3. Specify every interaction: what triggers what
4. Specify every state: empty, loading, partial, success, error
5. Note where existing patterns apply vs where new patterns are needed

### If Architect:
1. Map how this feature connects to existing system components
2. Define data models and their relationships
3. **Define exact API contracts** - this is critical:
   - Endpoint paths and HTTP methods
   - Request body shapes with types
   - Response body shapes with types
   - Error response shapes
   - Validation rules
   These contracts go into ARCHITECTURE.md and are the source of truth
   that both backend and frontend engineers build against independently.
4. Identify what existing code needs to change vs what's new
5. Flag any concerns about complexity or coherence

### If ML Engineer:
1. Define input/output specifications for the pipeline
2. Select model(s) with justification (quality vs cost vs speed)
3. Define performance targets (latency, accuracy, memory)
4. Design preprocessing and postprocessing steps
5. Identify hardware requirements

## Output
Write to docs/designs/YYYY-MM-DD-{feature}-{ux|architecture|ml}.md:

### What We're Building
One paragraph, non-technical summary

### Design Specification
(Role-specific sections as described above)

### Dependencies
What this feature requires that doesn't exist yet

### Risks
What could go wrong and how we'd mitigate it

### Out of Scope
Explicitly what this feature does NOT include

## Files Updated
| File | Change |
|------|--------|
| docs/designs/YYYY-MM-DD-{feature}-{type}.md | Created |
| .agent/ARCHITECTURE.md | Updated with API contracts (Architect only) |
| .agent/STATUS.md | Updated phase progress |

## Transition
This phase is done when:
- UX spec is specific enough that a frontend engineer doesn't need to
  make product decisions
- Architecture spec contains exact API contracts that frontend and
  backend can build against independently
- Human has approved both specs

Hand design docs to the plan phase.