# Status
[STATE: SHIPPED]

## Current Focus
No active feature. Ready for next cycle.

## Lifecycle Progress
_(No active feature — last completed below.)_

## Release History
| Version | Date | Highlights |
|---------|------|------------|
| v1.1.0 | 2026-04-23 | Migration DX improvements: section-scoped differ, batch/registry CLI, detector expansion |
| v1.0.3 | 2026-04-19 | CI fix: restrict matrix to macOS 3.11, fix Homebrew download |
| v1.0.2 | 2026-04-18 | Bug fixes and stability improvements |
| v1.0.1 | 2026-04-17 | Initial public release fixes |
| v1.0.0 | 2026-04-14 | Initial public release — 28 CLI commands, 5 topologies, MCP server |

## Known Issues
1. `gemstack init` skips entirely if `.agent/` exists (even if missing context files) — target v1.2.0

## Stub Audit Tracker

| Stub Location | Description | Blocked By | Target Removal |
|---------------|-------------|------------|----------------|
| `init_cmd.py:53` | Hard skip when `.agent/` exists | Needs `--force` or partial init | v1.2.0 |
