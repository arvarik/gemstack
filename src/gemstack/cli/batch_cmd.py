"""gemstack batch — Run commands across all registered projects."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

batch_app = typer.Typer(name="batch", help="Run Gemstack commands across all registered projects")

# Commands that can be batched
_BATCHABLE_COMMANDS = {"check", "diff", "migrate", "status"}


def _get_registry() -> list[str]:
    """Load the project registry."""
    from gemstack.project.config import GemstackConfig

    config = GemstackConfig.load()
    return list(config.projects)


@batch_app.callback(invoke_without_command=True)
def batch_main(
    ctx: typer.Context,
    command: str = typer.Argument(
        None, help="Gemstack command to run (check, diff, migrate, status)"
    ),
) -> None:
    """Run a Gemstack command across all registered projects.

    Example: gemstack batch check
    """
    if ctx.invoked_subcommand is not None:
        return

    if command is None:
        console.print("[yellow]Usage: gemstack batch <command>[/yellow]")
        console.print(f"[dim]Available commands: {', '.join(sorted(_BATCHABLE_COMMANDS))}[/dim]")
        return

    if command not in _BATCHABLE_COMMANDS:
        console.print(f"[red]❌ Cannot batch command: {command}[/red]")
        console.print(f"[dim]Batchable commands: {', '.join(sorted(_BATCHABLE_COMMANDS))}[/dim]")
        raise typer.Exit(code=1)

    projects = _get_registry()
    if not projects:
        console.print(
            "[yellow]⚠️  No projects registered. "
            "Use `gemstack registry add <path>` or `gemstack registry scan <dir>` first.[/yellow]"
        )
        raise typer.Exit(code=1)

    results: list[tuple[str, bool, float]] = []
    failed = 0

    console.print(
        f"\n[bold]Running `gemstack {command}` across {len(projects)} project(s)...[/bold]\n"
    )

    for project_path in projects:
        p = Path(project_path)
        name = p.name

        if not p.exists():
            console.print(f"  [red]✘[/red] {name} — path does not exist")
            results.append((name, False, 0.0))
            failed += 1
            continue

        start = time.monotonic()
        try:
            result = subprocess.run(
                ["gemstack", command, str(p)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            elapsed = time.monotonic() - start
            passed = result.returncode == 0

            icon = "[green]✔[/green]" if passed else "[red]✘[/red]"
            console.print(f"  {icon} {name} ({elapsed:.1f}s)")

            if not passed:
                failed += 1

            results.append((name, passed, elapsed))
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - start
            console.print(f"  [red]⏱[/red] {name} — timed out ({elapsed:.1f}s)")
            results.append((name, False, elapsed))
            failed += 1
        except FileNotFoundError:
            console.print(f"  [red]✘[/red] {name} — gemstack not found in PATH")
            results.append((name, False, 0.0))
            failed += 1

    # Summary table
    console.print()
    table = Table(title=f"Batch Results: gemstack {command}", show_header=True)
    table.add_column("Project")
    table.add_column("Result", width=8)
    table.add_column("Duration", width=10, justify="right")

    for name, passed, elapsed in results:
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        table.add_row(name, status, f"{elapsed:.1f}s")

    console.print(table)

    if failed > 0:
        console.print(f"\n[red]❌ {failed}/{len(projects)} project(s) failed[/red]")
        raise typer.Exit(code=1)
    else:
        console.print(f"\n[green]✅ All {len(projects)} project(s) passed[/green]")
