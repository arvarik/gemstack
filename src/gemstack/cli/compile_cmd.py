"""gemstack compile — Context compiler CLI command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def compile(
    step: str = typer.Argument(
        ...,
        help="Workflow step to compile (e.g., 'step1-spec', 'step3-build')",
    ),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
    clipboard: bool = typer.Option(
        False, "--clipboard", "-c", help="Copy compiled output to clipboard"
    ),
    output: str = typer.Option("", "--output", "-o", help="Write compiled output to file"),
    max_tokens: int = typer.Option(0, "--max-tokens", help="Maximum token budget (0 = unlimited)"),
    no_source: bool = typer.Option(
        False, "--no-source", help="Exclude source files from compilation"
    ),
) -> None:
    """Compile the full context prompt for a workflow step."""
    from gemstack.errors import GemstackError
    from gemstack.orchestration.compiler import ContextCompiler

    project_root = project_root.resolve()

    try:
        compiler = ContextCompiler()
        result = compiler.compile(
            step=step,
            project_root=project_root,
            include_source=not no_source,
            max_tokens=max_tokens if max_tokens > 0 else None,
        )
    except FileNotFoundError as e:
        from gemstack.cli.context import handle_error

        handle_error(e)
    except GemstackError as e:
        from gemstack.cli.context import handle_error

        handle_error(e)

    # Output destination
    if output:
        output_path = Path(output)
        output_path.write_text(result.total_content)
        console.print(f"[green]✅ Compiled context written to {output_path}[/green]")
    elif clipboard:
        _copy_to_clipboard(result.total_content)
        console.print("[green]✅ Compiled context copied to clipboard[/green]")
    else:
        # Print to stdout (useful for piping)
        console.print(result.total_content)

    # Always show stats on stderr
    stats = (
        f"[dim]📊 {len(result.sections)} sections | "
        f"~{result.token_estimate:,} tokens | "
        f"{len(result.sources)} sources"
    )
    if result.truncated:
        stats += " | ⚠️  truncated"
    stats += "[/dim]"
    Console(stderr=True).print(stats)


def _copy_to_clipboard(text: str) -> None:
    """Copy text to system clipboard."""
    if sys.platform == "darwin":
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
    elif sys.platform == "linux":
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text.encode(),
                check=True,
            )
        except FileNotFoundError:
            subprocess.run(
                ["xsel", "--clipboard", "--input"],
                input=text.encode(),
                check=True,
            )
    elif sys.platform == "win32":
        subprocess.run(["clip"], input=text.encode(), check=True)
    else:
        console.print(
            "[yellow]⚠️  Clipboard not supported on this platform. "
            "Try installing `xclip` or use the `--out <file>` flag "
            "to save to a file instead.[/yellow]"
        )
