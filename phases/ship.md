---
name: ship
description: Merge, deploy, archive docs, reset STATUS.md, and prepare for the next feature cycle
---
# Phase: Ship

Purpose: Deploy safely, verify it works, and clean up for the next feature.

## Primary Roles
- DevOps Engineer (deployment and infrastructure)

## Inputs
- Review phase completed with no blocking items
- .agent/ARCHITECTURE.md for deployment configuration
- .agent/TESTING.md confirming all scenarios pass

## Pre-Ship Checklist
Before deploying, verify:
- [ ] All "blocks release" bugs resolved
- [ ] Architecture review passed
- [ ] Security review passed (critical for public-facing deploys)
- [ ] No secrets in code, config, or git history
- [ ] Environment variables documented in .env.example
- [ ] Dependencies pinned to specific versions
- [ ] README updated if setup steps changed

## Process
1. Determine deployment target and method from ARCHITECTURE.md
2. **Pre-Merge Cleanup (Critical):** On the feature branch, finalize all documentation and tracking files:
   - **Archive feature docs**: Move all docs for this feature into a single archive folder using `git mv` (preserves history).
     ```bash
     mkdir -p docs/archive/{feature-name}/
     for f in docs/explorations/* docs/designs/* docs/plans/*; do
       [ -f "$f" ] && git mv "$f" docs/archive/{feature-name}/
     done
     ```
   - **Synthesize and Prune**: Ensure decisions from archived docs are in `.agent/ARCHITECTURE.md`. Remove stale schemas or replaced contracts.
   - **Reset STATUS.md**: Update `.agent/STATUS.md` to show what was just completed, clear "Relevant Files", and prep for the next feature.
   - **Clean TESTING.md**: Clean `.agent/TESTING.md` by keeping regression scenarios but archiving feature-specific completed ones.
   - **Commit Cleanup**: Commit all these changes to the feature branch in a single commit.
3. Merge feature branch to main:
   ```bash
   git checkout main
   git merge feat/{feature-name}
   git push origin main
   ```
4. Run the full test suite on main to confirm nothing broke
5. Deploy to staging/preview if available
6. Smoke test the deployment
7. Deploy to production
8. Verify production deployment works
9. Monitor for errors in the first 15 minutes

## Rollback Plan
Before every deploy, know how to undo it:
- What command reverts the deploy?
- How long does rollback take?
- Is there data migration that can't be rolled back?
  If yes, flag this before deploying.

## Post-Ship Cleanup
After successful deployment:

1. **Clean up worktrees**: If parallel worktrees were used during this feature, remove them:
   ```bash
   git worktree list
   git worktree remove ../project-feature-worktree-name
   ```
   Stale worktrees accumulate on disk and cause confusion. Clean them up every time you ship.

2. **Update Tracker**: Move the issue to Done (e.g. in Linear, Jira).

## Output
- Deployed, running application
- Clean docs/ directory (only active feature docs remain)
- Fresh STATUS.md ready for the next feature
- Archived feature docs in docs/archive/{feature-name}/

## Files Updated
| File | Change |
|------|--------|
| .agent/STATUS.md | Reset for next feature |
| .agent/TESTING.md | Archived, kept regression scenarios |
| .agent/ARCHITECTURE.md | Verified up-to-date |
| docs/archive/{feature-name}/ | Feature docs moved here |
| docs/explorations/, designs/, plans/ | Cleaned of shipped feature docs |

## Post-Ship
Pick up the next feature from the exploration doc's recommendations
or return to the ideate phase.