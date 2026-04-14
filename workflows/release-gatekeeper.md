---
name: release-gatekeeper
description: Run the release gatekeeper workflow
---
# Workflow: Release Gatekeeper

**Goal:** Break the app, log evidence, do a final sanity check, deploy, and clean up the archive folders.

## Composition
This workflow composes:
- **Roles:** `QA Engineer`, `Security Engineer`, `DevOps Engineer`
- **Phases:** `Test`, `Review`, `Ship`

## Process

1. **Step 1: Test (QA Engineer)**
   - Act as the **QA Engineer**. Execute the scenarios in `.agent/TESTING.md`. Provide terminal execution evidence for every test.
   - If blocking bugs are found, document them and halt the release (sending the feature back to the `Fix` phase).

2. **Step 2: Review (Security Engineer)**
   - Act as the **Security Engineer**. Assess the new feature for vulnerabilities. Check for exposed secrets, missing rate limits, and OWASP issues. Document findings in `.agent/STATUS.md`.

3. **Step 3: Ship (DevOps Engineer)**
   - Act as the **DevOps Engineer**. If tests and reviews pass, merge the feature branch to `main`.
   - Execute the deployment steps defined in `.agent/ARCHITECTURE.md`.
   - Perform post-ship cleanup: move feature documents from `docs/explorations/`, `docs/designs/`, and `docs/plans/` into `docs/archive/{feature}/`. Clear `.agent/STATUS.md`.

## Code Writing Policy
**INFRASTRUCTURE AND TESTS ONLY.** You write automated test scripts, deployment scripts, CI/CD pipelines, and configuration files. You NEVER write or modify application feature code.