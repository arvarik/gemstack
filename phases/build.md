---
name: build
description: Adopt the build phase
---
# Phase: Build

Purpose: The Autonomous Factory. Write the code and pass the mathematical trap.

## Primary Roles
- Principal Backend Engineer
- Principal Frontend Engineer
- ML Engineer

## Inputs
- Plan doc
- Executable Contracts (types, schemas)
- Failing Test Suite (written by SDET)
- .agent/STATUS.md

## Process
1. Identify your current task from the plan.
2. Implement the task following existing patterns and strict contracts.
3. **CRUCIAL RULE: The Terminal is the Referee.**
   - Run the test suite in the Antigravity terminal.
   - **You are locked in this phase until the terminal outputs Exit Code 0.**
   - Do not ask the human for help if tests fail. Read `stderr`, fix the application code, and retry autonomously.
4. After passing the test suite:
   - Mark the task done in the plan doc.
   - Update `STATUS.md` with current state.

## Rules
- **No Hallucinations:** Build exactly to the executable contracts.
- **No Logic Drift:** Do not hardcode the "happy path" just to pass the tests. Write robust logic that handles edge cases the SDET may have laid out.
- **Autonomy:** You must loop the test execution and fixing process entirely on your own until the terminal exits cleanly with `0`.

## Transition
A task is done ONLY when the terminal outputs Exit Code 0 for the SDET's test suite, proving the code fulfills the mathematical contract.