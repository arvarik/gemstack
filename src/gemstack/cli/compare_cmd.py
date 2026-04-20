"""gemstack compare — Context compilation benchmarking.

Benchmarks the Gemstack context compilation pipeline across different
model configurations. Measures compilation time, context size, and
section count — but does NOT make actual API calls to models.

For full agent evaluation, use ``gemstack eval``.
Requires the ``gemstack[ai]`` optional dependency (for import verification).
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from gemstack.orchestration.compiler import ContextCompiler

console = Console()


def compare(
    spec: Path = typer.Option(..., "--spec", help="Path to the feature spec markdown"),
    models: str = typer.Option(
        "gemini-2.5-pro,gemini-2.5-flash",
        "--models",
        help="Comma-separated model names to compare",
    ),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Compare AI agent performance across different model configurations."""
    project_root = project_root.resolve()
    spec = spec.resolve()

    if not spec.exists():
        console.print(f"[red]❌ Spec file not found: {spec}[/red]")
        raise typer.Exit(code=1)

    try:
        from google import genai  # noqa: F401
    except ImportError:
        console.print(
            "[red]❌ AI extra not installed. Install with: pip install gemstack[ai][/red]"
        )
        raise typer.Exit(code=1) from None

    model_list = [m.strip() for m in models.split(",") if m.strip()]
    spec_content = spec.read_text()

    console.print(f"[dim]Comparing {len(model_list)} models against: {spec.name}[/dim]")

    # Compile base context
    from gemstack.orchestration.compiler import ContextCompiler

    compiler = ContextCompiler()

    results: list[dict[str, Any]] = []
    for model_name in model_list:
        console.print(f"  [cyan]▶[/cyan] Testing {model_name}...")
        result = _benchmark_model(model_name, spec_content, compiler, project_root)
        results.append(result)

    _print_comparison(results)


def _benchmark_model(
    model_name: str,
    spec_content: str,
    compiler: ContextCompiler,
    project_root: Path,
) -> dict[str, Any]:
    """Benchmark a single model against the spec.

    Uses the compiler to generate context, measures compilation time
    and context size. Does NOT make actual API calls in the benchmark —
    that would be the full eval pipeline.
    """
    start = time.perf_counter()

    try:
        result = compiler.compile(
            step="step3-build",
            project_root=project_root,
            include_source=True,
        )
        compile_time = time.perf_counter() - start
        return {
            "model": model_name,
            "context_tokens": result.token_estimate,
            "sections": len(result.sections),
            "compile_time_ms": int(compile_time * 1000),
            "truncated": result.truncated,
            "status": "✅",
        }
    except Exception as e:
        return {
            "model": model_name,
            "context_tokens": 0,
            "sections": 0,
            "compile_time_ms": 0,
            "truncated": False,
            "status": f"❌ {e}",
        }


def _print_comparison(results: list[dict[str, Any]]) -> None:
    """Print a comparison table of results."""
    table = Table(title="Agent Comparison Results", show_header=True)
    table.add_column("Model", style="cyan")
    table.add_column("Context Tokens", justify="right")
    table.add_column("Sections", justify="right")
    table.add_column("Compile (ms)", justify="right")
    table.add_column("Status")

    for r in results:
        table.add_row(
            r["model"],
            f"{r['context_tokens']:,}",
            str(r["sections"]),
            str(r["compile_time_ms"]),
            r["status"],
        )

    console.print(table)
