---
name: llm-failure-modes
description: Guardrails for common AI agent failure modes — hallucination, drift, and scope creep
---
# Topology: LLM Failure Modes

<thinking_process>
This topology targets the specific weaknesses of AI agents. Think about:
1. Hallucination (inventing APIs or files).
2. Logic Drift (losing track of the contract).
3. Scope Creep (unnecessary refactoring).
</thinking_process>

<guardrails>
## Guardrail 1: Hallucination Protection
- **Rule**: If you are unsure if an API or file exists, you MUST run `ls` or check documentation before using it.
- **Rule**: Never "placeholder" a complex logic block with a comment like `// implement logic here`. Implement it or yield.

## Guardrail 2: Logic Drift Prevention
- **Rule**: Every 5 turns, or after a major task completion, re-read the `ARCHITECTURE.md` and `IMPLEMENTATION_PLAN.md` to re-align with the truth.
- **Rule**: Follow the **Mutex Lock** in `task.md`. If the phase doesn't match, stop.

## Guardrail 3: Scope Creep Mitigation
- **Rule**: Only modify files related to the current task in `task.md`.
- **Rule**: `git diff --stat` should not show changes in unrelated modules. If refactoring is needed, create a separate task for it.

## Guardrail 4: Silent Swallow Prevention
- **Rule**: Never wrap code in empty `try/catch` blocks. All errors must be logged or propagated.
- **Rule**: Tests must verify error handling paths.

## Guardrail 5: Context Window Protection
- **Rule**: Use summary tools (`head`, `grep`, `describe()`) instead of printing large datasets to the terminal.
</guardrails>
