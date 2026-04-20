"""gemstack status — Project state dashboard."""

import re
from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def status(
    project_root: Path = typer.Argument(".", help="Project root directory"),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable JSON output"),
) -> None:
    """Display the current Gemstack project status."""
    project_root = project_root.resolve()
    status_path = project_root / ".agent" / "STATUS.md"

    if not status_path.exists():
        console.print(
            Panel(
                "[bold red]No .agent/STATUS.md found.[/bold red]\n\n"
                "[dim]Run `gemstack init` to initialize this project.[/dim]",
                title="❌ No Status",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)

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
        import json

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
            f"[bold cyan]{project_root.name}[/bold cyan]\n"
            f"[dim]State: {state} | {focus}[/dim]",
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
