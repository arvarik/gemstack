# Style Guide

_Coding conventions for the gemstack codebase. Agents and developers: follow these rules for all code changes._

## Language: Python

### Formatting & Linting
- **Formatter:** Ruff (`ruff format`)
- **Linter:** Ruff (`ruff check`)
- **Type checker:** mypy (`mypy --strict`)
- **Line length:** 100 characters (configured in `pyproject.toml`)

### Naming Conventions
| Item | Convention | Example |
|------|-----------|---------|
| Modules | `snake_case` | `diff_cmd.py`, `route_cmd.py` |
| Classes | `PascalCase` | `ProjectDetector`, `TopologyMigrator` |
| Functions / Methods | `snake_case` | `detect_go()`, `_extract_env_vars()` |
| Constants | `UPPER_SNAKE_CASE` | `_BACKEND_GO_DEPS`, `_TESTING_MATRICES` |
| CLI commands | `kebab-case` (via Typer) | `gemstack hook install` |
| Private members | `_leading_underscore` | `_detect_node()`, `_HOOKS` |

### CLI Command Module Pattern
Every command lives in `src/gemstack/cli/{name}_cmd.py`:
```python
"""gemstack {name} — {Short description}."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from gemstack.cli.context import console


def command_name(
    project_root: Annotated[Path, typer.Argument(...)],
    flag: Annotated[bool, typer.Option("--flag", help="...")] = False,
) -> None:
    """Docstring becomes --help text."""
    ...
```

### Import Conventions
- `from __future__ import annotations` at the top of every module
- Use `TYPE_CHECKING` guard for type-only imports
- Lazy imports for heavy modules (e.g., `google.genai`) — import inside the function body
- Group imports: stdlib → third-party → local

### Error Handling
- Use structured errors from `gemstack.errors` (`GemstackError`, `ValidationError`, `ConfigError`)
- Never raise bare `Exception` or `RuntimeError`
- Wrap all manifest parsing (`package.json`, `pyproject.toml`, `go.mod`) in try/except — never crash on malformed user files

### Type Annotations
- All public functions must have full type annotations
- Use `Annotated` for CLI parameters (Typer convention)
- Use `X | None` (not `Optional[X]`) on Python 3.10+ compatible code
- Maintain `py.typed` marker — this is a PEP 561 typed package

### Testing Conventions
- Framework: `pytest` with `pytest-asyncio` for async tests
- Fixtures live in `tests/conftest.py` and `tests/fixtures/`
- Test files mirror source: `test_{module_name}.py`
- Use `tmp_path` fixture for filesystem tests — never write to repo
- No mocking of internal gemstack modules — mock only external APIs

### Docstrings
- Module-level docstrings on every `.py` file
- Class-level docstrings describing purpose and usage
- Function docstrings with Args/Returns for public APIs
- Use imperative mood: "Detect project profile" not "Detects project profile"

## Commit Messages
```
type(scope): short description

Longer body if needed.
```

Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`
Scopes: `cli`, `detector`, `differ`, `migrator`, `mcp`, `tui`, `plugins`
