---
name: infrastructure
description: Infrastructure topology guardrails — Proxmox/LXC, Docker Compose, and resource limits
---
# Topology: Infrastructure

<thinking_process>
The Infrastructure topology focuses on "Reliability" and "Environment Parity." Think about:
1. Resource constraints in an LXC environment.
2. Network topology (Caddy reverse proxy, DNS-01 challenges).
3. Secret management.
</thinking_process>

<guardrails>
## Guardrail 1: Container Orchestration
- Use **Docker Compose** as the primary orchestration tool.
- Every container MUST have `deploy.resources.limits` (CPU and Memory) defined to prevent a single service from crashing the LXC host.

## Guardrail 2: Reverse Proxy & TLS
- All external traffic must go through **Caddy**.
- Use the **DNS-01 challenge** (Cloudflare) for wildcard certificates.
- Internal services should communicate via the Docker network using service names.

## Guardrail 3: Data Persistence
- Use named volumes or bind mounts for persistent data.
- Ensure all volumes are backed up or documented in `INFRASTRUCTURE.md`.

## Guardrail 4: Secret Management
- NEVER commit `.env` files.
- Provide a `.env.example` with all required keys but empty/dummy values.
</guardrails>

<reporting>
### Infrastructure Health Matrix
The DevOps Engineer should record this in `INFRASTRUCTURE.md`:

| Service | Container Status | Memory Limit | Backup Status |
|---------|------------------|--------------|---------------|
| ...     | ...              | ...          | ...           |
</reporting>
