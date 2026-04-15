---
name: ml-ai
description: ML/AI topology guardrails — Evaluation-Driven Development, cost control, prompt versioning
---
# Topology: ML / AI

**Core Focus:** Evaluation-Driven Development (EDD) and Cost Control.

**When this topology applies:** Projects that use LLM APIs (Gemini, Claude, OpenAI), run ML inference, train models, operate RAG pipelines, or have any component with probabilistic/non-deterministic outputs.

_This profile is a behavioral modifier. It does not replace any role or workflow — it adds domain-specific constraints on top of whatever workflow the agent is currently executing. Read this profile when the project's `ARCHITECTURE.md` declares `ml-ai` in its Topology field._

---

## Guardrail 1: The AI Agent Testing Pyramid

Standard TDD (assert exact output matches expected output) does not work for probabilistic systems. Instead, testing follows a layered pyramid. Each layer has a dedicated owner and phase.

### Layer 1 — Deterministic Scaffolding Tests

**Owner:** SDET | **Phase:** Trap

Test the non-AI code with mocked LLM responses. This includes:

- **Prompt construction:** Does the template render correctly with variables?
- **Input sanitization:** Are user inputs cleaned before injection into prompts?
- **Response parsing:** Does the JSON parser handle malformed LLM output?
- **Error handling:** What happens when the API times out or returns garbage?
- **Rate limiting logic:** Are rate limits enforced before API calls?
- **Cost tracking arithmetic:** Are token counts and cost calculations correct?

These tests are fast, cheap, deterministic, and catch the majority of bugs. Write them like normal unit tests with mocked API responses.

### Layer 2 — Constrained Model Tests

**Owner:** SDET | **Phase:** Trap

Validate that the model respects structural constraints:

- Does it output valid JSON when asked for JSON?
- Does it respect length limits?
- Does it use the correct tool/function when tool-calling is configured?

These tests call the real model but with controlled, minimal inputs. They are more expensive than Layer 1 but still deterministic in their pass/fail criteria.

### Layer 3 — Evaluation Thresholds

**Owner:** ML Engineer | **Phase:** Build

Measure output quality against a curated eval dataset using domain-specific metrics. Populate this table in the project's `TESTING.md`:

```markdown
## ML / AI Evaluation Thresholds

| Metric | Target | Current | Method | Eval Set | Last Run |
|--------|--------|---------|--------|----------|----------|
| ROUGE-L (summary quality) | > 0.85 | — | deepeval | eval/summary_gold.json | — |
| Tool Selection Accuracy | > 0.90 | — | exact match | eval/tool_calls.json | — |
| JSON Schema Compliance | 1.00 | — | schema validation | eval/structured_output.json | — |
| Latency p95 | < 3s | — | timer | (all eval sets) | — |
```

### Layer 4 — Human-in-the-Loop

**Owner:** Human | **Phase:** Release Gatekeeper workflow

Reserved for subjective quality assessment and holdout set evaluation. The agent cannot perform this layer. It is triggered by the Release Gatekeeper workflow.

---

## Guardrail 2: Multi-Variable Circuit Breaker

Agents must halt execution and yield to the human if ANY of the following conditions are met during the Build phase. This prevents infinite retry loops, cost exhaustion, and diminishing-returns spirals.

| Trigger | Threshold | Rationale |
|---------|-----------|-----------|
| Consecutive attempts without metric improvement | 5 | Prevents infinite retry loops |
| Total session API cost | Defined in Model Ledger (`ARCHITECTURE.md`) | Prevents cost exhaustion |
| Per-attempt improvement rate | < 2% for 3 consecutive attempts | Diminishing returns detection |
| Total wall-clock time in tuning loop | 30 minutes | Prevents runaway sessions |

### When the Circuit Breaker Trips

The agent must immediately stop and output:

```markdown
### SYSTEM ROUTING
[🛑] CIRCUIT BREAKER TRIPPED: [Which trigger fired and current values]
[📊] PROGRESS SO FAR: [Best metric achieved, number of attempts, total cost]
[🔄] NEXT ACTION: Human review required. Consider: adjusting the eval threshold, changing the model, or restructuring the prompt.
```

**Applies to:** ML Engineer (Build phase), Builder (Build phase).

---

## Guardrail 3: Prompt Versioning

All LLM prompts must be externalized to a `/prompts` directory (or equivalent location documented in `ARCHITECTURE.md`). Inline prompt strings scattered across the codebase are FORBIDDEN.

### Rules for the Builder and ML Engineer (Build Phase)

- Every prompt change must be logged in the **Prompt Versioning Changelog** in `STATUS.md`.
- After every prompt change: re-run evals, record the delta in the changelog.
- If eval scores degrade after a prompt change, rollback to the previous version immediately.

### Prompt Versioning Changelog Format

```markdown
## Prompt Versioning Changelog (ML/AI)

| Version | Date | Change Description | Eval Score | Delta | File |
|---------|------|--------------------|------------|-------|------|
| v1.1 | 2026-04-14 | Added JSON schema directive | 81% | +19% | prompts/extraction_v1.1.txt |
| v1.0 | 2026-04-13 | Baseline extraction prompt | 62% | — | prompts/extraction_v1.0.txt |
```

This enables: diffing between versions, correlating prompt changes with eval score changes, and rollback when scores degrade.

---

## Guardrail 4: Context Window Protection

LLM agents can blow out their own context window by dumping large payloads to the terminal. Once this happens, the agent loses track of earlier instructions and quality degrades rapidly.

### Rules for All Roles (All Phases)

Agents must NEVER:
- Run `print(df)` or log raw dataset payloads to the terminal.
- Dump entire model responses to stdout without truncation.
- Load full datasets into the conversation context.

Instead:
- Use `.info()`, `.describe()`, `.head(5)`, or summary statistics.
- If you need to inspect data, write it to a temporary file and read specific lines.
- Truncate model responses before logging: show the first 200 characters + total length.

---

## Guardrail 5: The Holdout Rule

If the project uses eval datasets, the agent is restricted to the `eval_set` during development. The `holdout_set` (if it exists) is reserved for **human-run evaluation only**.

This is a hard boundary — the agent has filesystem access and could trivially overfit to holdout data if allowed to read it.

### Documentation Required in TESTING.md

```markdown
## Eval / Holdout Boundary
- **eval_set**: `eval/` directory — Agent may read and optimize against these.
- **holdout_set**: `eval/holdout/` directory — HUMAN-ONLY. Agent must never reference these files.
```

**Applies to:** All roles, all phases.

---

## Reporting: Model Ledger (in ARCHITECTURE.md)

The Architect must populate this table in `ARCHITECTURE.md` for every LLM/ML model the project uses. The Circuit Breaker reads Cost Cap values from this ledger.

```markdown
## Model Ledger (ML/AI Topology)

| Model | Role | Cost (1M input / 1M output) | Context Window | JSON Mode | Rate Limit | Circuit Breaker Cost Cap |
|-------|------|----------------------------|----------------|-----------|------------|--------------------------|
| gemini-2.5-pro | Primary reasoning | $1.25 / $10.00 | 1M tokens | Yes | 5 RPM | $5.00/session |
| gemini-2.5-flash | Extraction/fallback | $0.15 / $0.60 | 1M tokens | Yes | 15 RPM | $2.00/session |
```
