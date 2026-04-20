"""Centralized CLI context and error handling for Gemstack."""

from dataclasses import dataclass
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from gemstack.errors import GemstackError

# Shared console instances
console = Console()
err_console = Console(stderr=True)


@dataclass
class CliContext:
    """Global CLI state populated by the root command."""

    project_root: Path
    verbose: bool
    debug: bool


def handle_error(error: Exception) -> None:
    """Display a structured error with suggestion.

    CLI commands should raise GemstackError derivatives. This function
    ensures consistent error presentation per spec §5.3.
    """
    if isinstance(error, GemstackError):
        content = f"[bold red]{error}[/bold red]"
        if error.suggestion:
            content += f"\n\n[dim]{error.suggestion}[/dim]"
        err_console.print(Panel(content, title="❌ Error", border_style="red"))
    else:
        err_console.print(f"[red]Error: {error}[/red]")

    # We use sys.exit instead of typer.Exit to completely abort,
    # ensuring it acts globally if registered as a broader exception handler.
    # But typer.Exit is standard inside Typer context.
    raise typer.Exit(code=1)
