"""gemstack status — Project state dashboard."""

import json
import re
from pathlib import Path
from typing import Annotated

import typer
from rich import box
from rich.panel import Panel
from rich.table import Table

from gemstack.cli.context import console
from gemstack.errors import ProjectError


def status(
    project_root: Annotated[
        Path, typer.Argument(help="Project root directory", resolve_path=True)
    ] = Path("."),
    json_output: Annotated[
        bool, typer.Option("--json", help="Machine-readable JSON output")
    ] = False,
) -> None:
    """Display the current Gemstack project status."""
    status_path = project_root / ".agent" / "STATUS.md"

    if not status_path.exists():
        raise ProjectError(
            "No .agent/STATUS.md found.",
            suggestion="Run `gemstack init` to initialize this project.",
        )

    content = status_path.read_text()

    # Parse state
    state_match = re.search(r"\[STATE:\s*(\w+)\]", content)
    state = state_match.group(1) if state_match else "UNKNOWN"

    # Parse current focus
    focus_match = re.search(r"## Current Focus\s*\n\s*(.+)", content)
    focus = focus_match.group(1).strip() if focus_match else "No active feature"

    # Parse lifecycle checkboxes
    phases: dict[str, bool] = {}
    for phase_name in ["Spec", "Trap", "Build", "Audit", "Ship"]:
        checked = re.search(rf"\[x\]\s*{phase_name}", content, re.IGNORECASE)
        phases[phase_name] = bool(checked)

    if json_output:
        data = {
            "state": state,
            "focus": focus,
            "phases": phases,
            "project_root": str(project_root),
        }
        console.print(json.dumps(data, indent=2))
        return

    # Render beautiful dashboard
    console.print(
        Panel(
            f"[bold cyan]{project_root.name}[/bold cyan]\n[dim]State: {state} | {focus}[/dim]",
            title="🏗️ Gemstack Status",
            border_style="cyan",
            box=box.DOUBLE,
        )
    )

    # Phase progress
    table = Table(title="Feature Lifecycle", box=box.ROUNDED)
    table.add_column("Phase", style="bold")
    table.add_column("Status", justify="center")
    for phase_name, completed in phases.items():
        icon = "✅" if completed else "⬜"
        table.add_row(phase_name, icon)
    console.print(table)
    console.print()

    # API Key verification
    import os

    from gemstack.project.config import GemstackConfig

    config = GemstackConfig.load()
    api_key = (
        config.get_api_key()
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )

    if api_key:
        console.print("[green]✅ API Key configured[/green]")
    else:
        console.print(
            "[yellow]⚠️  No Gemini API key found.[/yellow]\n"
            "   [dim]To use AI features, run:[/dim]\n"
            "   [bold cyan]gemstack config set gemini-api-key <YOUR_KEY>[/bold cyan]"
        )
