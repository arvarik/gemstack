# Audit Findings — v1.1.0 Migration DX Improvements

**Auditor:** Security Engineer + SDET
**Date:** 2026-04-23
**Scope:** `git diff origin/main` — 9 files, +176 / -36 lines

## Automated Checks

| Check | Result |
|-------|--------|
| pytest (343 tests) | ✅ ALL PASS (1.28s) |
| ruff (SAST linter) | ✅ ALL PASS |
| mypy (type checking) | ✅ ALL PASS (78 source files) |

---

## Findings

### [DEGRADED] `differ.py:_check_stale_refs` — Inconsistent Regex vs Validator

**File:** `src/gemstack/utils/differ.py`, lines 152-173
**Severity:** `[DEGRADED]`

The `_check_stale_refs()` method in the differ uses a **looser regex** than the validator's `_extract_relevant_files()`:

- **Differ (line 166):** `r"[-*]\s*`?([^\s`]+)`?"` — Matches backtick-optional items, including bare words like `—` (em dash), list content, and description text.
- **Validator (line 127):** `r"[-*]\s+`([^`]+)`"` — Only matches backtick-wrapped items and filters for path-like patterns (must contain `.` or `/`).

The validator was correctly tightened for v1.1.0, but the **differ was not updated** to use the same extraction logic. This means `gemstack diff` can still produce false-positive stale file references from non-path text in the `## Relevant Files` section, while `gemstack check` will not.

**Expected:** Both should use the same extraction logic.
**Actual:** Differ uses old, loose regex; validator uses new, strict regex.

**Reproduction:**
```markdown
## Relevant Files
- `src/main.py` — entry point
```
The differ will also extract `—` and `entry` and `point` as file references.

---

### [DEGRADED] `validator.py:_suggest_state` — Overly Broad "release" Match

**File:** `src/gemstack/project/validator.py`, lines 139-147
**Severity:** `[DEGRADED]`

The `_suggest_state()` heuristic matches the substring `"release"` anywhere in `content.lower()`. This will incorrectly suggest `SHIPPED` for almost every project that has a `## Release History` section, even if the project is actively `IN_PROGRESS`.

**Expected:** Only suggest `SHIPPED` when the project is actually shipped (e.g., from a `[STATE: SHIPPED]` equivalent context, not from section headings).
**Actual:** Any STATUS.md that mentions "Release History" will get `suggested: SHIPPED`.

**Reproduction:**
```python
content = "# Status\n\n## Release History\n| v1.0.0 | Initial |\n\n## Current Focus\nBuilding v2.0"
ProjectValidator._suggest_state(content)  # Returns "SHIPPED" — wrong, should be "IN_PROGRESS"
```

**Fix approach:** Check precedence order — `IN_PROGRESS` should be checked before `SHIPPED`, or the `release` check should require stronger signals (e.g., `[STATE: SHIPPED]` or `released v\d` patterns, not just the word "release" in a heading).

---

### [COSMETIC] `_ENV_SECTION_PATTERNS` — Redundant Negative Lookahead

**File:** `src/gemstack/utils/differ.py`, line 294-296
**Severity:** `[COSMETIC]`

```python
_ENV_SECTION_PATTERNS = re.compile(
    r"configuration|environment|config(?!uration)", re.IGNORECASE
)
```

The `config(?!uration)` negative lookahead is redundant because `configuration` is already matched by the first alternative. The regex engine will match `configuration` on the first alternative before ever reaching `config(?!uration)`. This isn't a bug (it works correctly), but it's misleading — a reader might think the intent was to exclude "configuration" from the `config` match, which the regex already handles.

---

### [COSMETIC] `batch_cmd.py` — No Deduplication of Topology Classification

**File:** `src/gemstack/project/detector.py`, lines 451-471
**Severity:** `[COSMETIC]`

The Go detector can append `Topology.BACKEND` multiple times — once from `net/http` detection (line 460) and again from `cmd/` directory detection (line 467). The `cmd/` check has a guard (`Topology.BACKEND not in profile.topologies`), but if a project has `net/http` AND `cmd/` AND `pkg/`, the topologies list could contain `[BACKEND, BACKEND, LIBRARY_SDK]` if the net/http guard at line 452 runs first.

Actually — on closer inspection, the `net/http` block is also guarded by `if Topology.BACKEND not in profile.topologies` (line 452), and the `cmd/` block has the same guard. So this is **not a bug** — the guards are correct. Disregarding.

---

## Logic Drift Assessment

| Area | Status | Notes |
|------|--------|-------|
| Section-scoped parser (`differ.py`) | ✅ Clean | `_extract_sections()`, `_extract_documented_deps()`, `_extract_documented_env_vars()` correctly scope to relevant headings |
| `_DEP_EXCLUDE` filter | ✅ Clean | Properly filters SQL types, version strings, and function calls |
| `check --strict` flag | ✅ Clean | Correctly raises `ValidationError` after error check, proper ordering |
| Hook script fix | ✅ Clean | Positional arg syntax is correct for the check command |
| Detector expansions | ✅ Clean | New deps added to frozen sets, Go detection properly guarded |
| Validator scoped extraction | ✅ Clean | `_extract_relevant_files()` properly scoped to `## Relevant Files` |
| `batch_cmd.py` | ✅ Clean | Proper subprocess management, timeout handling, allowlist-only commands |
| `registry_cmd.py` | ✅ Clean | Path validation, dedup, atomic save via config |
| Test fixture updates | ✅ Clean | Old tests correctly updated with `## Tech Stack` / `## Configuration` headings |
| `main.py` command registration | ✅ Clean | Both `registry_app` and `batch_app` correctly imported and registered |

## Security Assessment

| Check | Status |
|-------|--------|
| Path traversal in registry | ✅ `Path.resolve()` used |
| Subprocess injection in batch | ✅ Hardcoded allowlist, no user-provided command strings |
| Config persistence (SecretStr) | ✅ API key exposure controlled via `get_api_key()` |
| File I/O error handling | ✅ All reads wrapped in try/except |
| Timeout protection in batch | ✅ 60s timeout on subprocess calls |

---

## Verdict

**Two `[DEGRADED]` findings block release:**

1. **Differ stale ref regex inconsistency** — the differ's `_check_stale_refs()` uses a loose regex while the validator was correctly tightened. This will produce false-positive drift warnings in `gemstack diff`.
2. **`_suggest_state` overly broad match** — the `"release"` substring match will misclassify most projects with a Release History section as `SHIPPED`.

Both are fixable in < 30 minutes.

---

### SYSTEM ROUTING
[🟠] DEGRADED: 2 findings require fixes before release.
🟠 NEXT ACTION: Open a New Chat, run `/step3-build`, and instruct:
> "You are in Fix-only mode. Read `.agent/AUDIT_FINDINGS.md`. Resolve all documented issues. Do not add new features."
