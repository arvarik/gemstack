"""gemstack diff — Context drift detection."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def diff(
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
    architecture: bool = typer.Option(False, "--architecture", help="Only ARCHITECTURE.md drift"),
    env: bool = typer.Option(False, "--env", help="Only .env drift"),
) -> None:
    """Detect drift between .agent/ docs and the actual codebase."""
    from gemstack.utils.differ import ContextDiffer

    project_root = project_root.resolve()
    agent_dir = project_root / ".agent"

    if not agent_dir.exists():
        console.print("[red]❌ No .agent/ directory found. Run `gemstack init` first.[/red]")
        raise typer.Exit(code=1)

    differ = ContextDiffer()
    report = differ.analyze(
        project_root,
        architecture_only=architecture,
        env_only=env,
    )

    if report.has_drift:
        console.print(
            Panel(
                report.to_markdown(),
                title="🔍 Context Drift Detected",
                border_style="yellow",
            )
        )
        console.print("[dim]Update your .agent/ files to resolve this drift.[/dim]")
        raise typer.Exit(code=1)
    else:
        console.print("[green]✅ No drift detected. .agent/ is in sync.[/green]")
