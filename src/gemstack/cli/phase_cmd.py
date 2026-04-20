"""gemstack phase — Phase transition CLI command."""

from __future__ import annotations

import re
from pathlib import Path

import typer
from rich.console import Console

console = Console()

# Valid phases and their state mappings
_PHASE_STATES = {
    "spec": "IN_PROGRESS",
    "trap": "IN_PROGRESS",
    "build": "READY_FOR_BUILD",
    "audit": "READY_FOR_AUDIT",
    "ship": "READY_FOR_SHIP",
}

_PHASE_CHECKBOXES = {
    "spec": "Spec",
    "trap": "Trap",
    "build": "Build",
    "audit": "Audit",
    "ship": "Ship",
}


def phase(
    phase_name: str = typer.Argument(
        ..., help="Phase to transition to (spec, trap, build, audit, ship)"
    ),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Advance or switch the active project phase."""
    project_root = project_root.resolve()

    phase_key = phase_name.lower()
    if phase_key not in _PHASE_STATES:
        console.print(
            f"[red]❌ Unknown phase: '{phase_name}'. "
            f"Valid phases: {', '.join(_PHASE_STATES.keys())}[/red]"
        )
        raise typer.Exit(code=1)

    status_path = project_root / ".agent" / "STATUS.md"
    if not status_path.exists():
        console.print("[red]❌ No .agent/STATUS.md found. Run `gemstack init` first.[/red]")
        raise typer.Exit(code=1)

    content = status_path.read_text()

    # Validate preconditions
    current_state_match = re.search(r"\[STATE:\s*(\w+)\]", content)
    current_state = current_state_match.group(1) if current_state_match else "UNKNOWN"

    if current_state == "INITIALIZED" and phase_key != "spec":
        console.print("[yellow]⚠️  Project is INITIALIZED. Start with 'spec' phase first.[/yellow]")

    # Check for plan doc requirement before build
    if phase_key == "build":
        plans_dir = project_root / "docs" / "plans"
        if plans_dir.exists() and not any(plans_dir.iterdir()):
            console.print(
                "[yellow]⚠️  No plan documents found in docs/plans/. "
                "Consider running /step2-trap first.[/yellow]"
            )

    # Update state
    new_state = _PHASE_STATES[phase_key]
    content = re.sub(
        r"\[STATE:\s*\w+\]",
        f"[STATE: {new_state}]",
        content,
    )

    # Mark preceding phases as complete
    phase_order = ["spec", "trap", "build", "audit", "ship"]
    current_idx = phase_order.index(phase_key)

    for i, p in enumerate(phase_order):
        checkbox_name = _PHASE_CHECKBOXES[p]
        if i < current_idx:
            # Mark completed
            content = re.sub(
                rf"- \[ \] {checkbox_name}",
                f"- [x] {checkbox_name}",
                content,
            )

    from gemstack.utils.fileutil import write_atomic

    write_atomic(status_path, content)

    console.print(f"[green]✅ Transitioned to [bold]{phase_name}[/bold] phase[/green]")
    console.print(f"[dim]STATUS.md state updated to [STATE: {new_state}][/dim]")
