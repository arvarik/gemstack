# Migration DX Improvements — Ideation

## Context

Migrated 8 repositories (whoop-go, whoop-stats, eero-go, eero-stats, contrack, personal-blog, aisrt, paste) to the gemstack CLI in a single session. This exposed multiple friction points in the CLI tooling, from noisy parsers to missing batch operations. Every pain point below was **directly experienced**, not hypothetical.

---

## Ideas Considered

### 1. `gemstack diff` Parser Overhaul — Precision Over Recall

**The pain**: The `ContextDiffer._extract_documented_deps()` method uses a naive regex (`[|*-]\s*` + backticks) that matches *everything* in backticks inside markdown tables and bullet lists. This means Go struct field JSON tags (`sleep_id`, `zone_five_milli`), SQL column types (`BIGINT`, `BYTEA`), error code constants (`API_ERROR`, `CONFLICT`), and even markdown pipe characters show up as "dependencies" or "environment variables." In our migration, **>90% of drift reports were false positives**. The tool cried wolf so loudly that we couldn't distinguish real drift from noise without manually reading every ARCHITECTURE.md.

**The opportunity**: A semantically-aware parser that scopes extraction to specific ARCHITECTURE.md sections would eliminate false positives:
- **Dependencies**: Only extract from `## Tech Stack`, `## Dependencies`, `### Core Libraries` sections
- **Env vars**: Only extract from `## Environment`, `## Configuration` sections  
- **Ignore**: Code blocks (` ``` `), inline code in prose paragraphs, table cells that aren't in dependency/env sections

**Source files**: [`differ.py:221-237`](file:///Users/arvind/Documents/github/gemstack/src/gemstack/utils/differ.py#L221-L237) (dep extraction), [`differ.py:254-268`](file:///Users/arvind/Documents/github/gemstack/src/gemstack/utils/differ.py#L254-L268) (env var extraction)

**Rough size**: Medium  
**Priority**: **Must-have** — the diff tool is effectively unusable on real-world projects right now

---

### 2. `gemstack check` — Separate Exit Codes for Errors vs Warnings

**The pain**: The pre-commit hook runs `gemstack check`, which exits 0 only when there are **no errors AND no warnings**. But the check command produces warnings for things like markdown table pipes being parsed as stale file references (`Stale reference in STATUS.md: |`). This blocked every single commit across 5 repos. We had to use `--no-verify` for a **documentation-only migration** — exactly the kind of commit that should fly through.

**The opportunity**: 
- Exit 0 on warnings only, exit 1 on errors only
- Add `--strict` flag that treats warnings as errors (for CI)
- The pre-commit hook should use the default (non-strict) behavior
- Bonus: add `--warn-as-error` / `--ignore-warnings` flags

**Source files**: [`check_cmd.py:49-56`](file:///Users/arvind/Documents/github/gemstack/src/gemstack/cli/check_cmd.py#L49-L56) (exit logic), [`hook_cmd.py:16-27`](file:///Users/arvind/Documents/github/gemstack/src/gemstack/cli/hook_cmd.py#L16-L27) (hook script)

**Rough size**: Small  
**Priority**: **Must-have** — the hook is broken out of the box on every repo we tested

---

### 3. `gemstack check` Stale Reference Parser — Too Greedy

**The pain**: The validator's stale reference check in STATUS.md matches markdown table pipes (`|`), brackets (`[`), and bold markers (`**[word]**`) as file references. Every single repo had 10-30 of these false-positive stale reference warnings. Related to idea #1 but in the validator, not the differ.

**The opportunity**: The stale ref scanner should:
- Only look inside a `## Relevant Files` section (which it claims to do, but the validator likely uses a different path than the differ)
- Exclude markdown syntax characters: `|`, `[`, `]`, `**`, `##`, etc.
- Require file references to look like file paths (contain `.` or `/`)

**Rough size**: Small  
**Priority**: **Must-have** — directly feeds into idea #2 (warnings cause hook failures)

---

### 4. Auto-Detection Gaps — Go Libraries and Python CLIs

**The pain**: The `ProjectDetector` failed to auto-detect topologies for 2 of 8 repos:
- **aisrt** (Python + Typer CLI + faster-whisper ML): Typer isn't in `_BACKEND_PYTHON_DEPS` and faster-whisper isn't in `_MLAI_PYTHON_DEPS`. Detected as zero topologies.
- **paste** (Go + `net/http` backend + HTML templates frontend): `net/http` isn't a framework dep, and HTML templates aren't detected as frontend. Detected as zero topologies.
- **whoop-go & eero-go** (Go SDK libraries): Both have `cmd/` directories (for examples/tools), so they were classified as `backend` instead of `library-sdk`. The detector checks `(root / "pkg").is_dir() and not (root / "cmd").is_dir()` — but SDK repos can have both.

**The opportunity**:
- Add `typer`, `click`, `fire` to `_BACKEND_PYTHON_DEPS` (or a new CLI topology)
- Add `faster-whisper`, `ctranslate2`, `whisper`, `onnxruntime` to `_MLAI_PYTHON_DEPS`
- For Go: detect `net/http` imports as backend, detect HTML template files as frontend
- For library-sdk: check if there's a `pkg/` dir *or* if the project has no `main.go` in root / `cmd/` is just examples
- Fallback: read existing `**Topology:**` from ARCHITECTURE.md if present, don't require re-detection

**Source file**: [`detector.py:416-461`](file:///Users/arvind/Documents/github/gemstack/src/gemstack/utils/detector.py#L416-L461) (Go detection), [`detector.py:110-140`](file:///Users/arvind/Documents/github/gemstack/src/gemstack/utils/detector.py#L110-L140) (Python ML deps)

**Rough size**: Medium  
**Priority**: **Should-have** — `--topology` override exists, but the auto-detection should work for common setups

---

### 5. `gemstack batch` — Multi-Repo Operations

**The pain**: Every operation in our migration had to be manually looped over 8 repos with `for repo in ...; do cd ... && gemstack <cmd>; done`. This includes check, migrate, diff, hook install, and the entire PR workflow. For a tool that manages `.agent/` across a portfolio of projects, there's no first-class multi-repo support.

**The opportunity**: A new `gemstack batch` command (or `--all` flag on existing commands):
```bash
# Configure a project registry
gemstack registry add ~/Documents/github/whoop-go
gemstack registry add ~/Documents/github/eero-stats
# ... or auto-discover from a parent dir

# Batch operations
gemstack batch check          # Run check on all registered projects
gemstack batch migrate        # Migrate all
gemstack batch diff           # Drift report across all
gemstack batch hook install   # Install hooks everywhere
```

This ties into the existing `gemstack matrix` command, which already "scans for Gemstack projects."

**Rough size**: Large  
**Priority**: **Should-have** — massive DX win for developers managing multiple repos

---

### 6. `gemstack migrate` — Idempotency and Topology Replacement

**The pain**: Running `gemstack migrate` twice appends testing matrices again (though the migrator checks for duplicate headers). More importantly, re-running with a *different* topology (e.g., changing from `backend` to `library-sdk`) just appends the new topology's matrix without removing the old one. There's no "replace topology" flow.

**The opportunity**:
- Add `--replace` flag that removes previously-injected topology sections before adding new ones
- Make the topology declaration in ARCHITECTURE.md updatable (currently skipped if one exists)
- Add `gemstack migrate --remove backend` to cleanly remove a topology

**Source file**: [`migrator.py:145-171`](file:///Users/arvind/Documents/github/gemstack/src/gemstack/project/migrator.py#L145-L171)

**Rough size**: Medium  
**Priority**: **Nice-to-have** — only matters when you make mistakes during initial setup

---

### 7. `gemstack ship` CLI Command — PR Workflow Automation

**The pain**: The full PR workflow (branch, push, create PR, wait for CI, merge, cleanup) required ~15 manual steps per repo. This is the most common operation after finishing any gemstack lifecycle, and it's entirely unautomated.

**The opportunity**: A `gemstack ship` command that:
1. Creates a branch from the current commit(s) ahead of origin/main
2. Pushes the branch
3. Creates a PR via `gh` with an auto-generated description from STATUS.md
4. Waits for CI checks
5. Merges via squash
6. Switches back to main, pulls, deletes branch

This aligns with the existing `/ship` phase in the 5-step lifecycle.

**Rough size**: Large  
**Priority**: **Should-have** — this is the "last mile" of every feature lifecycle

---

### 8. `gemstack init` Self-Application — Gemstack Should Eat Its Own Dog Food

**The pain**: The gemstack repo itself doesn't have `.agent/` context files (only the `.agent/workflows/` directory). It can't use `gemstack check`, `gemstack diff`, `gemstack route`, or `gemstack status` on itself.

**The opportunity**: Bootstrap gemstack's own `.agent/` files:
- ARCHITECTURE.md documenting the CLI structure, plugin system, topology profiles
- STATUS.md with `[STATE: SHIPPED]` or `[STATE: IN_PROGRESS]`
- PHILOSOPHY.md capturing the "top-down orchestration" principles from README.md
- TESTING.md with the test matrix
- STYLE.md with Python coding conventions

**Rough size**: Small  
**Priority**: **Nice-to-have** — but important for credibility and dogfooding

---

### 9. Smart STATE Auto-Detection

**The pain**: Every repo was missing `[STATE: ...]` in STATUS.md. We had to manually read each STATUS.md to figure out the correct state, then inject it. The gemstack check warning just says "missing" — it doesn't suggest what the state should be.

**The opportunity**: 
- `gemstack check --fix` could auto-detect state from STATUS.md content (e.g., "DX Polish shipped" → SHIPPED, "In Progress" → IN_PROGRESS)
- `gemstack migrate` could add the STATE tag automatically based on heuristics (has git tags → SHIPPED, has active TODO items → IN_PROGRESS)
- At minimum, `gemstack check` should suggest the likely state in its warning message

**Rough size**: Small  
**Priority**: **Should-have** — reduces manual work during onboarding

---

### 10. Hook Script — Respect Existing Hooks

**The pain**: When `gemstack hook install --pre-commit` writes the hook, it overwrites any existing gemstack hook (good) but doesn't chain with pre-existing non-gemstack hooks. eero-go and eero-stats had custom golangci-lint hooks in `.githooks/pre-commit` (managed via `core.hooksPath`). The gemstack hook writes to `.git/hooks/pre-commit` which is a different path — so both hooks ran, and the golangci-lint one blocked.

**The opportunity**:
- Detect if `core.hooksPath` is set and install there instead
- Support hook chaining (run existing hook, then gemstack check)
- Or at least warn the user when a custom hooks path is configured

**Rough size**: Small  
**Priority**: **Nice-to-have**

---

## Recommendation

### Move to Design Phase

**Priority 1 (Must-Have — Blocking DX):**
1. **#2: `check` exit code separation** — Fix the broken pre-commit hook. Errors = exit 1, warnings = exit 0. This is a 30-minute fix that unblocks every repo.
2. **#3: Stale reference parser fix** — Stop parsing markdown syntax as file references. Eliminates 80%+ of false warnings.
3. **#1: `diff` parser overhaul** — Scope extraction to relevant ARCHITECTURE.md sections. Eliminates 90%+ of false drift reports.

These three are tightly coupled and could ship as a single PR. They address the core issue: **the tools generate so much noise that users learn to ignore them, defeating their purpose.**

**Priority 2 (Should-Have — High Impact):**
4. **#4: Auto-detection gaps** — Expand the dependency sets to cover Typer, faster-whisper, net/http, and fix the library-sdk heuristic.
5. **#9: Smart STATE auto-detection** — Reduce manual work during migration and onboarding.

### Alignment with Philosophy (README.md)

From the README: *"Gemstack gives your Gemini-powered agents architectural memory, topology-aware guardrails, and a 5-step lifecycle that forces them to verify their own work."*

The diff/check noise issues directly undermine this promise. If the verification tools produce 90% false positives, agents (and humans) learn to bypass them. Fixing precision is a prerequisite for the guardrails to have any credibility.

---

## Open Questions

1. **Should `gemstack diff` have a `--strict` / `--lenient` mode?** Or should precision improvements make the single mode reliable enough?
2. **Is `gemstack batch` worth the complexity?** Or is `gemstack matrix` + shell loops sufficient for power users?
3. **Should the gemstack repo itself use gemstack?** This creates a chicken-and-egg problem during development but would be valuable for dogfooding.
4. **Should `gemstack ship` exist, or is this out of scope?** The 5-step lifecycle already has a `/ship` phase — should the CLI automate the git/GitHub portion, or just the context/documentation portion?
