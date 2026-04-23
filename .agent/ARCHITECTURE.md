# Architecture

_This document acts as the definitive anchor for understanding system design, data models, API contracts, and technology boundaries. Update this document during the Design and Review phases._

## 0. Project Topology

**Topology:** `[library-sdk]`

_Agents: Read the corresponding Gemstack topology profile (`library-sdk.md`) from `~/.gemini/antigravity/global_workflows/` before proceeding with any workflow step. This profile enforces API surface stability, backward compatibility, semver enforcement, documentation coverage, and dependency minimalism._

## 1. System Overview

**Name:** `gemstack`
**Repository:** `github.com/arvarik/gemstack`
**Description:** Opinionated AI agent orchestration framework for Gemini CLI and Antigravity. Provides architectural memory (`.agent/` context files), topology-aware guardrails, a 5-step lifecycle, and an autonomous executor — all exposed via a CLI and MCP server.
**Published to:** [PyPI](https://pypi.org/project/gemstack/) (`pipx install gemstack`)

## 2. Tech Stack & Dependencies

### Language & Runtime
- **Python:** `>=3.10` (supports 3.10, 3.11, 3.12, 3.13)
- **Build system:** Hatchling + hatch-vcs (dynamic version from git tags)

### Core Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `typer` | `>=0.12` | CLI framework (28 commands) |
| `rich` | `>=13.0` | Terminal output formatting |
| `jinja2` | `>=3.1` | Template rendering for `.agent/` files |
| `pyyaml` | `>=6.0` | YAML frontmatter parsing in workflows |
| `pydantic` | `>=2.0` | Data validation and settings |
| `platformdirs` | `>=4.0` | Cross-platform config directories |
| `tomli-w` | `>=1.0` | TOML writing |
| `tomli` | `>=2.0` | TOML parsing (only on Python <3.11) |

### Optional Dependencies (Extras)
| Extra | Packages | Purpose |
|-------|----------|---------|
| `ai` | `google-genai>=1.0` | AI-powered project bootstrapping via Gemini |
| `mcp` | `mcp>=1.0` | Model Context Protocol server for IDE integration |
| `tail` | `textual>=0.50`, `watchdog>=4.0` | Live TUI dashboard |
| `plugins` | `pluggy>=1.5` | Plugin hook system |

### Dev Dependencies
- `pytest>=8.0`, `pytest-cov>=5.0`, `pytest-asyncio>=0.24`
- `mypy>=1.10`, `ruff>=0.4`

## 3. Project Layout

```
gemstack/
├── .agent/
│   └── workflows/            # Distributed slash command files (28 files)
├── .github/workflows/
│   ├── ci.yml                # CI: lint, type-check, test (macOS + Ubuntu matrix)
│   └── update-formula.yml    # Homebrew formula auto-update on release
├── src/gemstack/
│   ├── __init__.py
│   ├── _version.py           # Auto-generated version from git tags
│   ├── errors.py             # Structured error types (GemstackError hierarchy)
│   ├── py.typed              # PEP 561 marker
│   ├── adapters/             # External service adapters
│   ├── ai/                   # AI-powered analysis (Gemini API)
│   ├── cli/                  # Typer CLI commands (28 command modules)
│   │   ├── main.py           # App entrypoint, command registration
│   │   ├── context.py        # Shared Rich console
│   │   ├── check_cmd.py      # Project validation
│   │   ├── compile_cmd.py    # Context compilation
│   │   ├── config_cmd.py     # Global config management
│   │   ├── diff_cmd.py       # Context drift detection
│   │   ├── doctor_cmd.py     # Environment diagnostics
│   │   ├── hook_cmd.py       # Git hook management
│   │   ├── init_cmd.py       # Project bootstrapping
│   │   ├── install_cmd.py    # Global workflow symlinks
│   │   ├── migrate_cmd.py    # Topology migration
│   │   ├── route_cmd.py      # Phase routing
│   │   ├── run_cmd.py        # Autonomous executor
│   │   ├── start_cmd.py      # Feature lifecycle start
│   │   └── ...               # 14 more command modules
│   ├── data/                 # Bundled data (topology profiles, templates)
│   ├── mcp/                  # MCP server implementation
│   ├── orchestration/        # Lifecycle orchestration engine
│   ├── platform/             # Platform abstractions (worktree, OS)
│   ├── plugins/              # Pluggy-based hook system
│   ├── project/              # Project analysis modules
│   │   ├── config.py         # Project config loading
│   │   ├── detector.py       # Tech stack & topology auto-detection
│   │   ├── migrator.py       # Topology migration engine
│   │   ├── scaffolder.py     # Code scaffolding
│   │   ├── templates.py      # .agent/ file template rendering
│   │   └── validator.py      # .agent/ integrity validation
│   ├── templates/            # Jinja2 templates for .agent/ files
│   ├── tui/                  # Textual TUI (tail dashboard)
│   └── utils/
│       ├── differ.py         # Context drift analysis engine
│       └── fileutil.py       # Atomic file write utilities
├── tests/                    # pytest suite (30 test modules)
├── docs/                     # User-facing documentation (8 guides)
├── Formula/                  # Homebrew formula
├── pyproject.toml            # Package metadata, deps, tool configs
├── CHANGELOG.md              # Release changelog
├── LICENSE                   # Apache-2.0
└── README.md                 # User-facing docs with architecture diagram
```

## 4. Key Modules & Data Flow

### CLI Entry Point
`src/gemstack/cli/main.py` registers all commands via Typer. Entry point: `gemstack.cli.main:app` (declared in `pyproject.toml`).

### Project Detector (`project/detector.py`)
Scans the filesystem to produce a `ProjectProfile` dataclass:
- Detects language, runtime, framework, package manager from manifest files
- Infers topologies from dependency sets (frontend/backend/ml-ai/infrastructure/library-sdk)
- Discovers legacy context files (.cursorrules, GEMINI.md, etc.)

### Context Differ (`utils/differ.py`)
Compares `.agent/` documentation against codebase reality:
1. **Dependency drift**: manifest deps vs ARCHITECTURE.md backtick references
2. **Env var drift**: `.env.example` keys vs ARCHITECTURE.md backtick references
3. **Stale file refs**: STATUS.md file paths vs filesystem

### Topology Migrator (`project/migrator.py`)
Upgrades existing projects with topology-specific sections:
- Inserts `**Topology:** [...]` declaration into ARCHITECTURE.md
- Appends testing matrices to TESTING.md
- Appends tracking sections to STATUS.md

### Autonomous Executor (`cli/run_cmd.py`)
Compiles context → calls Gemini API → parses structured response → writes files atomically → tracks costs.

## 5. Configuration

Global config stored at `~/.config/gemstack/config.toml` (via `platformdirs`).

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `api-key` | For AI features | — | Gemini API key |
| `model` | No | `gemini-2.5-flash` | Default model for AI operations |

## 6. CI/CD Pipeline

### GitHub Actions (`ci.yml`)
**Triggers:** Push to `main`, PRs targeting `main`
**Matrix:** macOS-latest × Python 3.11
**Steps:** checkout → setup-python → uv install → ruff check → mypy → pytest

### Homebrew Formula
Auto-updated on new GitHub releases via `update-formula.yml`.

## 7. Safety Invariants & Architectural Rules

- **NEVER** write to disk without atomic file operations (`utils/fileutil.write_atomic`)
- **NEVER** allow AI-generated file paths outside the project root (path traversal prevention in executor)
- **ALWAYS** use `py.typed` marker and maintain type annotations on all public APIs
- **ALWAYS** support Python 3.10+ (no walrus operator in hot paths, conditional `tomllib` import)
- **NEVER** add runtime dependencies without justification — extras system exists for optional features
- **ALWAYS** wrap manifest parsing in try/except — never crash on malformed user projects
- **ALWAYS** use structured error types from `errors.py` — never raise bare exceptions
