"""gemstack check — Project health validator."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

REQUIRED_AGENT_FILES = [
    "ARCHITECTURE.md",
    "STYLE.md",
    "TESTING.md",
    "PHILOSOPHY.md",
    "STATUS.md",
]


def check(
    project_root: Path = typer.Argument(".", help="Project root directory"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix trivial issues"),
) -> None:
    """Validate the project's .agent/ directory integrity."""
    project_root = project_root.resolve()
    agent_dir = project_root / ".agent"

    errors: list[str] = []
    warnings: list[str] = []
    fixes_applied = 0

    # Check 1: .agent/ directory exists
    if not agent_dir.exists():
        console.print(
            Panel(
                "[bold red]No .agent/ directory found.[/bold red]\n\n"
                "[dim]Run `gemstack init` to initialize this project.[/dim]",
                title="❌ Check Failed",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)

    # Check 2: Required files exist
    for filename in REQUIRED_AGENT_FILES:
        if not (agent_dir / filename).exists():
            errors.append(f"Missing required file: .agent/{filename}")

    # Check 3: docs/ lifecycle directories
    for dirname in ["explorations", "designs", "plans", "archive"]:
        docs_dir = project_root / "docs" / dirname
        if not docs_dir.exists():
            if fix:
                docs_dir.mkdir(parents=True, exist_ok=True)
                (docs_dir / ".gitkeep").touch()
                fixes_applied += 1
            else:
                warnings.append(f"Missing directory: docs/{dirname}/ (fix with --fix)")

    # Check 4: STATUS.md has a state enum
    status_path = agent_dir / "STATUS.md"
    if status_path.exists():
        import re

        content = status_path.read_text()
        if not re.search(r"\[STATE:\s*\w+\]", content):
            warnings.append("STATUS.md missing [STATE: ...] declaration")

    # Check 5: ARCHITECTURE.md has topology
    arch_path = agent_dir / "ARCHITECTURE.md"
    if arch_path.exists():
        content = arch_path.read_text()
        if "Topology" not in content:
            warnings.append("ARCHITECTURE.md missing topology declaration")

    # Check 6: Plugin-registered custom checks
    from gemstack.plugins import fire_register_checks

    plugin_errors = fire_register_checks(project_root)
    errors.extend(plugin_errors)

    # Display results
    if not errors and not warnings:
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

        for err in errors:
            table.add_row("[red]ERROR[/red]", err)
        for warn in warnings:
            table.add_row("[yellow]WARN[/yellow]", warn)

        console.print(table)

        if fixes_applied:
            console.print(f"\n[green]Applied {fixes_applied} auto-fixes.[/green]")

    if errors:
        raise typer.Exit(code=1)
