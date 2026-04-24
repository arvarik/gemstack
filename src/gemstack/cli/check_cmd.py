"""gemstack check — Project health validator."""

from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from gemstack.cli.context import console
from gemstack.errors import ValidationError
from gemstack.project.validator import ProjectValidator


def check(
    project_root: Annotated[
        Path, typer.Argument(help="Project root directory", resolve_path=True)
    ] = Path("."),
    fix: Annotated[bool, typer.Option("--fix", help="Auto-fix trivial issues")] = False,
    strict: Annotated[
        bool, typer.Option("--strict", help="Treat warnings as errors")
    ] = False,
) -> None:
    """Validate the project's .agent/ directory integrity."""
    validator = ProjectValidator()
    result = validator.validate(project_root, auto_fix=fix)

    # Display results
    if result.passed and not result.warnings:
        console.print(
            Panel(
                "[bold green]All checks passed![/bold green]",
                title="✅ Project Health",
                border_style="green",
            )
        )
    else:
        table = Table(title="Check Results", show_lines=True)
        table.add_column("Severity", style="bold", width=10)
        table.add_column("Issue")

        for err in result.errors:
            table.add_row("[red]ERROR[/red]", err)
        for warn in result.warnings:
            table.add_row("[yellow]WARN[/yellow]", warn)

        console.print(table)

        if result.fixes_applied:
            console.print(f"\n[green]Applied {result.fixes_applied} auto-fixes.[/green]")

    if result.errors:
        raise ValidationError(
            f"{len(result.errors)} validation checking errors found.",
            suggestion=(
                "Fix the errors listed above or optionally "
                "run `gemstack check --fix` for trivial issues."
            ),
        )

    # --strict: treat warnings as errors
    if strict and result.warnings:
        raise ValidationError(
            f"{len(result.warnings)} warnings treated as errors (--strict mode).",
            suggestion="Fix the warnings listed above or remove the --strict flag.",
        )
