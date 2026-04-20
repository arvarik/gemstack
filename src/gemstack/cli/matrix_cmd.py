"""gemstack matrix — Cross-project dashboard.

Scans directories for Gemstack-enabled projects and shows a unified
status matrix of phases, features, and health.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def matrix(
    projects: str = typer.Option(
        "", "--projects", help="Comma-separated project paths"
    ),
    scan: Path = typer.Option(
        None, "--scan", help="Directory to auto-discover Gemstack projects"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output as JSON instead of table"
    ),
) -> None:
    """Show a unified status matrix across multiple Gemstack projects."""
    project_paths: list[Path] = []

    if scan:
        project_paths = _discover_projects(scan.resolve())
    elif projects:
        project_paths = [
            Path(p.strip()).resolve() for p in projects.split(",") if p.strip()
        ]
    else:
        console.print(
            "[yellow]⚠️  Specify --projects or --scan to find projects.[/yellow]"
        )
        raise typer.Exit(code=1)

    if not project_paths:
        console.print("[yellow]⚠️  No Gemstack projects found.[/yellow]")
        raise typer.Exit(code=1)

    rows = [_get_project_status(p) for p in project_paths]

    if json_output:
        import json

        console.print(json.dumps(rows, indent=2, default=str))
    else:
        _print_table(rows)


def _discover_projects(scan_dir: Path) -> list[Path]:
    """Find directories containing .agent/ (excludes .git, node_modules, etc.)."""
    _SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".tox", "venv"}
    projects: list[Path] = []

    def _walk(directory: Path, depth: int = 0) -> None:
        if depth > 4:  # Don't scan too deep
            return
        try:
            for entry in sorted(directory.iterdir()):
                if not entry.is_dir():
                    continue
                if entry.name in _SKIP_DIRS:
                    continue
                if entry.name == ".agent":
                    projects.append(entry.parent)
                else:
                    _walk(entry, depth + 1)
        except PermissionError:
            pass

    _walk(scan_dir)
    return sorted(projects)


def _get_project_status(project_root: Path) -> dict[str, Any]:
    """Extract status information from a project."""
    status: dict[str, Any] = {
        "name": project_root.name,
        "path": str(project_root),
        "state": "UNKNOWN",
        "feature": "(none)",
        "health": "✅",
    }

    status_path = project_root / ".agent" / "STATUS.md"
    if not status_path.exists():
        status["health"] = "❌"
        return status

    content = status_path.read_text()

    # Extract state
    state_match = re.search(r"\[STATE:\s*(\w+)\]", content)
    if state_match:
        status["state"] = state_match.group(1)

    # Extract current feature
    feature_match = re.search(r"## Current Focus\s*\n\s*(.+)", content)
    if feature_match:
        status["feature"] = feature_match.group(1).strip()

    # Check staleness
    import os
    import time

    try:
        mtime = os.path.getmtime(status_path)
        age_days = (time.time() - mtime) / 86400
        if age_days > 7:
            status["health"] = f"⚠️ ({int(age_days)}d stale)"
    except OSError:
        pass

    return status


def _print_table(rows: list[dict[str, Any]]) -> None:
    """Print a Rich table of project statuses."""
    table = Table(title="Gemstack Project Matrix", show_header=True)
    table.add_column("Project", style="cyan")
    table.add_column("State", style="green")
    table.add_column("Feature")
    table.add_column("Health")

    for row in rows:
        table.add_row(
            row["name"],
            row["state"],
            row["feature"],
            row["health"],
        )

    console.print(table)
