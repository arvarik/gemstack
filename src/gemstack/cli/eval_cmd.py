"""gemstack eval — Evaluation runner for ML/AI topology projects.

Manages eval sets, enforces holdout boundaries, and populates
the Evaluation Thresholds table in TESTING.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from gemstack.core.fileutil import write_atomic

console = Console()

eval_app = typer.Typer(name="eval", help="Evaluation runner (ML/AI)")


@eval_app.command()
def run(
    metric: str = typer.Option(
        "", "--metric", help="Run specific metric only (e.g., rouge-l)"
    ),
    prompts: bool = typer.Option(
        False, "--prompts", help="Evaluate prompt variations"
    ),
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Run evaluation sets against the current configuration."""
    project_root = project_root.resolve()
    eval_dir = project_root / "eval"

    if not eval_dir.exists():
        console.print("[red]❌ No eval/ directory found.[/red]")
        console.print("[dim]Create eval/ with eval set JSON files to get started.[/dim]")
        raise typer.Exit(code=1)

    # Enforce holdout boundary
    holdout_dir = eval_dir / "holdout"
    if holdout_dir.exists():
        console.print(
            "[yellow]⚠️  Holdout directory detected — "
            "eval/holdout/ will NOT be loaded.[/yellow]"
        )

    # Discover eval sets (exclude holdout)
    eval_sets = _discover_eval_sets(eval_dir, exclude_holdout=True)
    if not eval_sets:
        console.print("[yellow]⚠️  No eval sets found in eval/.[/yellow]")
        raise typer.Exit(code=1)

    console.print(f"[dim]Found {len(eval_sets)} eval sets[/dim]")

    results: list[dict[str, Any]] = []
    for eval_path in eval_sets:
        result = _run_eval_set(eval_path, metric_filter=metric)
        results.append(result)
        emoji = "✅" if result["passed"] else "❌"
        console.print(
            f"  {emoji} {result['name']}: "
            f"{result['score']:.2f} (target: {result['target']:.2f})"
        )

    # Update TESTING.md thresholds
    _update_testing_thresholds(project_root, results)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    overall = "✅" if passed == total else "❌"
    console.print(f"\n{overall} [bold]{passed}/{total} eval sets passed[/bold]")

    if passed < total:
        console.print(
            "[yellow]Circuit breaker: thresholds not met. "
            "Fix before proceeding to audit.[/yellow]"
        )
        raise typer.Exit(code=1)


@eval_app.command()
def status(
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Show current eval scores vs targets."""
    project_root = project_root.resolve()
    eval_dir = project_root / "eval"

    if not eval_dir.exists():
        console.print("[yellow]⚠️  No eval/ directory found.[/yellow]")
        raise typer.Exit(code=1)

    eval_sets = _discover_eval_sets(eval_dir, exclude_holdout=True)
    if not eval_sets:
        console.print("[yellow]⚠️  No eval sets found.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title="Evaluation Status", show_header=True)
    table.add_column("Eval Set", style="cyan")
    table.add_column("Metric")
    table.add_column("Target", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Status")

    for eval_path in eval_sets:
        result = _run_eval_set(eval_path)
        table.add_row(
            result["name"],
            result["metric"],
            f"{result['target']:.2f}",
            f"{result['score']:.2f}",
            "✅" if result["passed"] else "❌",
        )

    console.print(table)


# ── Helpers ────────────────────────────────────────────────────────


def _discover_eval_sets(eval_dir: Path, *, exclude_holdout: bool = True) -> list[Path]:
    """Find eval set JSON files, respecting holdout boundary."""
    eval_sets: list[Path] = []
    for path in sorted(eval_dir.rglob("*.json")):
        if exclude_holdout and "holdout" in path.parts:
            continue
        eval_sets.append(path)
    return eval_sets


def _run_eval_set(eval_path: Path, metric_filter: str = "") -> dict[str, Any]:
    """Run a single eval set and return results.

    Eval set JSON format:
    {
        "name": "extraction-accuracy",
        "metric": "accuracy",
        "target": 0.95,
        "cases": [
            {"input": "...", "expected": "...", "actual": "..."}
        ]
    }
    """
    try:
        data = json.loads(eval_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return {
            "name": eval_path.stem,
            "metric": "error",
            "target": 0.0,
            "score": 0.0,
            "passed": False,
            "error": str(e),
        }

    name = data.get("name", eval_path.stem)
    metric_name = data.get("metric", "accuracy")
    target = data.get("target", 0.9)
    cases = data.get("cases", [])

    if metric_filter and metric_name != metric_filter:
        return {
            "name": name,
            "metric": metric_name,
            "target": target,
            "score": 0.0,
            "passed": True,  # skip
            "skipped": True,
        }

    # Simple accuracy: proportion of cases where actual == expected
    if not cases:
        score = 0.0
    else:
        correct = sum(
            1 for c in cases
            if c.get("actual", "").strip() == c.get("expected", "").strip()
        )
        score = correct / len(cases)

    return {
        "name": name,
        "metric": metric_name,
        "target": target,
        "score": score,
        "passed": score >= target,
    }


def _update_testing_thresholds(project_root: Path, results: list[dict[str, Any]]) -> None:
    """Update the Evaluation Thresholds table in TESTING.md."""
    testing_path = project_root / ".agent" / "TESTING.md"
    if not testing_path.exists():
        return

    content = testing_path.read_text()
    marker = "## Evaluation Thresholds"
    if marker not in content:
        return

    # Build new table
    rows = [
        "| Eval Set | Metric | Target | Current | Status |",
        "|----------|--------|--------|---------|--------|",
    ]
    for r in results:
        if r.get("skipped"):
            continue
        status_emoji = "✅" if r["passed"] else "❌"
        rows.append(
            f"| {r['name']} | {r['metric']} | {r['target']:.2f} "
            f"| {r['score']:.2f} | {status_emoji} |"
        )

    new_table = "\n".join(rows)

    # Replace existing table under the marker
    pattern = rf"({re.escape(marker)})\s*\n\|.*?(?=\n##|\n---|\Z)"
    replacement = f"{marker}\n\n{new_table}"
    updated = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if updated != content:
        write_atomic(testing_path, updated)
