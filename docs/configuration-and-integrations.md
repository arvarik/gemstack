# Configuration & Integrations

This guide covers Gemstack's global configuration system, API key management, and integration with system agent tools like Gemini CLI and Antigravity.

---

## Global Configuration

Gemstack stores its configuration in the standard platform-specific config directory:

| OS | Config File Location |
|----|---------------------|
| **macOS** | `~/Library/Application Support/gemstack/config.toml` |
| **Linux** | `~/.config/gemstack/config.toml` |
| **Windows** | `%APPDATA%/gemstack/config.toml` |

Gemstack uses [platformdirs](https://pypi.org/project/platformdirs/) for cross-platform directory resolution.

### Managing Configuration

```bash
# Set the Gemini API key (required for `gemstack run` and `gemstack init --ai`)
gemstack config set gemini-api-key YOUR_GEMINI_API_KEY

# Set the default model (used by `gemstack run`)
gemstack config set default-model gemini-2.5-flash  # Default: gemini-3.1-pro-preview

# View all current settings (API keys are masked for security)
gemstack config list
```

### Configuration Precedence

When resolving configuration values, Gemstack checks sources in this order (first match wins):

1. **CLI flags** — `--model gemini-2.5-pro` on a specific command
2. **Environment variables** — `GEMINI_API_KEY` or `GOOGLE_API_KEY`
3. **Config file** — Values from `config.toml`
4. **Defaults** — Built-in fallbacks (e.g., `gemini-3.1-pro-preview` for the model)

### Key Configuration Values

| Key | Environment Variable | Default | Description |
|-----|---------------------|---------|-------------|
| `gemini-api-key` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | *(none)* | Google Gemini API key for AI features |
| `default-model` | *(none)* | `gemini-3.1-pro-preview` | Default Gemini model for `gemstack run` |

---

## API Key Setup

The Gemini API key is required for two features:
- `gemstack init --ai` — AI-powered project analysis during initialization
- `gemstack run` — Autonomous workflow step execution

### Getting a Key

1. Visit [aistudio.google.com](https://aistudio.google.com)
2. Create or select a project
3. Generate an API key

### Setting the Key

**Option 1: Via `gemstack config`** (recommended — persisted to config file)

```bash
gemstack config set gemini-api-key YOUR_GEMINI_API_KEY
```

**Option 2: Via environment variable** (useful for CI/CD or temporary usage)

```bash
export GEMINI_API_KEY=YOUR_GEMINI_API_KEY
# or
export GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

**Option 3: Via `.env` file** (project-local)

```bash
# .env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### Verifying the Key

```bash
gemstack config list   # Shows masked key if configured
gemstack doctor        # Checks API key availability as part of diagnostics
```

---

## Cost Tracking

When you use `gemstack run`, every API call is recorded with full cost tracking in `.agent/costs.json`. This includes:

- **Per-step tracking** — How much each workflow step cost in tokens and USD
- **Per-feature tracking** — Cumulative cost across all steps for a feature
- **Model-aware pricing** — Uses Gemini's pricing model ($0.15/1M input tokens, $0.60/1M output tokens for `gemini-3.1-pro-preview`)

### Setting Cost Limits

```bash
# Set a per-feature USD limit (circuit breaker halts execution when exceeded)
gemstack run step3-build --feature "..." --max-cost 5.00

# Set a per-step token limit
gemstack run step3-build --feature "..." --max-tokens 500000
```

When a limit is exceeded, Gemstack raises a `CostLimitExceeded` error with a clear message showing the current spend vs. the limit. You can then either increase the limit or reset costs:

**Note:** Cost limits are opt-in. If you don't specify `--max-cost` or `--max-tokens`, costs are still *recorded* but never *enforced*.

---

## Gemini CLI & Antigravity Integration

Gemstack can be mounted globally alongside your system agent tools, enabling you to use Gemstack's workflows, roles, and phases as slash commands in Gemini CLI and Antigravity.

### Installing Slash Commands

```bash
gemstack install
```

This creates symlinks in the global workflow directory (e.g., `~/.gemini/antigravity/global_workflows/`) for:

| Symlinked Files | Slash Commands Available |
|----------------|------------------------|
| **Workflows** (`step1-spec.md`, etc.) | `/step1-spec`, `/step2-trap`, `/step3-build`, `/step4-audit`, `/step5-ship` |
| **Roles** (`architect.md`, `sdet.md`, etc.) | `/architect`, `/sdet`, `/security-engineer`, `/ml-engineer`, etc. |
| **Phases** (`build.md`, `design.md`, etc.) | `/build`, `/design`, `/ideate`, `/review`, `/test`, etc. |
| **Topologies** (`backend.md`, `frontend.md`, etc.) | `/backend`, `/frontend`, `/ml-ai`, `/infrastructure`, `/library-sdk` |

After installation, you can use these directly in any new conversation:

```
/architect     # Activate the Architect role persona
/step3-build   # Load the Build workflow protocol
/backend       # Inject backend topology guardrails
```

### Uninstalling

```bash
gemstack uninstall   # Removes all symlinks
```

---

## Integration with Other AI Agents

### MCP-Based Integration (Recommended)

For rich, bidirectional integration with Cursor, Claude Desktop, Gemini CLI, and Cline, use the [MCP Server](mcp-server.md). This exposes your project context as resources and actionable tools.

### Manual Integration

If you use an AI tool that doesn't support MCP, you can still use Gemstack by:

1. **Exporting compiled context:**
   ```bash
   gemstack compile step3-build > /tmp/context.md
   ```
   Then paste the output into your agent's system prompt.

2. **Using `gemstack export`:**
   ```bash
   gemstack export --format json > context.json
   ```
   Feed the JSON into tools that accept structured input.

3. **Running drift checks manually:**
   ```bash
   gemstack diff
   gemstack check
   ```
   Copy the output into your agent conversation if drift is detected.

---

## Git Hooks

Gemstack can install git hooks to automatically run drift detection and validation before commits:

```bash
gemstack hook install
```

This installs a `pre-commit` hook that runs:
1. `gemstack check` — Validates `.agent/` integrity
2. `gemstack diff` — Detects context drift

If either check fails, the commit is blocked with a descriptive error message.

```bash
gemstack hook remove   # Remove the installed hooks
```

---

## CI/CD Integration

Generate CI pipeline configuration that includes Gemstack validation:

```bash
gemstack ci generate            # GitHub Actions (default)
gemstack ci generate --gitlab   # GitLab CI
```

The generated pipeline includes:
- Installing Gemstack in CI
- Running `gemstack check` as a quality gate
- Running `gemstack diff` to detect documentation drift
- (Optional) Running `gemstack compile` to validate context compilation

---

## Docker Support

Gemstack ships with a `Dockerfile` for containerized execution:

```bash
docker build -t gemstack .
docker run -v $(pwd):/project gemstack init --ai
```

The Dockerfile:
- Uses a minimal Python base image
- Installs Gemstack with all extras
- Sets `/project` as the working directory
- Runs as a non-root user for security
