"""gemstack migrate — Topology migration."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def migrate(
    topology: str = typer.Option(
        "", "--topology", "-t", help="Explicit topology (e.g., 'backend,frontend')"
    ),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Upgrade a project to include topology-specific sections."""
    from gemstack.project.migrator import TopologyMigrator

    project_root = project_root.resolve()
    agent_dir = project_root / ".agent"

    if not agent_dir.exists():
        console.print("[red]❌ No .agent/ directory found. Run `gemstack init` first.[/red]")
        raise typer.Exit(code=1)

    # Determine topologies
    if topology:
        topologies = [t.strip() for t in topology.split(",") if t.strip()]
    else:
        # Auto-detect from project
        from gemstack.project.detector import ProjectDetector

        detector = ProjectDetector()
        profile = detector.detect(project_root)
        topologies = [t.value for t in profile.topologies]

        if not topologies:
            console.print("[yellow]⚠️  No topologies detected. Use --topology to specify.[/yellow]")
            raise typer.Exit(code=1)

        console.print(f"[dim]Detected topologies: {', '.join(topologies)}[/dim]")

    migrator = TopologyMigrator()
    result = migrator.migrate(project_root, topologies)

    # Report results
    if result.files_modified:
        for filename in result.files_modified:
            console.print(f"  [green]✔[/green] Modified .agent/{filename}")
        for section in result.sections_added:
            console.print(f"  [cyan]↳[/cyan] {section}")
        console.print("[green]✅ Topology migration complete![/green]")
    else:
        console.print("[yellow]⚠️  No changes needed — topologies already present.[/yellow]")

    for warning in result.warnings:
        console.print(f"[yellow]⚠️  {warning}[/yellow]")
