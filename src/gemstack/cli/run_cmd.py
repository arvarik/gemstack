"""gemstack run — Autonomous step execution.

The flagship Phase 5 command. Compiles context, calls Gemini,
and writes structured output to project files.

Requires the ``gemstack[ai]`` optional dependency.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel

from gemstack.cli.context import console
from gemstack.errors import GemstackError, ProjectError


def run(
    step: Annotated[str, typer.Argument(help="Workflow step (step1-spec, step2-trap, etc.)")],
    feature: Annotated[
        str, typer.Argument(help="Feature description (e.g., 'Add user notifications')")
    ],
    project_root: Annotated[
        Path, typer.Option("--project", "-p", help="Project root directory", resolve_path=True)
    ] = Path("."),
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Compile context only, no API call")
    ] = False,
    model: Annotated[
        str, typer.Option("--model", "-m", help="Gemini model to use")
    ] = "gemini-3.1-pro-preview",
    max_cost: Annotated[
        float | None, typer.Option("--max-cost", help="Max USD cost per feature (circuit breaker)")
    ] = None,
    max_tokens: Annotated[
        int | None, typer.Option("--max-tokens", help="Max tokens per step (circuit breaker)")
    ] = None,
) -> None:
    """Execute a workflow step autonomously via Gemini API."""
    agent_dir = project_root / ".agent"

    if not agent_dir.exists():
        raise ProjectError("No .agent/ directory found.", suggestion="Run `gemstack init` first.")

    from gemstack.orchestration.executor import StepExecutor

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
        raise GemstackError(
            result.summary(),
            suggestion="Fix the underlying step execution errors before trying again.",
        )
