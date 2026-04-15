# Example: Infrastructure Project — `[infrastructure]`

A walkthrough of the Gemstack 5-step workflow for an **infrastructure** project — e.g., a Docker Compose stack, Terraform configs, Kubernetes manifests, or CI/CD pipeline definitions.

**Topology:** `[infrastructure]`
**Active Guardrails:** `infrastructure.md` — YAML validation, no-auto-apply policy, port isolation, configuration drift detection
**Example Project:** A self-hosted Docker Compose stack running on a home server (NAS)

---

## The Feature

> "Add Uptime Kuma as a new service for monitoring the health of all other services in the stack, with Telegram notifications for downtime."

---

## Step 1: `/step1-spec` (The Contract)

**Roles:** Product Visionary + UI/UX Designer + Architect
**Phases:** Ideate, Design

### What happens

For infrastructure, the roles shift context:

**Product Visionary:**
- **Pain:** Services go down silently. You discover the DNS server has been dead for 3 days when something else breaks.
- **Vision:** A single dashboard showing the health of every service, with instant alerts when something fails.

**Architect** locks in the infrastructure contract:
```yaml
# Added to ARCHITECTURE.md — Service Definition

Service: uptime-kuma
Port: 3001 (external) → 3001 (internal)
Network: monitoring_net (new bridge network)
Volume: uptime-kuma-data:/app/data (persistent)
Dependencies: none (monitors other services via HTTP probes)
Restart Policy: unless-stopped
Health Check: HTTP GET http://localhost:3001/api/status-page/heartbeat
Labels:
  - homepage.group=Monitoring
  - homepage.name=Uptime Kuma
  - homepage.icon=uptime-kuma.png
```

### Topology influence
The **infrastructure topology** requires:
- All port allocations checked against existing services (no conflicts)
- Network topology documented (which bridge networks, which services share them)
- Volume mount paths validated
- No secrets in the compose file (use env vars or Docker secrets)

---

## Step 2: `/step2-trap` (Setting the Trap)

**Roles:** Principal Engineer + SDET
**Phases:** Contract & Plan

### What happens

The **DevOps Engineer** writes the task plan:
```
1. Add uptime-kuma service definition to docker-compose.yml (trivial)
2. Create monitoring_net bridge network (trivial)
3. Add volume definition for persistent data (trivial)
4. Configure Telegram notification in uptime-kuma config (moderate)
5. Add health check probes for all existing services (moderate)
6. Update homepage dashboard labels (trivial)
```

The **SDET** defines the verification criteria:
```bash
# Validation tests:
1. docker compose config --quiet  # YAML syntax valid
2. docker compose up -d uptime-kuma  # Service starts
3. curl -s http://localhost:3001/api/status-page/heartbeat  # Health check responds
4. No port conflicts with existing services (grep for :3001 in compose file)
5. Volume is persisted across restart
```

### Topology influence
The **infrastructure topology** enforces:
- `docker compose config --quiet` must pass before any deployment
- Port isolation: verify no other service uses port 3001
- No-auto-apply: changes are validated and reviewed before `docker compose up`

---

## Step 3: `/step3-build` (The Autonomous Factory)

**Roles:** DevOps Engineer
**Phases:** Build

### What happens

```bash
# Validate YAML:
$ docker compose config --quiet
# ✔ Valid

# Check port conflicts:
$ grep -n "3001" docker-compose.yml
# Only uptime-kuma — no conflicts ✔

# Deploy:
$ docker compose up -d uptime-kuma
# ✔ Service started

# Verify health:
$ curl -sf http://localhost:3001/api/status-page/heartbeat && echo "healthy"
# healthy ✔

# Verify persistence:
$ docker compose restart uptime-kuma
$ sleep 5
$ curl -sf http://localhost:3001/api/status-page/heartbeat && echo "still healthy"
# still healthy ✔
```

### Topology influence
- **Infrastructure topology:** NO `docker compose up -d` without first running `docker compose config --quiet`
- Changes are applied to the specific service only, not the entire stack

---

## Step 4: `/step4-audit` (The Jury)

**Roles:** Security Engineer + SDET
**Phases:** Test, Review, Audit

### What happens

**Security Engineer:**
- Is the Uptime Kuma dashboard exposed to the public internet? (Should be internal only)
- Are Telegram API tokens stored as Docker secrets, not environment variables in the compose file?
- Is the monitoring network isolated from the data network?
- Can Uptime Kuma be used as a side-channel to probe internal services?

**SDET:**
- Stop a monitored service — does Uptime Kuma detect it within the configured interval?
- Restart Uptime Kuma — does it retain all configured monitors from the persistent volume?
- Does the Telegram notification actually fire? (Send a test alert)

---

## Step 5: `/step5-ship` (The Gatekeeper)

**Roles:** DevOps Engineer + Principal Engineer
**Phases:** Integrate, Ship

### What happens

For infrastructure, "shipping" means:
1. Commit the compose file changes
2. Document the new service in `ARCHITECTURE.md` (port, network, volume, health check)
3. Update the port allocation table
4. Archive docs, reset `STATUS.md`

### Topology influence
- The **infrastructure topology** does a final drift check: does the running stack match the committed compose file? `docker compose config` vs. actual running containers.

---

## Standalone Phase: `/fix`

**Uptime Kuma stops sending Telegram alerts** after a Docker host restart.

```
/fix

Bug: After the Docker host rebooted, Uptime Kuma is running and shows
green status for all services, but Telegram notifications no longer
fire for test alerts. The Telegram bot token is configured.
```

The agent:
1. **Diagnoses:** The Telegram webhook URL resolves to the old container IP post-restart
2. **Patches:** Switches to hostname-based resolution using the Docker network alias
3. **Verifies:** Sends a test alert successfully
4. **Done.**
