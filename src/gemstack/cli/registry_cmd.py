"""gemstack registry — Project registry management for multi-repo workflows."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

registry_app = typer.Typer(name="registry", help="Manage project registry for batch operations")


def _load_registry() -> list[str]:
    """Load the registry from global config."""
    from gemstack.project.config import GemstackConfig

    config = GemstackConfig.load()
    return list(config.projects)


def _save_registry(projects: list[str]) -> None:
    """Persist the registry to global config."""
    from gemstack.project.config import GemstackConfig

    config = GemstackConfig.load()
    config.projects = projects
    config.save()


@registry_app.command("add")
def registry_add(
    path: str = typer.Argument(..., help="Path to a Gemstack project"),
) -> None:
    """Register a project path for batch operations."""
    resolved = Path(path).resolve()

    if not resolved.is_dir():
        console.print(f"[red]❌ Path does not exist: {resolved}[/red]")
        raise typer.Exit(code=1)

    projects = _load_registry()
    path_str = str(resolved)

    if path_str in projects:
        console.print(f"[yellow]⚠️  Already registered: {resolved}[/yellow]")
        return

    projects.append(path_str)
    _save_registry(projects)
    console.print(f"[green]✔ Registered: {resolved}[/green]")


@registry_app.command("list")
def registry_list() -> None:
    """List all registered projects."""
    projects = _load_registry()

    if not projects:
        console.print(
            "[dim]No projects registered. Use `gemstack registry add <path>` to add.[/dim]"
        )
        return

    table = Table(title="Registered Projects", show_header=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Path")
    table.add_column("Status", width=12)

    for i, project_path in enumerate(projects, 1):
        p = Path(project_path)
        has_agent = (p / ".agent").is_dir()
        status = "[green]✔ active[/green]" if has_agent else "[yellow]⚠ no .agent[/yellow]"
        if not p.exists():
            status = "[red]✘ missing[/red]"
        table.add_row(str(i), project_path, status)

    console.print(table)


@registry_app.command("remove")
def registry_remove(
    path: str = typer.Argument(..., help="Path to remove from registry"),
) -> None:
    """Unregister a project path."""
    resolved = str(Path(path).resolve())
    projects = _load_registry()

    if resolved not in projects:
        console.print(f"[yellow]⚠️  Not registered: {resolved}[/yellow]")
        return

    projects.remove(resolved)
    _save_registry(projects)
    console.print(f"[green]✔ Removed: {resolved}[/green]")


@registry_app.command("scan")
def registry_scan(
    parent: str = typer.Argument(..., help="Parent directory to scan for Gemstack projects"),
) -> None:
    """Auto-discover and register projects with .agent/ directories."""
    parent_path = Path(parent).resolve()

    if not parent_path.is_dir():
        console.print(f"[red]❌ Not a directory: {parent_path}[/red]")
        raise typer.Exit(code=1)

    projects = _load_registry()
    discovered = 0

    for child in sorted(parent_path.iterdir()):
        if child.is_dir() and (child / ".agent").is_dir():
            path_str = str(child)
            if path_str not in projects:
                projects.append(path_str)
                console.print(f"  [green]✔[/green] Discovered: {child.name}")
                discovered += 1

    if discovered > 0:
        _save_registry(projects)
        console.print(f"\n[green]✅ Registered {discovered} new project(s)[/green]")
    else:
        console.print("[dim]No new Gemstack projects found.[/dim]")
