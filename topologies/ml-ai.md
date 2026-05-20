---
name: ml-ai
description: ML/AI topology guardrails — Evaluation-Driven Development and cost control
---
# Topology: ML / AI

<thinking_process>
The ML/AI topology focuses on "Evaluation" and "Safety." Think about:
1. Probabilistic vs. Deterministic testing.
2. API cost management.
3. Prompt versioning and eval-tracking.
</thinking_process>

<guardrails>
## Guardrail 1: The AI Testing Pyramid
### Layer 1: Deterministic Scaffolding (SDET)
Test the non-AI code with mocked LLM responses. Focus on prompt rendering, parsing, and error handling.
### Layer 2: Constrained Model Tests (SDET)
Real model calls with minimal inputs to verify structural compliance (JSON schema, tool-calling).
### Layer 3: Evaluation Thresholds (ML Engineer)
Measure output quality against an eval dataset using metrics (ROUGE-L, Cosine Similarity, or LLM-as-a-judge).

## Guardrail 2: The Circuit Breaker
Agents must halt and yield if:
- Consecutive attempts without improvement > 5.
- Session API cost exceeds the "Cost Cap" defined in `ARCHITECTURE.md`.
- Latency p95 > threshold.

## Guardrail 3: Prompt Externalization
Prompts MUST be stored in `/prompts/*.txt` or similar. Inline prompt strings are FORBIDDEN.

## Guardrail 4: Context Protection
Never dump large datasets or raw model responses to stdout. Use summary statistics (`.info()`, `.describe()`).
</guardrails>

<reporting>
### Model Ledger (in ARCHITECTURE.md)
The Architect must populate this:

| Model | Role | Cost Cap | Context | JSON Mode |
|-------|------|----------|---------|-----------|
| ...   | ...  | ...      | ...     | ...       |
</reporting>
