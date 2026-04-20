# Topology-Aware Guardrails

Instead of prompting every AI agent with the same generic instructions regardless of project type, Gemstack detects your project's **topology** and dynamically loads domain-specific guardrails. A Next.js frontend gets different rules than a Go microservice, which gets different rules than a Python ML pipeline.

---

## What Are Topologies?

A topology is a declaration of what *kind* of software your project is. You declare one or more topologies in the `## 0. Project Topology` section of your `.agent/ARCHITECTURE.md`:

```markdown
**Topology:** [frontend, backend]
```

When Gemstack compiles context (via `gemstack compile` or `gemstack run`), it reads this declaration and injects the corresponding guardrail documents into the AI's prompt. Multiple topologies can be combined — a full-stack app with AI features would declare `[frontend, backend, ml-ai]`, and all three guardrail sets would be applied simultaneously.

### Auto-Detection

During `gemstack init`, the **Project Detector** automatically infers your topology from your dependencies and project structure:

| Signal | Inferred Topology |
|--------|------------------|
| `react`, `next`, `vue`, `svelte`, `vite` in `package.json` | `frontend` |
| `express`, `fastify`, `hono`, `nestjs` in `package.json` | `backend` |
| `fastapi`, `flask`, `django` in `pyproject.toml` | `backend` |
| `go-chi`, `gin`, `fiber` in `go.mod` | `backend` |
| `torch`, `transformers`, `openai`, `langchain` in deps | `ml-ai` |
| `docker-compose.yml`, `*.tf`, `k8s/` without app code | `infrastructure` |
| `pkg/` directory without `cmd/` in Go projects | `library-sdk` |

You can override the auto-detection with an explicit flag:

```bash
gemstack init --topology "frontend,backend,ml-ai"
```

---

## The 5 + 1 Topology Profiles

### Backend

**For:** REST/GraphQL APIs, microservices, CLIs with server-side logic.

Key guardrails enforced:

| Category | Rule |
|----------|------|
| **Data Integrity** | Every mutation (INSERT/UPDATE/DELETE) must have a corresponding test that verifies the database state before and after |
| **Anti-Mocking Discipline** | Integration tests must hit real dependencies (databases, queues). Mocks are only permitted for external third-party APIs. Never mock your own code |
| **N+1 Prevention** | ORM queries in loops are flagged. Use eager loading, joins, or batch queries |
| **Deterministic Testing** | Tests must not depend on wall-clock time, random values, or external network. Use deterministic seeds, frozen time, and test databases |
| **Transaction Boundaries** | Every write operation must define explicit transaction boundaries. No implicit auto-commit |

### Frontend

**For:** SPAs, SSR/SSG apps, component libraries, design systems.

Key guardrails enforced:

| Category | Rule |
|----------|------|
| **Component State Matrix** | Every UI component must handle 5 states: **empty**, **loading**, **success**, **error**, and **partial** data. Missing states are flagged |
| **Hydration Safety** | Code that accesses `window`, `document`, or `localStorage` must be wrapped in client-only guards. Server/client boundary violations are flagged |
| **Accessibility** | Interactive elements must have labels, focus management, and keyboard navigation. ARIA attributes must match semantic HTML |
| **No Raw Fetch Loops** | Data fetching must go through the project's established data layer (React Query, SWR, server actions, etc.). Raw `useEffect` + `fetch` patterns are forbidden |
| **Visual Regression** | UI changes must include screenshot or snapshot tests to prevent unintended visual drift |

### ML/AI

**For:** LLM applications, ML pipelines, RAG systems, fine-tuning workflows.

Key guardrails enforced:

| Category | Rule |
|----------|------|
| **Evaluation-Driven Development** | Every prompt change must be validated against a held-out evaluation set. No "it looks right" deployments |
| **Cost Circuit Breaker** | Every model call must have a cost ceiling. The circuit breaker halts execution if cumulative costs exceed the per-feature budget (tracked in `.agent/costs.json`) |
| **Prompt Versioning** | All prompt templates are versioned. Changes are tracked in the Prompt Versioning Changelog (in `STATUS.md`). Rollback to any previous version must be trivial |
| **Eval/Holdout Boundary** | Evaluation data must be strictly separated from training/fine-tuning data. Cross-contamination is a blocking issue |
| **Model Ledger** | Every model in use must be documented in the Model Ledger (in `ARCHITECTURE.md`) with costs, context window, rate limits, and circuit breaker caps |

### Infrastructure

**For:** Docker Compose stacks, Kubernetes manifests, Terraform configs, homelab documentation.

Key guardrails enforced:

| Category | Rule |
|----------|------|
| **YAML Validation** | All YAML files must be syntactically valid and pass schema validation before apply |
| **No-Auto-Apply** | `terraform apply`, `kubectl apply`, and `docker compose up` must never run without explicit plan/diff review first |
| **Port Isolation** | Every service must have explicitly documented port mappings. Port conflicts across services are flagged |
| **Configuration Drift Detection** | Running state must be compared against declared state. Drift is reported as a blocking issue |
| **Secret Management** | Secrets must never appear in YAML files, env vars in compose files, or Terraform state. Use external secret managers or encrypted references |

### Library/SDK

**For:** Packages published to npm, PyPI, crates.io, or Go modules.

Key guardrails enforced:

| Category | Rule |
|----------|------|
| **API Surface Stability** | Public API changes are detected via snapshot diffing. Any change to exported types, functions, or constants requires explicit acknowledgment |
| **Backward Compatibility** | Removing or renaming public APIs is a semver-major change. Adding new APIs is semver-minor. Bug fixes are semver-patch |
| **Semver Enforcement** | Version bumps must match the scope of changes. A breaking change with a minor version bump is flagged as a blocking error |
| **Documentation Coverage** | Every exported symbol must have a docstring. New public APIs without documentation are flagged |
| **Dependency Minimalism** | New runtime dependencies must be justified. Unnecessary transitive dependencies bloat consumer install sizes |

### LLM Failure Modes (Cross-Cutting Reference)

In addition to the 5 topology profiles, Gemstack bundles a comprehensive **LLM Failure Modes** reference document (~10K tokens) that catalogues known failure patterns across all AI coding agents:

- Hallucination patterns (confident fabrication, API drift, phantom dependencies)
- Sycophantic and yes-man behavior
- Context window degradation
- Premature optimization and over-engineering
- Silent test mutation (changing tests to match broken code)
- And many more

This reference is available to all topology guardrails and can be injected into any workflow step via the plugin system.

---

## Migrating Existing Projects

If you initialized a Gemstack project before topology support was added, run:

```bash
gemstack migrate
```

This will:
1. Detect your project's topology from its dependencies
2. Add the `**Topology:** [...]` declaration to your `ARCHITECTURE.md`
3. Insert topology-specific coverage matrices into `TESTING.md`
4. Add the Stub Audit Tracker and (if applicable) Prompt Versioning Changelog to `STATUS.md`

---

## Custom Topologies via Plugins

If your project type isn't covered by the built-in topologies (e.g., mobile, embedded, game development), you can register custom topologies via the [plugin system](plugins.md):

```python
from gemstack.plugins.hooks import hookimpl

class MobilePlugin:
    @hookimpl
    def gemstack_register_topologies(self):
        return [{
            "name": "mobile",
            "description": "iOS and Android native development",
            "content": "# Mobile Topology Guardrails\n\n..."
        }]
```

Once registered, declare it in `ARCHITECTURE.md`:

```markdown
**Topology:** [mobile, backend]
```

The compiler will load your custom guardrails alongside the built-in ones.
