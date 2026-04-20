"""gemstack run — Autonomous step execution.

The flagship Phase 5 command. Compiles context, calls Gemini,
and writes structured output to project files.

Requires the ``gemstack[ai]`` optional dependency.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def run(
    step: str = typer.Argument(
        ..., help="Workflow step (step1-spec, step2-trap, etc.)"
    ),
    feature: str = typer.Argument(
        ..., help="Feature description (e.g., 'Add user notifications')"
    ),
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Compile context only, no API call"
    ),
    model: str = typer.Option(
        "gemini-2.5-flash", "--model", "-m", help="Gemini model to use"
    ),
    max_cost: float = typer.Option(
        None,
        "--max-cost",
        help="Max USD cost per feature (circuit breaker)",
    ),
    max_tokens: int = typer.Option(
        None,
        "--max-tokens",
        help="Max tokens per step (circuit breaker)",
    ),
) -> None:
    """Execute a workflow step autonomously via Gemini API."""
    project_root = project_root.resolve()
    agent_dir = project_root / ".agent"

    if not agent_dir.exists():
        console.print(
            "[red]❌ No .agent/ directory found. "
            "Run `gemstack init` first.[/red]"
        )
        raise typer.Exit(code=1)

    from gemstack.core.executor import StepExecutor

    executor = StepExecutor(
        model=model,
        max_cost=max_cost,
        max_tokens=max_tokens,
    )

    console.print(
        Panel(
            f"[bold cyan]Step:[/bold cyan] {step}\n"
            f"[bold cyan]Feature:[/bold cyan] {feature}\n"
            f"[bold cyan]Model:[/bold cyan] {model}\n"
            f"[bold cyan]Mode:[/bold cyan] "
            f"{'🔍 Dry Run' if dry_run else '🚀 Live'}",
            title="gemstack run",
            border_style="cyan",
        )
    )

    result = asyncio.run(
        executor.execute(
            step=step,
            feature=feature,
            project_root=project_root,
            dry_run=dry_run,
        )
    )

    # Display result
    if result.success:
        console.print(f"\n{result.summary()}")
    else:
        console.print(f"\n[red]{result.summary()}[/red]")
        raise typer.Exit(code=1)
