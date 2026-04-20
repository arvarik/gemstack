"""gemstack scaffold — Smart boilerplate generation.

Generates context-aware scaffolding that respects the project's
topology and style guide.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from gemstack.cli.context import console
from gemstack.project.scaffolder import Scaffolder

scaffold_app = typer.Typer(name="scaffold", help="Smart boilerplate generation")


@scaffold_app.command()
def route(
    path: Annotated[str, typer.Argument(help="Route path (e.g., /api/v1/notifications)")],
    project_root: Annotated[
        Path, typer.Option("--project", "-p", help="Project root directory", resolve_path=True)
    ] = Path("."),
) -> None:
    """Scaffold a backend route and its test file."""
    scaffolder = Scaffolder(project_root)
    scaffolder.scaffold_route(path)
    console.print("[green]✅ Route scaffolded![/green]")


@scaffold_app.command()
def component(
    name: Annotated[str, typer.Argument(help="Component name (e.g., NotificationBell)")],
    project_root: Annotated[
        Path, typer.Option("--project", "-p", help="Project root directory", resolve_path=True)
    ] = Path("."),
) -> None:
    """Scaffold a frontend component with all 5 states."""
    scaffolder = Scaffolder(project_root)
    scaffolder.scaffold_component(name)
    console.print("[green]✅ Component scaffolded with 5-state skeleton![/green]")


@scaffold_app.command("test")
def scaffold_test(
    name: Annotated[str, typer.Argument(help="Test suite name")],
    project_root: Annotated[
        Path, typer.Option("--project", "-p", help="Project root directory", resolve_path=True)
    ] = Path("."),
) -> None:
    """Scaffold a test file matching project conventions."""
    scaffolder = Scaffolder(project_root)
    scaffolder.scaffold_test(name)
    console.print("[green]✅ Test suite scaffolded![/green]")
