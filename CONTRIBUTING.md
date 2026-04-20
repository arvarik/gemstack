# Contributing to Gemstack

Thank you for your interest in contributing to Gemstack! This document provides
guidelines and instructions for contributing.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold this code.

## Development Setup

### Prerequisites

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Getting Started

```bash
# Clone the repository
git clone https://github.com/arvarik/gemstack.git
cd gemstack

# Create a virtual environment and install dependencies
uv sync --all-extras

# Run the test suite
uv run pytest

# Run linting and type checking
uv run ruff check src/ tests/
uv run mypy src/gemstack
```

### Running Gemstack Locally (Editable Install)

```bash
uv pip install -e ".[all]"
gemstack --version
```

## Making Changes

### Branch Naming

- `feat/<description>` — New features
- `fix/<description>` — Bug fixes
- `docs/<description>` — Documentation changes
- `refactor/<description>` — Code refactoring (no behavior change)

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/). **This is strictly enforced** as Gemstack uses Google's Release Please automation to parse commit messages for version bumping and changelog generation.

```
feat: add MCP server stdio transport
fix: handle malformed package.json in detector
docs: add plugin development guide
test: add fixtures for Go project detection
```

### Code Style

- **Formatter/Linter**: [Ruff](https://docs.astral.sh/ruff/) — configured in `pyproject.toml`
- **Type checker**: [mypy](https://mypy-lang.org/) in strict mode
- **Line length**: 100 characters
- **Docstrings**: Google-style
- Run `uv run ruff check --fix src/ tests/` to auto-fix lint issues

### Testing Requirements

- All new code must have corresponding tests
- Tests must pass on Python 3.11+ (CI runs on Ubuntu + macOS with 3.11 and 3.13)
- Maintain ≥80% coverage for `core/` modules
- Use `tmp_path` for all filesystem operations — never write outside temp dirs

### Pull Request Process

1. Fork the repository and create your branch from `main`
2. Add tests for any new functionality
3. Ensure all checks pass: `uv run pytest && uv run ruff check && uv run mypy src/gemstack`
4. Submit a pull request with a clear description

### Developer Certificate of Origin (DCO)

By contributing to this project, you certify that your contribution was
created in whole or in part by you and you have the right to submit it
under the Apache 2.0 license.

Sign your commits with `git commit -s` to add a DCO sign-off line.

## Plugin Development

See [Building Custom Plugins](docs/plugins.md) for details on creating Gemstack plugins.

## Reporting Issues

- **Bugs**: Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Features**: Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
- **Security**: See [SECURITY.md](SECURITY.md) for vulnerability reporting
