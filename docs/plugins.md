# Building Custom Plugins

Gemstack uses [pluggy](https://pluggy.readthedocs.io/) for deep extensibility. Plugins can register custom topologies, custom roles, custom validation checks, and intercept compilation and execution events — all without modifying Gemstack's core code.

The Plugin API is **stable and backward-compatible through the entire 1.x release series**. New hooks may be added, but existing signatures will not change.

---

## Prerequisites

Install Gemstack with the plugins extra:

```bash
pipx install 'gemstack[plugins]'
# or
uv tool install 'gemstack[all]'
```

This installs `pluggy>=1.5` alongside Gemstack.

---

## Plugin Architecture

Plugins are standard Python packages that:
1. Import the `hookimpl` marker from `gemstack.plugins.hooks`
2. Define a class with methods decorated by `@hookimpl`
3. Register the class via the `[project.entry-points."gemstack"]` section in their `pyproject.toml`

Gemstack discovers and loads all registered plugins at startup using pluggy's entry-point discovery mechanism.

---

## Available Hooks

### Lifecycle Hooks

These hooks fire during project initialization and autonomous execution:

#### `gemstack_post_init(project_root: Path, profile: ProjectProfile)`

Called after `gemstack init` completes. Use this to:
- Add custom files to the `.agent/` directory
- Post-process the AI-generated context files
- Set up project-specific configuration

```python
from gemstack.plugins.hooks import hookimpl
from pathlib import Path

class MyPlugin:
    @hookimpl
    def gemstack_post_init(self, project_root, profile):
        """Add a custom context file after initialization."""
        custom_file = project_root / ".agent" / "CUSTOM.md"
        custom_file.write_text(
            f"# Custom Context\n\n"
            f"Language: {profile.language}\n"
            f"Framework: {profile.framework}\n"
        )
```

#### `gemstack_pre_run(step: str, feature: str)`

Called before `gemstack run` executes a workflow step. Use this for:
- Pre-execution validation
- Logging and telemetry
- Environment setup

```python
@hookimpl
def gemstack_pre_run(self, step, feature):
    """Log execution start to an external system."""
    print(f"Starting {step} for feature: {feature}")
```

#### `gemstack_post_run(step: str, result: ExecutionResult)`

Called after `gemstack run` completes a step. The `result` parameter is an `ExecutionResult` instance containing:
- `step`, `feature`, `success`, `dry_run`
- `files_written`, `compiled_tokens`, `output_tokens`
- `cost_usd`, `duration_seconds`, `error`, `next_step`

```python
@hookimpl
def gemstack_post_run(self, step, result):
    """Send a Slack notification on step completion."""
    if result.success:
        send_slack(f"✅ {step} completed for '{result.feature}' (${result.cost_usd:.4f})")
    else:
        send_slack(f"❌ {step} failed: {result.error}")
```

### Compilation Hooks

These hooks let you modify the compiled context before and after it's assembled:

#### `gemstack_pre_compile(step: str, sections: list[tuple[str, str]]) -> list[tuple[str, str]]`

Called before the compiler stitches sections together. You receive the full list of `(section_name, content)` tuples and **must return** the (possibly modified) list.

Use cases:
- Inject additional context sections (e.g., company-wide coding standards)
- Remove or filter sections based on custom logic
- Reorder sections for specific steps

```python
@hookimpl
def gemstack_pre_compile(self, step, sections):
    """Inject company coding standards into every step."""
    standards = Path("~/.company/coding-standards.md").expanduser().read_text()
    sections.append(("Company Standards", standards))
    return sections
```

#### `gemstack_post_compile(step: str, compiled: str) -> str`

Called after the full context string is assembled. You receive the compiled string and **must return** the (possibly modified) string.

```python
@hookimpl
def gemstack_post_compile(self, step, compiled):
    """Append a reminder to every compiled context."""
    return compiled + "\n\n## REMINDER: Follow the company coding standards above.\n"
```

### Extension Hooks

These hooks let you register new content types:

#### `gemstack_register_topologies() -> list[dict[str, str]]`

Register custom topology profiles. Each dict must have keys:
- `name` — Topology identifier (e.g., `"mobile"`)
- `description` — Human-readable description
- `content` — Full markdown content of the topology guardrails

```python
@hookimpl
def gemstack_register_topologies(self):
    return [{
        "name": "mobile",
        "description": "iOS and Android native development",
        "content": (
            "# Mobile Topology Guardrails\n\n"
            "## Platform Parity\n"
            "Every feature must work on both iOS and Android.\n\n"
            "## Offline First\n"
            "All core features must work without network connectivity.\n"
        ),
    }]
```

#### `gemstack_register_roles() -> list[dict[str, str]]`

Register custom role definitions. Same dict structure as topologies:

```python
@hookimpl
def gemstack_register_roles(self):
    return [{
        "name": "accessibility-engineer",
        "description": "Accessibility specialist",
        "content": "# Accessibility Engineer\n\nYou are an accessibility expert...",
    }]
```

#### `gemstack_register_checks() -> list[Callable[..., Any]]`

Register custom validation checks for `gemstack check`. Each callable receives a `project_root: Path` and returns a list of error strings (empty if the check passes):

```python
@hookimpl
def gemstack_register_checks(self):
    def check_changelog(project_root):
        if not (project_root / "CHANGELOG.md").exists():
            return ["Missing CHANGELOG.md — required by company policy"]
        return []

    return [check_changelog]
```

---

## Registering Your Plugin

Package your plugin as a standard Python package and register it via entry points in your `pyproject.toml`:

```toml
[project]
name = "gemstack-mobile"
version = "0.1.0"
dependencies = ["gemstack"]

[project.entry-points."gemstack"]
mobile = "gemstack_mobile:MobilePlugin"
```

Where `gemstack_mobile/__init__.py` contains:

```python
from gemstack.plugins.hooks import hookimpl

class MobilePlugin:
    @hookimpl
    def gemstack_register_topologies(self):
        return [{
            "name": "mobile",
            "description": "iOS/Android",
            "content": "...",
        }]

    @hookimpl
    def gemstack_post_init(self, project_root, profile):
        (project_root / ".agent" / "MOBILE.md").write_text("# Mobile Context")
```

After installing the plugin package (`pip install gemstack-mobile`), Gemstack will automatically discover and load it.

---

## Plugin API Version

You can check the plugin API version for compatibility:

```python
from gemstack.plugins.hooks import PLUGIN_API_VERSION

print(PLUGIN_API_VERSION)  # "1.0"
```

The `PLUGIN_API_VERSION` is `"1.0"` and is guaranteed stable through the 1.x release series. Third-party plugins can check this value to verify they're running against a compatible Gemstack installation.

---

## Graceful Degradation

If `pluggy` is not installed (i.e., the user installed `gemstack` without the `plugins` extra), all hook markers become no-ops. The `gemstack.plugins.hooks` module can still be imported — the `@hookspec` and `@hookimpl` decorators simply pass through without effect. This means:

- Plugin code can live in your project without causing import errors
- Users who don't need plugins pay no performance penalty
- The plugin system is entirely opt-in
