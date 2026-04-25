"""gemstack start — Feature kickoff CLI command."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def start(
    feature: str = typer.Argument(..., help="Feature name to start"),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
    branch: bool = typer.Option(False, "--branch", "-b", help="Create a feature branch"),
) -> None:
    """Initialize a new feature lifecycle in STATUS.md."""
    project_root = project_root.resolve()
    status_path = project_root / ".agent" / "STATUS.md"

    if not status_path.exists():
        console.print("[red]❌ No .agent/STATUS.md found. Run `gemstack init` first.[/red]")
        raise typer.Exit(code=1)

    # Read current status
    content = status_path.read_text()

    # Update state to IN_PROGRESS
    content = re.sub(
        r"\[STATE:\s*\w+\]",
        "[STATE: IN_PROGRESS]",
        content,
    )

    # Update current focus
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    content = re.sub(
        r"(## Current Focus\s*\n).*?(?=\n##)",
        rf"\g<1>\n{feature} (started {timestamp})\n",
        content,
        flags=re.DOTALL,
    )

    # Reset lifecycle checkboxes
    content = re.sub(r"- \[x\] (Spec|Trap|Build|Audit|Ship)", r"- [ ] \1", content)

    # Write atomically (spec §9.5)
    from gemstack.utils.fileutil import write_atomic

    write_atomic(status_path, content)

    console.print(f"[green]✅ Started feature: [bold]{feature}[/bold][/green]")
    console.print("[dim]STATUS.md updated to [STATE: IN_PROGRESS][/dim]")

    # Optionally create a feature branch
    if branch:
        slug = re.sub(r"[^a-z0-9]+", "-", feature.lower()).strip("-")
        branch_name = f"feat/{slug}"
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=str(project_root),
                check=True,
                capture_output=True,
                text=True,
            )
            console.print(f"[green]✅ Created branch: [bold]{branch_name}[/bold][/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]⚠️  Failed to create branch: {e.stderr.strip()}[/yellow]")
        except FileNotFoundError:
            console.print("[yellow]⚠️  git not found — skipping branch creation. Install `git` and ensure it is in your PATH.[/yellow]")

    console.print("[dim]Next: Run `gemstack route` to determine your next step.[/dim]")
