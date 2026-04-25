"""gemstack install / uninstall — Global slash command distribution."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def install(
    antigravity_only: bool = typer.Option(
        False, "--antigravity-only", help="Install Antigravity symlinks only"
    ),
    gemini_cli_only: bool = typer.Option(
        False, "--gemini-cli-only", help="Install Gemini CLI TOML wrappers only"
    ),
    copy_mode: bool = typer.Option(
        False, "--copy-mode", help="Copy files instead of symlink (Windows compatibility)"
    ),
) -> None:
    """Install Gemstack commands for Antigravity and Gemini CLI."""
    console.print(
        Panel(
            "[bold cyan]Installing Gemstack commands[/bold cyan]",
            title="📦 gemstack install",
            border_style="cyan",
        )
    )

    # Determine which adapters to use
    install_antigravity = not gemini_cli_only
    install_gemini = not antigravity_only

    if install_antigravity:
        _install_antigravity(copy_mode)

    if install_gemini:
        _install_gemini_cli()

    console.print("\n[green]✅ Installation complete![/green]")
    console.print("[dim]Run `gemstack doctor` to verify the installation.[/dim]")


def uninstall() -> None:
    """Remove all Gemstack symlinks and TOML wrappers."""
    console.print(
        Panel(
            "[bold yellow]Removing Gemstack commands[/bold yellow]",
            title="🗑️  gemstack uninstall",
            border_style="yellow",
        )
    )

    _uninstall_antigravity()
    _uninstall_gemini_cli()

    console.print("\n[green]✅ Uninstallation complete.[/green]")


def _install_antigravity(copy_mode: bool) -> None:
    """Install symlinks into Antigravity global_workflows."""
    target_dir = Path.home() / ".gemini" / "antigravity" / "global_workflows"
    console.print(f"\n[bold]Antigravity[/bold] → {target_dir}")

    if not target_dir.parent.exists():
        console.print(
            "  [yellow]⚠️  Antigravity directory not found. "
            "Skipping. Install Antigravity first.[/yellow]"
        )
        return

    target_dir.mkdir(parents=True, exist_ok=True)

    # Get bundled data path
    try:
        from importlib.resources import files

        data = files("gemstack.data")
        installed = 0

        for subdir in ["roles", "phases", "workflows", "topologies"]:
            source_dir = data / subdir
            # Use joinpath to traverse
            for md_file in sorted(Path(str(source_dir)).glob("*.md")):
                target = target_dir / md_file.name
                if target.exists() or target.is_symlink():
                    target.unlink()
                if copy_mode:
                    import shutil

                    shutil.copy2(md_file, target)
                else:
                    target.symlink_to(md_file.resolve())
                installed += 1

        console.print(f"  [green]✔[/green] Installed {installed} commands")
    except Exception as e:
        console.print(f"  [red]✘ Error: {e}[/red]")


def _install_gemini_cli() -> None:
    """Generate TOML wrappers for Gemini CLI commands."""
    commands_dir = Path.home() / ".gemini" / "commands"
    console.print(f"\n[bold]Gemini CLI[/bold] → {commands_dir}")

    if not commands_dir.parent.exists():
        console.print(
            "  [yellow]⚠️  Gemini CLI directory not found. Skipping. Install it globally with `npm install -g @google/generative-ai-cli` first.[/yellow]"
        )
        return

    commands_dir.mkdir(parents=True, exist_ok=True)
    console.print("  [dim]TOML wrapper generation coming in v0.2.0[/dim]")


def _uninstall_antigravity() -> None:
    """Remove Antigravity symlinks."""
    target_dir = Path.home() / ".gemini" / "antigravity" / "global_workflows"
    if not target_dir.exists():
        console.print("  [dim]No Antigravity symlinks found.[/dim]")
        return

    removed = 0
    for link in target_dir.iterdir():
        if link.is_symlink():
            # Only remove symlinks that point to gemstack data
            target = link.resolve()
            if "gemstack" in str(target).lower():
                link.unlink()
                removed += 1

    console.print(f"  [green]✔[/green] Removed {removed} Antigravity symlinks")


def _uninstall_gemini_cli() -> None:
    """Remove Gemini CLI TOML wrappers."""
    console.print("  [dim]Gemini CLI TOML cleanup coming in v0.2.0[/dim]")
