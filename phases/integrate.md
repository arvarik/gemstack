---
name: integrate
description: Adopt the integrate phase
---
# Phase: Integrate

Purpose: Wire the real systems together and remove all stubs/mocks.

## Primary Roles
- Principal Backend Engineer
- Principal Frontend Engineer

## Inputs
- Completed Frontend Code (with stubs)
- Completed Backend Code
- Executable Contracts

## Process
1. Search the entire codebase for `// TODO: remove stub` or `// TODO: remove mock` comments.
2. Carefully strip out all mock data, stub responses, and mocked API handlers.
3. Wire the frontend directly to the real backend endpoints.
4. Verify the integration works end-to-end by running the full integrated test suite.
5. If the integration fails, debug the boundaries. Since both sides were built to the same Executable Contract, integration bugs are usually configuration or routing issues.

## Rules
- You are strictly tasked with removal and wiring. Do not add new features in this phase.
- LLMs are notoriously bad at remembering to remove stubs. You must be exhaustive in your search.

## Transition
Done when all stubs are removed, real endpoints are wired, and the integrated application starts and passes basic end-to-end verification.