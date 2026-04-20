"""gemstack tail — Live session monitor."""

from __future__ import annotations

import re
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live

console = Console()


def tail(
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
    minimal: bool = typer.Option(False, "--minimal", help="Compact one-line status"),
) -> None:
    """Live TUI dashboard showing agent orchestration activity."""
    project_root = project_root.resolve()

    if not (project_root / ".agent").exists():
        console.print("[red]❌ No .agent/ directory found. Run `gemstack init` first.[/red]")
        raise typer.Exit(code=1)

    if minimal:
        _run_minimal(project_root)
    else:
        _run_tui(project_root)


def _run_tui(project_root: Path) -> None:
    """Launch the full Textual TUI dashboard."""
    try:
        from gemstack.tui.tail_app import GemstackTailApp
    except ImportError:
        console.print(
            "[red]❌ Tail extra not installed. Install with: pip install gemstack[tail][/red]"
        )
        raise typer.Exit(code=1) from None

    app = GemstackTailApp(project_root)
    app.run()


def _run_minimal(project_root: Path) -> None:
    """Run a compact one-line status monitor using Rich Live."""
    status_path = project_root / ".agent" / "STATUS.md"
    if not status_path.exists():
        console.print("[red]❌ No .agent/STATUS.md found.[/red]")
        raise typer.Exit(code=1)

    console.print("[dim]Watching STATUS.md (Ctrl+C to stop)...[/dim]")

    last_mtime = 0.0
    try:
        with Live(console=console, refresh_per_second=2) as live:
            while True:
                try:
                    mtime = status_path.stat().st_mtime
                    if mtime != last_mtime:
                        last_mtime = mtime
                        content = status_path.read_text()
                        state = _parse_state(content)
                        feature = _parse_feature(content)
                        live.update(
                            f"[bold cyan]State:[/bold cyan] {state}  "
                            f"[bold green]Feature:[/bold green] {feature}"
                        )
                except OSError:
                    live.update("[red]STATUS.md not found[/red]")

                time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped watching.[/dim]")


def _parse_state(content: str) -> str:
    """Extract [STATE: ...] from STATUS.md."""
    match = re.search(r"\[STATE:\s*(\w+)\]", content)
    return match.group(1) if match else "UNKNOWN"


def _parse_feature(content: str) -> str:
    """Extract current feature from STATUS.md."""
    match = re.search(r"## Current Focus\s*\n\s*(.+)", content)
    return match.group(1).strip() if match else "(none)"
