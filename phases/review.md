---
name: review
description: Adopt the review phase
---
# Phase: Review

Purpose: Step back and evaluate the bigger picture before shipping.

## Primary Roles
- Architect (coherence and quality review)
- Security Engineer (vulnerability assessment)
- Product Visionary (does this actually solve the original problem?)

## When To Run
- After a feature is built and tested (all tests pass)
- Before merging to main
- Periodically (every few features) for drift check
- Before any public deployment

## Process

### Architecture Review:
1. Does the implementation follow ARCHITECTURE.md patterns?
2. Has complexity grown in any one area disproportionately?
3. Are there new patterns that conflict with existing ones?
4. Is the data flow still traceable and understandable?
5. Do the API contracts in ARCHITECTURE.md still match the
   actual implementation? Update if they've drifted.

### Security Review:
1. Identify all new attack surface (new endpoints, user inputs,
   file handling, external API calls)
2. For each: what's the worst-case exploit?
3. Check for OWASP top 10 where applicable
4. Check dependencies for known vulnerabilities
5. For AI-exposed features: prompt injection, cost abuse, data leak

### Product Review:
1. Does this feature actually solve the pain from the ideate doc?
2. Use it as a real user would. Is it intuitive?
3. Does it fit naturally with the rest of the product?
4. Is anything missing that the user would immediately ask for?
5. Does it align with PHILOSOPHY.md?

## Output
Write findings to STATUS.md under a review section:

### Review Results - [date]
- **Architecture**: [pass / concerns noted]
- **Security**: [pass / findings with severity]
- **Product fit**: [pass / gaps identified]

### Action Items
For each item:
- Description of what needs to change
- Severity: blocks ship / recommended / nice-to-have
- Which role should fix it

## Files Updated
| File | Change |
|------|--------|
| .agent/STATUS.md | Review results + action items |
| .agent/ARCHITECTURE.md | Updated if decisions were made or contracts drifted |

## Transition
Route action items based on their nature:
- **Localized bugs** (specific code issues, missing validation,
  UI glitches): send to the **fix phase**. The fix is re-tested by
  QA, then returns here for re-review of only the changed items.
- **Architectural / structural issues** (wrong data model, misplaced
  responsibilities, pattern violations that require rethinking the
  approach): send back to the **plan + build phases**. Do NOT send
  architectural rework to the fix phase - the fix phase explicitly
  bans architecture changes, and sending structural issues there
  creates contradictory instructions.
- **Recommended / nice-to-have items**: document in STATUS.md for
  future consideration. Do not block the ship.

If clean, move to ship phase.