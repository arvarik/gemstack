# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] — 2026-04-20

### Fixed

- Restrict CI test matrix purely to macOS + Python 3.11 to resolve environment flakes.
- Fix Homebrew `update-formula.yml` dynamically polling PyPI JSON for sdist hashed URL distributions resolving 404 errors.

## [1.0.2] — 2026-04-20

### Fixed

- Resolved test suite formatting violations and MyPy strictness errors mapping to `SecretStr` overrides and generator yields across tests and `tail_app`.
- Hardened autonomous testing assertions (`test_executor.py`) to bypass unmanaged `.agent/` path resolutions correctly.
- Aligned wildcard and disjoint Python imports globally via Ruff tracking 100% format compliance.

### Changed

- Refactored `gemstack.core` layer explicitly into `orchestration`, `platform`, `project`, and `utils` for strict domain separation.

## [1.0.1] — 2026-04-20

### Fixed

- Fix 15 CI test failures caused by `.gitignore` excluding test fixture `.agent/` directories.
- Fix mypy `import-not-found` errors for `tomllib` by replacing `try/except` with `sys.version_info` guards.
- Remove stale `noqa` comments from `worktree.py` after global ruff rule updates.
- Fix unused variable in `doctor_cmd.py`.

### Changed

- Simplify CI to macOS + Python 3.11 only (removed 12-job matrix).
- Upgrade README badges with `flat-square` style, logos, and CI status badge.
- Fix ASCII architecture diagram and 5-step lifecycle alignment in README.
- Add GitHub Release and Homebrew formula auto-update workflows.
- Update author info, security contact, and development status to Beta.

## [1.0.0] — 2026-04-20

### Added

- **CLI Framework**: 28 commands built with Typer + Rich, covering the full 5-step lifecycle (Spec → Trap → Build → Audit → Ship).
- **Context Compiler**: Deterministic Jinja2-based prompt stitching engine with token budgeting and truncation priorities.
- **Phase Router**: Filesystem-driven state machine that reads `STATUS.md` to recommend the next workflow step.
- **Project Detector**: Automatic detection of language, framework, topology, and package manager from project manifests.
- **Drift Detector**: Compares `.agent/` documentation against actual dependency and environment state.
- **AI Bootstrapping**: Gemini-powered codebase analysis to auto-populate `.agent/` files (`gemstack init --ai`).
- **MCP Server**: Model Context Protocol server with stdio/SSE transport for agent interoperability.
- **Plugin System**: Pluggy-based hook architecture with stable v1.0 API (topologies, roles, compilation hooks, lifecycle hooks).
- **Process Registry**: Background process tracking with signal handlers, atomic persistence, and PID lifecycle management.
- **Cost Tracker**: API token usage tracking with configurable circuit breaker budgets per feature and per step.
- **Worktree Manager**: Parallel git worktree creation for concurrent step execution.
- **TUI Dashboard**: Live `gemstack tail` monitor built with Textual + watchdog filesystem watching.
- **Export Adapters**: Context export to Cursor (`.cursorrules`), Claude (`CLAUDE.md`), and Gemini (`GEMINI.md`) formats.
- **Topology Guardrails**: Built-in profiles for backend, frontend, ML/AI, infrastructure, and library/SDK topologies.
- **Docker Support**: Multi-stage Dockerfile for containerized execution.
- **Shell Completion**: Auto-generated completion for bash, zsh, and fish via Typer.

### Security

- Path traversal protection on all file write operations (executor) and MCP resource reads.
- API keys stored using Pydantic `SecretStr` with masked display output.
- Atomic file writes via temp-file-then-rename pattern to prevent data corruption.
- Non-root user in Docker container.
