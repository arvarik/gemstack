# Autonomous Execution

The `gemstack run` command is Gemstack's most powerful feature — it compiles your full project context, calls the Gemini API, parses the structured response, writes files to disk, and tracks costs — all in a single command.


---

## Overview

Instead of copy-pasting compiled prompts into a chat interface, `gemstack run` handles the entire pipeline autonomously:

```bash
gemstack run step1-spec --feature "Add user notifications"   # Define the spec
gemstack run step3-build --feature "Add user notifications"  # Build until tests pass
gemstack run step4-audit --feature "Add user notifications"  # Fresh-context audit
gemstack run step5-ship --feature "Add user notifications"   # Integrate and deploy
```

Each execution goes through a **10-stage pipeline** with built-in safety mechanisms — cost circuit breakers, path traversal prevention, per-project locking, and plugin hooks.

---

## The Execution Pipeline

When you run `gemstack run step3-build --feature "Add user search"`, the following stages execute in order:

```text
 1. Validate       →  Is this step transition legal? (phase router check)
 2. Compile        →  JIT-assemble the full context prompt
 3. Cost Check     →  Will this exceed the per-feature budget?
 4. Pre-Run Hook   →  Fire gemstack_pre_run plugin hook
 5. API Call       →  Send compiled prompt to Gemini via google-genai
 6. Parse          →  Extract file operations from structured response
 7. Write Files    →  Atomic writes with path traversal prevention
 8. Record Costs   →  Append to .agent/costs.json
 9. Post-Run Hook  →  Fire gemstack_post_run plugin hook
10. Summary        →  Print result with cost, duration, and next step
```

### Stage 1: Step Validation

The **deterministic phase router** checks that the requested step transition is valid given the current `STATUS.md` state. For example:
- You can't run `step3-build` if the state is `INITIALIZED` (you must spec and trap first)
- You can't run `step5-ship` if `AUDIT_FINDINGS.md` exists (fix issues first)

If the transition is invalid, Gemstack prints the correct next action and exits.

### Stage 2: Context Compilation

The **Context Compiler** performs JIT prompt assembly — see [The Context Compiler](context-compiler.md) for full details. The compiled prompt includes:
- Workflow goal and step description
- Role definitions (e.g., Principal Backend Engineer for build)
- Phase instructions (e.g., "loop until Exit Code 0")
- Topology guardrails from your `ARCHITECTURE.md` declaration
- Your `.agent/` context files
- Relevant source files from `STATUS.md`
- Plugin-injected sections

### Stage 3: Cost Check

If you specified `--max-cost` or `--max-tokens`, the executor checks cumulative costs from `.agent/costs.json`. If the limit would be exceeded, it raises a `CostLimitExceeded` error with a clear message:

```
Error: Cost limit exceeded for feature "Add user search"
  Current spend: $3.42
  Budget limit:  $5.00
  Estimated cost: $2.15
  Total would be: $5.57 (exceeds limit by $0.57)
```

### Stage 5: API Call

The compiled prompt is sent to the Gemini API via `google-genai` using `asyncio.to_thread()` for non-blocking execution. The default model is `gemini-3.1-pro-preview` (configurable via `gemstack config set default-model`).

### Stage 7: Atomic File Writes

All file writes go through `utils/fileutil.write_atomic()` which:
1. **Validates the path** — resolves symlinks and ensures the target is within the project root (path traversal prevention)
2. **Writes to a temp file** — creates a temporary file in the same directory
3. **Atomic rename** — uses `os.rename()` for atomic replacement (no partial writes on crash)

---

## Dry Run Mode

Preview what would happen without making an API call:

```bash
gemstack run step1-spec --feature "Add user search" --dry-run
```


Dry run mode:
- ✅ Validates the step transition
- ✅ Compiles the full context prompt
- ✅ Reports token count and estimated cost
- ❌ Does NOT call the Gemini API
- ❌ Does NOT write any files

This is useful for:
- Verifying your context compiles correctly before spending money
- Checking estimated costs before a long build session
- Testing plugin hooks in isolation

---

## Cost Controls

### Setting Limits

```bash
# Per-feature USD limit — halts execution when cumulative spend exceeds this
gemstack run step3-build --feature "Add user search" --max-cost 5.00

# Per-step token limit — prevents sending oversized prompts
gemstack run step3-build --feature "Add user search" --max-tokens 500000
```

### How Costs Are Tracked

Every API call is recorded in `.agent/costs.json` with full detail:

```json
{
  "features": {
    "Add user search": {
      "total_cost_usd": 1.23,
      "steps": [
        {
          "step": "step1-spec",
          "model": "gemini-3.1-pro-preview",
          "input_tokens": 45000,
          "output_tokens": 8500,
          "cost_usd": 0.0119,
          "timestamp": "2026-04-24T15:30:00Z",
          "duration_seconds": 12.4
        }
      ]
    }
  }
}
```


### Viewing Costs

```bash
gemstack costs                           # Show costs for all features
gemstack costs --feature "Add user search"  # Show costs for a specific feature
```

> **Note:** Cost limits are opt-in. If you don't specify `--max-cost` or `--max-tokens`, costs are still *recorded* but never *enforced*.

---

## Per-Project Lockfile

To prevent concurrent corruption, `gemstack run` acquires a per-project lockfile before execution. If another `gemstack run` is already running in the same project directory, the second invocation will fail immediately with a clear error:

```
Error: Another gemstack run is already executing in this project.
  Lockfile: /path/to/project/.agent/.gemstack.lock
  If this is stale, delete the lockfile manually.
```

---

## Path Traversal Prevention

All file paths generated by the AI are validated before writing:

1. The path is resolved to its absolute form (following symlinks)
2. The resolved path must start with the project root directory
3. Paths like `../../etc/passwd` or `/tmp/malicious.sh` are rejected with a `PermissionError`

This prevents the AI from writing files outside your project, even if it hallucinates a malicious path.

---

## Circuit Breaker (Bounded Reflexion)

During `step3-build`, the build-test-fix cycle is bounded to a maximum of **3 attempts**:

```text
Attempt 1: Write code → Run tests → FAIL
Attempt 2: Read stderr → Fix code → Run tests → FAIL  
Attempt 3: Read stderr → Fix code → Run tests → FAIL
Circuit breaker triggered → Revert → Write reflection
```

If the test suite still fails after 3 full loops:
1. Changes are reverted to the last known-good state (`git checkout -- .`)
2. A `<reflection>` block is written explaining what was tried and why it failed
3. Control is yielded back to the SDET for test review

---

## Using Compiled Context Directly

If you want to use Gemstack's context compilation with your own AI tooling (instead of the built-in executor), you can:

### Export to Clipboard

```bash
# Copy the compiled prompt to your clipboard
gemstack compile step3-build | pbcopy

# Paste into any AI chat interface
```

### Export as JSON

```bash
# Export as structured JSON
gemstack export --format json > context.json
```

### Use Programmatically

```python
import subprocess
import json

# Get compiled context as a string
result = subprocess.run(
    ["gemstack", "compile", "step3-build"],
    capture_output=True, text=True, check=True
)
compiled_context = result.stdout

# Feed into your own Gemini/OpenAI/Anthropic call
# ...
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `InvalidStepTransition` | Step not allowed from current state | Run `gemstack route` to see the correct next step |
| `CostLimitExceeded` | Cumulative costs would exceed `--max-cost` | Increase the limit or reset costs |
| `APIKeyNotConfigured` | No Gemini API key found | Run `gemstack config set gemini-api-key YOUR_KEY` |
| `LockfileExists` | Another execution is running (or stale lock) | Wait or delete `.agent/.gemstack.lock` |
| `PathTraversalBlocked` | AI generated a path outside the project | Re-run the step (the AI will generate a valid path) |
| `CircuitBreakerTriggered` | 3 build attempts failed | Review the reflection block and fix tests or contracts |

---

## Troubleshooting

### "No API key configured"

```bash
# Set via gemstack config (persisted)
gemstack config set gemini-api-key YOUR_KEY

# Or via environment variable (temporary)
export GEMINI_API_KEY=YOUR_KEY

# Verify
gemstack doctor
```

### "Step transition not allowed"

The phase router enforces a strict lifecycle. Run `gemstack route` to see where you are and what to do next. See [The 5-Step Lifecycle](the-5-step-lifecycle.md) for the full routing decision tree.

### "Costs seem too high"

- Use `--dry-run` to preview costs before execution
- Use `--token-budget` to limit context size: `gemstack compile step3-build --token-budget 100000`
- Use a cheaper model: `gemstack config set default-model gemini-2.5-flash`

---

## Next Steps

- 🧠 Understand how context is assembled in [The Context Compiler](context-compiler.md)
- 💰 Configure cost limits in [Configuration & Integrations](configuration-and-integrations.md)
- 🔄 Learn the lifecycle rules in [The 5-Step Lifecycle](the-5-step-lifecycle.md)
