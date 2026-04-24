# MCP Server & IDE Integration

Gemstack ships with a built-in **Model Context Protocol (MCP)** server that exposes your project's `.agent/` context, actionable tools, and workflow prompts to any MCP-compatible AI agent — including Cursor, Claude Desktop, Gemini CLI, and Cline.

This means your IDE agent automatically has access to your architecture, can trigger drift detection, compile step-specific context, check project status, and even execute workflow steps — all without leaving your editor.

---

## Prerequisites

Install Gemstack with the MCP extra:

```bash
pipx install 'gemstack[mcp]'
# or
uv tool install 'gemstack[ai,mcp]'
```

This installs the `mcp` SDK (FastMCP) alongside Gemstack.

---

## Running the Server

### stdio Mode (Default)

Standard I/O transport — the agent launches gemstack as a subprocess and communicates via stdin/stdout. This is the most common mode for IDE integrations:

```bash
gemstack mcp serve
```


### SSE Mode (Network)

Server-Sent Events transport — exposes the MCP server over HTTP for network-accessible agents or multi-client setups:

```bash
gemstack mcp serve --transport sse --port 8765
```

This starts an HTTP server at `http://localhost:8765` that any MCP client can connect to. Useful for:
- Remote development environments
- Multiple agents connecting to the same project context
- Docker-based agent setups

---

## Registering with IDEs

Gemstack can automatically inject its MCP server configuration into your IDE's agent settings. Run the registration commands for your tools:

```bash
# Register with Cursor (project-local — writes to .cursor/mcp.json)
gemstack mcp register --cursor

# Register with Claude Desktop (writes to platform-specific config)
gemstack mcp register --claude-desktop
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Linux: ~/.config/claude/claude_desktop_config.json
# Windows: %APPDATA%/Claude/claude_desktop_config.json

# Register with Gemini CLI (writes to ~/.gemini/settings.json)
gemstack mcp register --gemini-cli

# Register with Cline (VS Code extension — writes to globalStorage config)
gemstack mcp register --cline
# macOS: ~/Library/Application Support/Code/User/globalStorage/
#         saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```
Each registration command creates or updates the `mcpServers` section in the target config file, adding a `"gemstack"` entry with the command `gemstack mcp serve --transport stdio`.

You can register with multiple agents simultaneously — they all point to the same gemstack installation.

---

## What the Server Exposes

### Resources (Read-Only Context)

The MCP server exposes all `.agent/` markdown files as read-only resources via the `gemstack://agent/{filename}` URI scheme:

| Resource URI | Content |
|-------------|---------|
| `gemstack://agent/ARCHITECTURE.md` | Tech stack, API contracts, data models, system boundaries |
| `gemstack://agent/STYLE.md` | Coding conventions, design tokens, forbidden patterns |
| `gemstack://agent/TESTING.md` | Test strategy, commands, scenario tables, coverage matrices |
| `gemstack://agent/PHILOSOPHY.md` | Product soul, core beliefs, decision principles |
| `gemstack://agent/STATUS.md` | Current lifecycle state, active feature, blocking issues |

**Security:** All resource reads are validated against path traversal attacks — the resolved path must remain within the `.agent/` directory. Requests like `gemstack://agent/../../../etc/passwd` are rejected with a `PermissionError`.

### Tools (Actionable Operations)

The following tools are exposed for IDE agents to call:

| Tool | Description | Return Value |
|------|-------------|-------------|
| `gemstack_status` | Get the current project status | Full `STATUS.md` content |
| `gemstack_route` | Get the recommended next action | Action, next command, and reasoning |
| `gemstack_compile(step, max_tokens?)` | Compile the full context prompt for a step | The compiled prompt string |
| `gemstack_check` | Validate `.agent/` directory integrity | Pass/fail with error list |
| `gemstack_diff` | Detect context drift vs. codebase | Drift report in markdown |
| `gemstack_run(step, feature, dry_run?)` | Execute or dry-run a workflow step | Execution result summary |
| `gemstack_costs(feature?)` | Get cost tracking data for API usage | Cost summary with breakdowns |

**Example interaction in Cursor:**
When your Cursor agent encounters an architecture question, it can call `gemstack_compile("step3-build")` to get the full compiled context with all roles, phases, topology guardrails, and project files — giving it the exact same context that `gemstack run` would use.

**`gemstack_run` Tool:**
This async-safe tool orchestrates the full execution pipeline (compile context → check costs → call Gemini → write files → record costs). The `dry_run=True` parameter (default) lets agents preview what would happen without making an API call — perfect for cost estimation and context size checks.

### Prompts (Reusable Workflow Templates)

All 5 workflow step templates are exposed as reusable MCP prompts:

| Prompt | Description |
|--------|-------------|
| `step1_spec` | Step 1 — Define the feature and lock in contracts |
| `step2_trap` | Step 2 — Write the task plan and failing test suite |
| `step3_build` | Step 3 — Implement until all tests pass |
| `step4_audit` | Step 4 — Security and logic review |
| `step5_ship` | Step 5 — Integrate, merge, deploy |

These prompts contain the full workflow definitions including role composition, process steps, accuracy checks, circuit breaker rules, and the routing protocol.

---

## Usage Patterns

### Pattern 1: Context-Aware Coding in Cursor

After registering, your Cursor agent can:
1. Read `gemstack://agent/ARCHITECTURE.md` to understand your stack before writing code
2. Call `gemstack_route` to determine what step you should be working on
3. Call `gemstack_check` to validate the project setup before starting work
4. Call `gemstack_diff` to detect if any documentation is stale

### Pattern 2: Autonomous Execution in Claude Desktop

Claude Desktop can use the `gemstack_run` tool to:
1. Dry-run a step to see the compiled context and estimated token usage
2. Execute the step fully — compiling context, calling Gemini, and writing results

### Pattern 3: Drift Detection in CI

Run the MCP server in SSE mode and connect a CI agent to periodically check for drift:
```bash
gemstack mcp serve --transport sse --port 8765 &
# CI agent connects and calls gemstack_diff periodically
```

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `mcp` import error | Install with: `pipx install 'gemstack[mcp]'` |
| Agent can't find `gemstack` command | Ensure `gemstack` is on your `$PATH`. With `pipx`, run `pipx ensurepath` |
| Registration doesn't take effect | Restart your IDE after running `gemstack mcp register` |
| SSE server won't start | Check if the port is already in use: `lsof -i :8765` |
| Path traversal error | This is expected — the server is blocking an unsafe resource request |
