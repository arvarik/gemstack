# Testing

_Testing strategy, coverage requirements, and topology-specific matrices for the gemstack project._

## Test Stack
| Tool | Purpose |
|------|---------|
| `pytest` | Test runner |
| `pytest-cov` | Coverage reporting |
| `pytest-asyncio` | Async test support |
| `ruff` | Linting (ruff check) |
| `mypy` | Static type checking (strict mode) |

## Running Tests
```bash
uv run pytest                        # Full suite
uv run pytest tests/test_differ.py   # Single module
uv run pytest -x -v                  # Stop on first failure, verbose
uv run ruff check .                  # Lint
uv run mypy .                        # Type check
```

## CI Pipeline
- **Matrix:** macOS-latest × Python 3.11
- **Steps:** ruff check → mypy → pytest
- **Trigger:** Push to main, PRs targeting main

## Test Categories

### Unit Tests
| Module | Test File | What It Covers |
|--------|-----------|----------------|
| `detector.py` | `test_detector.py` | Topology auto-detection from manifests |
| `differ.py` | `test_differ.py` | Context drift detection accuracy |
| `migrator.py` | `test_migrator.py` | Topology migration idempotency |
| `validator.py` | `test_cli.py` | `.agent/` integrity checking |
| `errors.py` | `test_errors.py` | Structured error hierarchy |
| `templates.py` | `test_templates.py` | Template rendering |
| `config.py` | `test_config.py` | Config loading/saving |

### CLI Integration Tests
| Command | Test File | What It Covers |
|---------|-----------|----------------|
| `init` | `test_bootstrap.py` | End-to-end project initialization |
| `check` | `test_cli.py` | Validation with real `.agent/` dirs |
| `doctor` | `test_cli.py` | Environment diagnostic checks |
| `hook` | `test_hook.py` | Git hook install/uninstall |
| `route` | `test_router.py` | Phase routing logic |
| `compile` | `test_compiler.py` | Context compilation |
| `run` | `test_run_cmd.py` | Autonomous execution pipeline |
| `snapshot` | `test_snapshot.py` | Snapshot create/restore |
| `scaffold` | `test_scaffold.py` | Code scaffolding |
| `matrix` | `test_matrix.py` | Cross-project scanning |
| `ci` | `test_ci.py` | CI config generation |
| `mcp` | `test_mcp.py` | MCP server registration |
| `worktree` | `test_worktree.py` | Git worktree management |
| `batch` | `test_v110_contracts.py` | Multi-project batch execution |
| `registry` | `test_v110_contracts.py` | Project registry management |

### Mandatory Test Rules
1. **No mocking of internal gemstack modules** — mock only external APIs (Gemini, filesystem edges)
2. **All filesystem tests use `tmp_path`** — never write to the real repo during tests
3. **CLI tests verify exit codes** — not just stdout content
4. **Detector tests cover all 5 language families** — Node.js, Python, Go, Rust, infrastructure

### API Surface Coverage

| Export | Unit Test | Type Test | Doc Example | Breaking Change Guard |
|-------|-----------|-----------|-------------|----------------------|
| `gemstack init` | ✅ | ✅ | ✅ | — |
| `gemstack check` | ✅ | ✅ | ✅ | — |
| `gemstack diff` | ✅ | ✅ | ✅ | — |
| `gemstack migrate` | ✅ | ✅ | ✅ | — |
| `gemstack route` | ✅ | ✅ | ✅ | — |
| `gemstack hook` | ✅ | ✅ | ✅ | — |
| `ProjectDetector` | ✅ | ✅ | — | — |
| `ContextDiffer` | ✅ | ✅ | — | — |
| `TopologyMigrator` | ✅ | ✅ | — | — |
| Plugin hooks | ✅ | ✅ | ✅ | — |
