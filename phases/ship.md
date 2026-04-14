---
name: ship
description: Adopt the ship phase
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
2. Merge feature branch to main:
   ```
   git checkout main
   git merge feat/{feature-name}
   git push origin main
   ```
3. Run the full test suite on main to confirm nothing broke
4. Deploy to staging/preview if available
5. Smoke test the deployment
6. Deploy to production
7. Verify production deployment works
8. Monitor for errors in the first 15 minutes

## Rollback Plan
Before every deploy, know how to undo it:
- What command reverts the deploy?
- How long does rollback take?
- Is there data migration that can't be rolled back?
  If yes, flag this before deploying.

## Post-Ship Cleanup (Critical)
After successful deployment:

1. **Archive feature docs**: Move all docs for this feature into
   a single archive folder using git mv (preserves history).
   Use defensive checks since not every feature produces all doc types:
   ```
   mkdir -p docs/archive/{feature-name}/
   for f in docs/explorations/{this-feature}*.md docs/designs/{this-feature}*.md docs/plans/{this-feature}*.md; do
     [ -e "$f" ] && git mv "$f" docs/archive/{feature-name}/
   done
   ```
   This prevents docs/ folders from growing unbounded. Active folders
   should only contain docs for features currently in progress.

2. **Synthesize into permanent files**: Any architectural decisions,
   new patterns, or style changes from the archived docs should
   already be captured in ARCHITECTURE.md and STYLE.md from the
   review phase. Verify nothing was missed.

3. **Reset STATUS.md**: Clear completed feature state. The new
   STATUS.md should show:
   - What was just shipped (in "Recently Completed")
   - Known issues carried forward
   - What's next (from the original exploration doc's recommendations)
   - Empty "Relevant Files" section (next feature hasn't started)

4. **Clean TESTING.md**: Archive completed test results. Keep only:
   - The test methods section (how to test this project)
   - Any persistent regression scenarios worth re-running
   - Clear the feature-specific scenario tables

5. **Clean up worktrees**: If parallel worktrees were used during
   this feature, remove them:
   ```
   git worktree list
   git worktree remove ../project-feature-worktree-name
   ```
   Stale worktrees accumulate on disk and cause confusion. Clean
   them up every time you ship.

6. **Update Linear**: Move the issue to Done

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