"""gemstack worktree — Parallel execution manager."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

worktree_app = typer.Typer(name="worktree", help="Parallel git worktree management")


@worktree_app.command()
def create(
    backend: str = typer.Option("", "--backend", help="Backend branch name"),
    frontend: str = typer.Option("", "--frontend", help="Frontend branch name"),
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Create worktrees for parallel development."""
    from gemstack.core.worktree import WorktreeManager

    branches: dict[str, str] = {}
    if backend:
        branches["backend"] = backend
    if frontend:
        branches["frontend"] = frontend

    if not branches:
        console.print(
            "[red]❌ Specify at least one branch: "
            "--backend <branch> and/or --frontend <branch>[/red]"
        )
        raise typer.Exit(code=1)

    manager = WorktreeManager()
    result = manager.create(project_root.resolve(), branches)

    if result.success:
        for wt in result.worktrees:
            console.print(
                f"  [green]✔[/green] Created worktree: {wt.path} ({wt.branch})"
            )
        console.print("[green]✅ Worktrees created![/green]")
    else:
        console.print(f"[red]❌ {result.message}[/red]")
        raise typer.Exit(code=1)


@worktree_app.command("status")
def worktree_status(
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Show active worktree status."""
    from gemstack.core.worktree import WorktreeManager

    manager = WorktreeManager()
    result = manager.status(project_root.resolve())

    if not result.success:
        console.print(f"[red]❌ {result.message}[/red]")
        raise typer.Exit(code=1)

    table = Table(title="Active Worktrees", show_header=True)
    table.add_column("Path", style="cyan")
    table.add_column("Branch", style="green")
    table.add_column("Commit", style="dim")

    for wt in result.worktrees:
        table.add_row(wt.path, wt.branch, wt.commit)

    console.print(table)


@worktree_app.command()
def merge(
    branch: str = typer.Argument("", help="Branch to merge (empty = all)"),
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Merge worktrees back to main branch."""
    from gemstack.core.worktree import WorktreeManager

    manager = WorktreeManager()
    result = manager.merge(
        project_root.resolve(), branch=branch if branch else None
    )

    if result.success:
        console.print(f"[green]✅ {result.message}[/green]")
    else:
        console.print(f"[red]❌ {result.message}[/red]")
        raise typer.Exit(code=1)


@worktree_app.command()
def cleanup(
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Clean up completed worktrees."""
    from gemstack.core.worktree import WorktreeManager

    manager = WorktreeManager()
    result = manager.cleanup(project_root.resolve())

    if result.success:
        console.print(f"[green]✅ {result.message}[/green]")
    else:
        console.print(f"[red]❌ {result.message}[/red]")
        raise typer.Exit(code=1)
