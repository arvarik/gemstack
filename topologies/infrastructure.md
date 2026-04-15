---
name: infrastructure
description: Infrastructure topology guardrails — YAML validation, service safety, deployment discipline
---
# Topology: Infrastructure

**Core Focus:** Configuration Integrity and Service Safety.

**When this topology applies:** Docker Compose stacks, Terraform/Pulumi repos, Kubernetes manifests, NAS configurations, CI/CD pipeline definitions, or any project where the "code" is primarily YAML/HCL/TOML configuration.

_This profile is a behavioral modifier. It does not replace any role or workflow — it adds domain-specific constraints on top of whatever workflow the agent is currently executing. Read this profile when the project's `ARCHITECTURE.md` declares `infrastructure` in its Topology field._

---

## Guardrail 1: Configuration Validation

Before any deployment or PR, agents must validate configuration syntax. Validation commands vary by tool:

| Tool | Validation Command | Expected Result |
|------|--------------------|-----------------|
| Docker Compose | `docker compose config --quiet` | Exit code 0 |
| Kubernetes | `kubectl apply --dry-run=client -f <file>` | No errors per manifest |
| Terraform | `terraform validate` + `terraform plan` | Plan only — never auto-apply |
| GitHub Actions | `actionlint` (if installed) | Zero warnings |
| Ansible | `ansible-playbook --syntax-check <playbook>` | No syntax errors |

**Applies to:** Builder (Build phase), SDET (Trap phase — write tests that run these validations).

---

## Guardrail 2: No Auto-Apply

Agents must NEVER execute destructive infrastructure commands without human approval. The following commands are unconditionally FORBIDDEN for agents:

- `terraform apply` — agent may only `plan`.
- `docker compose down -v` — destroys volumes and data.
- `kubectl delete` — destroys resources.
- Any command that drops, truncates, or migrates a production database.
- `rm -rf` on data directories or mounted volumes.

The agent's job is to **prepare the change and present the plan**. The human applies it.

### When You Hit This Boundary

Output a SYSTEM ROUTING block:

```markdown
### SYSTEM ROUTING
[✅] PLAN READY: Terraform plan generated. 3 resources to add, 1 to modify, 0 to destroy.
🟠 NEXT ACTION: Human must run `terraform apply` after reviewing the plan output above.
```

**Applies to:** All roles, all phases.

---

## Guardrail 3: Port and Network Isolation

### Rules for the Auditor (Audit Phase)

Verify the following for every service in the stack:

- **No database ports exposed to the host network.** Database services (PostgreSQL, MySQL, Redis, InfluxDB) must communicate only via Docker internal networks. If a port mapping like `5432:5432` exists, flag it.
- **No services run with `network_mode: host`** unless explicitly justified in `ARCHITECTURE.md`.
- **Health checks defined** for all services that accept external traffic. A service without a health check can accept traffic before it's ready.

### Rules for the Builder (Build Phase)

- When adding a new service, always define it on a named Docker network — never rely on the default bridge.
- Always add a `healthcheck` block for services that accept HTTP traffic.
- Use `.env` files for port configuration — never hardcode port numbers in `docker-compose.yml`.

---

## Guardrail 4: Secret Management

### Rules for the Auditor (Audit Phase)

- No secrets (API keys, passwords, tokens) hardcoded in configuration files. All secrets must come from environment variables or a secrets manager.
- `.env` files containing real secrets must be in `.gitignore`. Check that `.env.example` exists with placeholder values.
- Docker Compose `environment:` blocks must reference `${VAR}` syntax, not literal secret values.

### Rules for the Builder (Build Phase)

- When adding a new service that requires secrets, add the variable to `.env.example` with a placeholder value and document it in `ARCHITECTURE.md`.
