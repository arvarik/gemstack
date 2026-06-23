"""gemstack config — Configuration management CLI command."""

from __future__ import annotations

from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()

config_app = typer.Typer(name="config", help="Manage global Gemstack settings")

# Valid config keys and their descriptions
_VALID_KEYS = {
    "gemini-api-key": "Gemini API key for AI-powered bootstrapping",
    "default-model": (
        "Default Gemini model (e.g., gemini-3.1-pro-preview)"
    ),
    "default-topology": "Default topology for new projects (comma-separated)",
    "custom-templates-dir": "Path to custom template directory",
    "copy-mode": "Use file copy instead of symlinks (true/false)",
}

# Map CLI key names to GemstackConfig attribute names
_KEY_MAP = {
    "gemini-api-key": "gemini_api_key",
    "default-model": "default_model",
    "default-topology": "default_topology",
    "custom-templates-dir": "custom_templates_dir",
    "copy-mode": "copy_mode",
}


def _mask_value(key: str, value: Any) -> str:
    """Mask configuration value if it appears to be an API key."""
    raw_value = str(value)
    if "api-key" in key.lower():
        if len(raw_value) > 8:
            return raw_value[:4] + "..." + raw_value[-4:]
        return "********"
    return raw_value


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
) -> None:
    """Set a global configuration value."""
    from gemstack.project.config import GemstackConfig

    if key not in _VALID_KEYS:
        console.print(
            f"[red]❌ Unknown config key: '{key}'[/red]\n"
            f"[dim]Valid keys: {', '.join(_VALID_KEYS.keys())}[/dim]"
        )
        raise typer.Exit(code=1)

    config = GemstackConfig.load()
    attr_name = _KEY_MAP[key]

    # Type conversion
    if attr_name == "copy_mode":
        setattr(config, attr_name, value.lower() in ("true", "1", "yes"))
    elif attr_name == "default_topology":
        setattr(config, attr_name, [t.strip() for t in value.split(",")])
    elif attr_name == "gemini_api_key":
        from pydantic import SecretStr

        setattr(config, attr_name, SecretStr(value))
    else:
        setattr(config, attr_name, value)

    config.save()

    display_value = _mask_value(key, value)

    console.print(f"[green]✅ Set {key} = {display_value}[/green]")
    console.print(f"[dim]Saved to {GemstackConfig.config_path()}[/dim]")


@config_app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Configuration key"),
) -> None:
    """Get a global configuration value."""
    from gemstack.project.config import GemstackConfig

    if key not in _VALID_KEYS:
        console.print(
            f"[red]❌ Unknown config key: '{key}'[/red]\n"
            f"[dim]Valid keys: {', '.join(_VALID_KEYS.keys())}[/dim]"
        )
        raise typer.Exit(code=1)

    config = GemstackConfig.load()
    attr_name = _KEY_MAP[key]

    # Use safe accessor for API key
    if attr_name == "gemini_api_key":
        raw_value = config.get_api_key()
    else:
        raw_value = getattr(config, attr_name)

    if raw_value is None:
        console.print(f"[dim]{key}: (not set)[/dim]")
    else:
        display_value = _mask_value(key, raw_value)
        console.print(f"{key}: {display_value}")


@config_app.command("list")
def config_list() -> None:
    """List all configuration values."""
    from gemstack.project.config import GemstackConfig

    config = GemstackConfig.load()

    table = Table(title="Gemstack Configuration", show_header=True)
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_column("Description", style="dim")

    for key, description in _VALID_KEYS.items():
        attr_name = _KEY_MAP[key]

        # Use safe accessor for API key
        if attr_name == "gemini_api_key":
            raw_value = config.get_api_key()
        else:
            raw_value = getattr(config, attr_name)

        if raw_value is None:
            display_value = "[dim](not set)[/dim]"
        else:
            display_value = _mask_value(key, raw_value)

        table.add_row(key, display_value, description)

    console.print(table)
    console.print(f"\n[dim]Config file: {GemstackConfig.config_path()}[/dim]")
