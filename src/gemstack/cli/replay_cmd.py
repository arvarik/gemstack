"""gemstack replay — Feature replay / post-mortem report.

Generates a timeline showing the full lifecycle progression
of a shipped feature by parsing archived artifacts and cost data.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()


def replay(
    feature: str = typer.Argument("", help="Feature name to replay (empty = --all)"),
    all_features: bool = typer.Option(False, "--all", help="Summary of all shipped features"),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Generate a retrospective report for a shipped feature."""
    project_root = project_root.resolve()
    archive_dir = project_root / "docs" / "archive"

    if not archive_dir.exists():
        console.print("[yellow]⚠️  No docs/archive/ directory found. Archive a feature first by completing the `gemstack phase ship` process.[/yellow]")
        raise typer.Exit(code=1)

    if all_features or not feature:
        _replay_all(archive_dir, project_root)
    else:
        _replay_feature(archive_dir, feature, project_root)


def _replay_all(archive_dir: Path, project_root: Path) -> None:
    """Show summary of all archived features."""
    features = sorted(d for d in archive_dir.iterdir() if d.is_dir())

    if not features:
        console.print("[yellow]⚠️  No archived features found. Complete and ship a feature using `gemstack phase ship` before replaying.[/yellow]")
        return

    table = Table(title="Feature Archive", show_header=True)
    table.add_column("Feature", style="cyan")
    table.add_column("Files")
    table.add_column("Cost", justify="right")
    table.add_column("Status")

    costs = _load_cost_data(project_root)

    for feature_dir in features:
        file_count = sum(1 for f in feature_dir.iterdir() if f.is_file())
        has_spec = (feature_dir / "spec.md").exists()
        has_plan = (feature_dir / "plan.md").exists()
        status = "✅ Complete" if (has_spec and has_plan) else "📝 Partial"
        feature_cost = costs.get(feature_dir.name, 0.0)
        cost_str = f"${feature_cost:.2f}" if feature_cost > 0 else "—"
        table.add_row(feature_dir.name, str(file_count), cost_str, status)

    console.print(table)


def _replay_feature(archive_dir: Path, feature: str, project_root: Path) -> None:
    """Show detailed timeline for a specific feature."""
    feature_dir = archive_dir / feature

    if not feature_dir.exists():
        console.print(f"[red]❌ Feature '{feature}' not found in archive.[/red]")
        available = ", ".join(d.name for d in archive_dir.iterdir() if d.is_dir())
        console.print(f"[dim]Available: {available}[/dim]")
        raise typer.Exit(code=1)

    # Build timeline tree
    tree = Tree(f"[bold cyan]Feature: {feature}[/bold cyan]")

    lifecycle_files = [
        ("spec.md", "📋 Spec", "step1-spec"),
        ("plan.md", "📐 Plan", "step2-trap"),
        ("tasks.md", "📝 Tasks", "step2-trap"),
        ("audit.md", "🔍 Audit", "step4-audit"),
        ("findings.md", "⚠️ Findings", "step4-audit"),
        ("ship.md", "🚀 Ship", "step5-ship"),
    ]

    for filename, label, _step in lifecycle_files:
        path = feature_dir / filename
        if path.exists():
            size = path.stat().st_size
            tree.add(f"{label}: [green]✔[/green] ({size:,} bytes)")
        else:
            tree.add(f"{label}: [dim]○ not found[/dim]")

    console.print(tree)

    # Cost summary
    costs_by_step = _load_cost_by_step(project_root, feature)
    if costs_by_step:
        console.print("\n[bold]Cost Summary[/bold]")
        cost_table = Table(show_header=True)
        cost_table.add_column("Step", style="cyan")
        cost_table.add_column("Tokens", justify="right")
        cost_table.add_column("Cost", justify="right")

        total_tokens = 0
        total_cost = 0.0
        for step_name, data in costs_by_step.items():
            tokens = int(data["tokens"])
            cost = float(data["cost"])
            total_tokens += tokens
            total_cost += cost
            cost_table.add_row(
                step_name,
                f"{tokens:,}",
                f"${cost:.4f}",
            )
        cost_table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{total_tokens:,}[/bold]",
            f"[bold]${total_cost:.4f}[/bold]",
        )
        console.print(cost_table)

    # Iteration metrics
    reroute_count = _count_reroutes(project_root, feature)
    if reroute_count > 0:
        console.print(f"\n[dim]Audit re-routes: {reroute_count}[/dim]")

    # Show all files in the feature directory
    all_files = sorted(f for f in feature_dir.iterdir() if f.is_file())
    lifecycle_names = {name for name, _, _ in lifecycle_files}
    extra = [f for f in all_files if f.name not in lifecycle_names]
    if extra:
        console.print(f"\n  [dim]Additional files: {', '.join(f.name for f in extra)}[/dim]")


# ── Helpers ────────────────────────────────────────────────────────


def _load_cost_data(project_root: Path) -> dict[str, float]:
    """Load total cost per feature from costs.json."""
    costs_file = project_root / ".agent" / "costs.json"
    if not costs_file.exists():
        return {}
    try:
        data = json.loads(costs_file.read_text())
        totals: dict[str, float] = {}
        for record in data.get("records", []):
            feat = record.get("feature", "unknown")
            totals[feat] = totals.get(feat, 0.0) + record.get("cost_usd", 0.0)
        return totals
    except (json.JSONDecodeError, OSError):
        return {}


def _load_cost_by_step(project_root: Path, feature: str) -> dict[str, dict[str, float | int]]:
    """Load cost breakdown by step for a specific feature."""
    costs_file = project_root / ".agent" / "costs.json"
    if not costs_file.exists():
        return {}
    try:
        data = json.loads(costs_file.read_text())
        by_step: dict[str, dict[str, float | int]] = {}
        for record in data.get("records", []):
            if record.get("feature") != feature:
                continue
            step = record.get("step", "unknown")
            if step not in by_step:
                by_step[step] = {"tokens": 0, "cost": 0.0}
            tokens = record.get("input_tokens", 0) + record.get("output_tokens", 0)
            by_step[step]["tokens"] = int(by_step[step]["tokens"]) + tokens
            by_step[step]["cost"] = float(by_step[step]["cost"]) + record.get("cost_usd", 0.0)
        return by_step
    except (json.JSONDecodeError, OSError):
        return {}


def _count_reroutes(project_root: Path, feature: str) -> int:
    """Count audit re-route events for a feature from cost data."""
    costs_file = project_root / ".agent" / "costs.json"
    if not costs_file.exists():
        return 0
    try:
        data = json.loads(costs_file.read_text())
        audit_count = sum(
            1
            for r in data.get("records", [])
            if r.get("feature") == feature and r.get("step") == "step4-audit"
        )
        # Each audit beyond the first is a re-route
        return max(0, audit_count - 1)
    except (json.JSONDecodeError, OSError):
        return 0
