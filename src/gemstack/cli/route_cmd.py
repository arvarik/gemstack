"""gemstack route — Routing decision engine CLI command."""

from __future__ import annotations

import json as json_mod
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

# Emoji mapping for routing actions
_ACTION_EMOJI = {
    "continue": "🟢",
    "reroute_to_build": "🟠",
    "reroute_to_spec": "🟠",
    "ready_to_ship": "🚀",
    "blocked": "🛑",
}


def route(
    project_root: Path = typer.Argument(".", help="Project root directory", exists=True),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable JSON output"),
) -> None:
    """Get the recommended next action based on project state."""
    from gemstack.orchestration.router import PhaseRouter

    project_root = project_root.resolve()
    router = PhaseRouter()
    decision = router.route(project_root)

    if json_output:
        console.print(
            json_mod.dumps(
                {
                    "action": decision.action.value,
                    "next_command": decision.next_command,
                    "reason": decision.reason,
                    "context_files": decision.context_files,
                    "blockers": decision.blockers,
                },
                indent=2,
            )
        )
        return

    emoji = _ACTION_EMOJI.get(decision.action.value, "❓")
    action_color = "red" if decision.action.value == "blocked" else "green"

    content = (
        f"[bold {action_color}]{emoji} {decision.action.value.upper()}[/bold {action_color}]\n\n"
        f"{decision.reason}\n"
    )

    if decision.next_command:
        content += f"\n[bold cyan]Next:[/bold cyan] `{decision.next_command}`"

    if decision.blockers:
        content += "\n\n[bold red]Blockers:[/bold red]"
        for blocker in decision.blockers:
            content += f"\n  • {blocker}"

    console.print(
        Panel(
            content,
            title="🧭 Gemstack Router",
            border_style="cyan",
        )
    )

    # Exit code 1 if blocked
    if decision.action.value == "blocked":
        raise typer.Exit(code=1)
