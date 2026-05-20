---
name: step5-ship
description: "Step 5: Deployment, infrastructure, and post-flight checks"
---
# Workflow: Ship (The Deployment)

<thinking_process>
The Ship phase is about "Delivery." Think about:
1. Safe deployment strategies (Blue/Green, Canary).
2. Infrastructure stability.
3. Post-deployment monitoring.
</thinking_process>

**Goal:** Deploy the feature and ensure operational stability.

## Composition
- **Roles:** `DevOps Engineer`
- **Phases:** `Ship`
- **Native Tools:** Uses `walkthrough.md` and `task.md`.

## Process

1.  **Deploy**: The **DevOps Engineer** provisions infrastructure and pushes the build.
2.  **Verify**: Perform live smoke tests.
3.  **Clean up**: Archive the feature logs and mark as shipped.

## Accuracy Checks
- [ ] Is the service reachable at the production URL?
- [ ] Are logs and monitoring dashboards showing healthy status?
- [ ] Is the feature documentation updated?

[STATE: SHIPPED]