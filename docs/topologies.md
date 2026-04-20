# Topology-Aware Guardrails

Instead of using the exact same generic prompts for a static website vs a complex machine-learning pipeline, Gemstack detects your project's **Topology**. 

A Next.js app with a Go backend is detected as `[frontend, backend]`. A Python API heavily reliant on a RAG pipeline is detected as `[backend, ml-ai]`. 

Guardrails are loaded dynamically based on your topology declaration in `ARCHITECTURE.md`.

| Topology | Key Guardrails Enforced |
|----------|---------------|
| **Backend** | Data integrity testing, anti-mocking rules, N+1 query detection, deterministic test discipline |
| **Frontend** | Component state coverage matrix (empty/loading/success/error/partial), hydration safety, accessibility |
| **ML/AI** | Evaluation-Driven Development, circuit breaker for cost control, prompt versioning, eval/holdout boundary |
| **Infrastructure** | YAML validation, no-auto-apply policy, port isolation, configuration drift detection |
| **Library/SDK** | API surface stability via snapshot diffing, backward compatibility, semver enforcement |

To migrate an older Gemstack repository to use Topologies, run:
```bash
gemstack migrate
```
