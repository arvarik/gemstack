# Drift Detection

Over time, your codebase evolves — new dependencies get added, environment variables change, files get renamed or deleted. When your `.agent/` documentation doesn't reflect these changes, the AI operates on stale assumptions. Gemstack's **drift detection** catches this before it causes problems.

---

## What Is Context Drift?

Context drift occurs when your actual codebase diverges from what's documented in your `.agent/` files. For example:

- You add `redis` to `package.json` but never mention it in `ARCHITECTURE.md`
- You remove the `STRIPE_API_KEY` env var but it's still documented
- You delete `src/legacy/old-api.ts` but `STATUS.md` still lists it as a relevant file

The AI doesn't know about these changes — it reads your `.agent/` files and assumes they're accurate. Drift leads to hallucination: the AI writes code that imports removed packages, references deleted files, or uses deprecated environment variables.

---

## The Two Detection Tools

### `gemstack diff` — Drift Detection

Compares your `.agent/` documentation against your actual codebase state:

```bash
gemstack diff
```


This analyzes **3 categories** of drift:

#### 1. Dependency Drift

Compares packages in your manifest files (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`) against backtick-quoted package names in `ARCHITECTURE.md`.

| Finding | Meaning |
|---------|---------|
| **New dependency not documented** | A package exists in your manifest but isn't mentioned in `ARCHITECTURE.md` |
| **Documented dependency removed** | A package is mentioned in `ARCHITECTURE.md` but no longer in your manifest |

#### 2. Environment Variable Drift

Compares variables in `.env.example` against backtick-quoted variable names in `ARCHITECTURE.md`.

| Finding | Meaning |
|---------|---------|
| **New env var not documented** | A variable exists in `.env.example` but isn't mentioned in `ARCHITECTURE.md` |
| **Documented env var removed** | A variable is mentioned in `ARCHITECTURE.md` but no longer in `.env.example` |

#### 3. Stale File References

Checks that every file path listed in `STATUS.md` under "Relevant Files" actually exists on disk.

| Finding | Meaning |
|---------|---------|
| **Stale file reference** | A file is listed in `STATUS.md` but doesn't exist on disk |

### Clean Output

When no drift is detected:


---

### `gemstack check` — Integrity Validation

Validates that your `.agent/` directory is structurally correct:

```bash
gemstack check
```


This verifies:

| Check | What It Validates |
|-------|-------------------|
| **Required files exist** | All 5 `.agent/*.md` files are present |
| **STATUS.md has a valid state** | The `[STATE: ...]` tag contains a recognized value |
| **Topology is declared** | `ARCHITECTURE.md` contains a `**Topology:** [...]` line |
| **Plugin checks pass** | Custom validation checks registered via `gemstack_register_checks` |

When validation fails:


---

## Automating Drift Checks

### Git Hooks

Install a pre-commit hook that blocks commits when drift is detected:

```bash
gemstack hook install
```

This installs a `pre-commit` hook that runs:
1. `gemstack check` — validates `.agent/` integrity
2. `gemstack diff` — detects context drift

If either check fails, the commit is blocked with a descriptive error message.

```bash
gemstack hook remove   # Remove the hooks later
```

### CI Pipeline

Add drift detection to your CI pipeline:

```yaml
# .github/workflows/ci.yml
- name: Check .agent/ integrity
  run: gemstack check

- name: Detect context drift
  run: gemstack diff
```

Or generate a full CI config automatically:

```bash
gemstack ci generate          # GitHub Actions (default)
gemstack ci generate --gitlab # GitLab CI
```

### Shell Script

For custom automation:

```bash
#!/bin/bash
# Pre-deploy drift check
gemstack check && gemstack diff || {
  echo "❌ Context drift detected — update .agent/ before deploying"
  exit 1
}
```

---

## Fixing Detected Drift

When `gemstack diff` reports drift, here's how to fix each category:

### Dependency Drift

**New dependency not documented:**
1. Open `.agent/ARCHITECTURE.md`
2. Add the package to the appropriate section (Core Dependencies, Optional Dependencies, etc.)
3. Include the version constraint and a brief description of why it's used

**Documented dependency removed:**
1. Open `.agent/ARCHITECTURE.md`
2. Remove the stale reference to the package
3. If it was a significant removal, note it in `STATUS.md` under blocking issues

### Environment Variable Drift

**New env var not documented:**
1. Open `.agent/ARCHITECTURE.md`
2. Add the variable to the Environment Variables section
3. Include its purpose, whether it's required, and a default value if applicable

**Documented env var removed:**
1. Open `.agent/ARCHITECTURE.md`
2. Remove the stale reference

### Stale File References

1. Open `.agent/STATUS.md`
2. Update the "Relevant Files" section to reflect the current file paths
3. If files were renamed, update to the new paths
4. If files were deleted, remove them from the list

---

## MCP Integration

The drift detection tools are also available as MCP tools for IDE agents:

| MCP Tool | CLI Equivalent | Description |
|----------|---------------|-------------|
| `gemstack_diff` | `gemstack diff` | Returns drift report in markdown |
| `gemstack_check` | `gemstack check` | Returns pass/fail with error list |

This means your Cursor/Claude Desktop agent can proactively detect drift during its work without you running any commands.

---

## Best Practices

1. **Run `gemstack diff` before starting new features** — Catch drift early before it compounds across multiple features.

2. **Install git hooks on every project** — `gemstack hook install` takes 2 seconds and prevents stale documentation from ever being committed.

3. **Keep `ARCHITECTURE.md` as the source of truth** — When you add a dependency or env var, update `ARCHITECTURE.md` in the same commit.

4. **Use `gemstack init --ai` for bulk updates** — If your project has drifted significantly, re-running `gemstack init --ai` can regenerate context files with current reality.

5. **Don't ignore drift warnings** — Every unresolved drift item is a potential hallucination vector. The AI will reference documented packages that no longer exist.

---

## Next Steps

- ⚙️ Learn what the `.agent/` files contain in [The `.agent/` Context System](the-agent-context.md)
- 🛠️ Set up automated hooks in [Configuration & Integrations](configuration-and-integrations.md)
- 🧠 Understand how context is compiled in [The Context Compiler](context-compiler.md)
