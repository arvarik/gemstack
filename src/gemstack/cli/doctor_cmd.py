"""gemstack doctor — Environment diagnostics."""

import platform
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def doctor() -> None:
    """Validate the Gemstack installation and environment."""
    console.print(
        Panel(
            "[bold cyan]Running environment diagnostics...[/bold cyan]",
            title="🩺 gemstack doctor",
            border_style="cyan",
        )
    )

    results: list[tuple[str, bool, str]] = []

    # Check 1: Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 10)
    results.append((
        "Python version",
        py_ok,
        f"{py_version}" + ("" if py_ok else " (requires ≥3.10)"),
    ))

    # Check 2: Gemstack version
    from gemstack import __version__

    results.append(("Gemstack version", True, __version__))

    # Check 3: Platform
    results.append(("Platform", True, f"{platform.system()} {platform.machine()}"))

    # Check 4: Antigravity directory
    antigravity_dir = Path.home() / ".gemini" / "antigravity"
    ag_exists = antigravity_dir.exists()
    results.append((
        "Antigravity directory",
        ag_exists,
        str(antigravity_dir) if ag_exists else "Not found",
    ))

    # Check 5: Global workflows directory
    workflows_dir = antigravity_dir / "global_workflows"
    wf_exists = workflows_dir.exists()
    if wf_exists:
        symlink_count = sum(1 for f in workflows_dir.iterdir() if f.suffix == ".md")
        results.append(("Global workflows", True, f"{symlink_count} files found"))
    else:
        results.append(("Global workflows", False, "Directory not found"))

    # Check 6: Gemini CLI
    gemini_dir = Path.home() / ".gemini"
    gemini_exists = gemini_dir.exists()
    results.append((
        "Gemini CLI config",
        gemini_exists,
        str(gemini_dir) if gemini_exists else "Not found",
    ))

    # Check 7: Bundled data integrity
    try:
        from importlib.resources import files

        files("gemstack.data")  # Verify bundled data is accessible
        data_ok = True
        data_msg = "Bundled data accessible"
    except Exception as e:
        data_ok = False
        data_msg = f"Error: {e}"
    results.append(("Bundled data", data_ok, data_msg))

    # Display results
    table = Table(show_lines=False)
    table.add_column("Check", style="bold")
    table.add_column("Status", justify="center", width=4)
    table.add_column("Details")

    all_ok = True
    for name, ok, detail in results:
        icon = "[green]✔[/green]" if ok else "[red]✘[/red]"
        if not ok:
            all_ok = False
        table.add_row(name, icon, detail)

    console.print(table)

    if all_ok:
        console.print("\n[bold green]All checks passed! 🎉[/bold green]")
    else:
        console.print(
            "\n[yellow]Some checks failed. "
            "Run `gemstack install` to fix missing components.[/yellow]"
        )
