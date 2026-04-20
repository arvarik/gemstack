"""Main CLI entry point for Gemstack."""

import logging

import typer
from rich.console import Console

app = typer.Typer(
    name="gemstack",
    help="Opinionated AI agent orchestration framework for software engineering.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()
err_console = Console(stderr=True)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from gemstack import __version__

        console.print(f"gemstack {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
    version: bool | None = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Gemstack — structure your AI agent workflows."""
    log_level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s %(name)s: %(message)s",
        handlers=[_create_rich_handler(log_level)],
    )


def _create_rich_handler(level: int) -> logging.Handler:
    """Create a Rich-powered log handler."""
    from rich.logging import RichHandler

    return RichHandler(
        level=level,
        console=err_console,
        show_path=False,
        markup=True,
    )


def handle_error(error: Exception) -> None:
    """Display a structured error with suggestion.

    CLI commands should catch GemstackError and call this function
    instead of doing ad-hoc console.print("[red]...") formatting.
    This ensures consistent error presentation per spec §5.3.
    """
    from rich.panel import Panel

    from gemstack.errors import GemstackError

    if isinstance(error, GemstackError):
        content = f"[bold red]{error}[/bold red]"
        if error.suggestion:
            content += f"\n\n[dim]{error.suggestion}[/dim]"
        err_console.print(Panel(content, title="❌ Error", border_style="red"))
    else:
        err_console.print(f"[red]Error: {error}[/red]")
    raise typer.Exit(code=1)


# --- Register all subcommands ---


def _register_commands() -> None:
    """Register all CLI commands.

    Phase 1 commands are functional stubs.
    Future commands print a "coming soon" message.
    """
    from gemstack.cli.check_cmd import check
    from gemstack.cli.doctor_cmd import doctor
    from gemstack.cli.init_cmd import init
    from gemstack.cli.install_cmd import install, uninstall
    from gemstack.cli.status_cmd import status

    # Phase 1 commands
    app.command()(init)
    app.command()(install)
    app.command()(uninstall)
    app.command()(status)
    app.command()(check)
    app.command()(doctor)

    # Future commands (Phase 2+) — registered as stubs
    from gemstack.cli.compile_cmd import compile
    from gemstack.cli.config_cmd import config_app
    from gemstack.cli.diff_cmd import diff
    from gemstack.cli.export_cmd import export
    from gemstack.cli.hook_cmd import hook_app
    from gemstack.cli.mcp_cmd import mcp_app
    from gemstack.cli.migrate_cmd import migrate
    from gemstack.cli.phase_cmd import phase
    from gemstack.cli.route_cmd import route
    from gemstack.cli.start_cmd import start
    from gemstack.cli.tail_cmd import tail
    from gemstack.cli.worktree_cmd import worktree_app

    app.command()(compile)
    app.command()(route)
    app.command()(start)
    app.command()(phase)
    app.command()(migrate)
    app.command()(diff)
    app.command()(export)
    app.command()(tail)
    app.add_typer(config_app, name="config")
    app.add_typer(hook_app, name="hook")
    app.add_typer(mcp_app, name="mcp")
    app.add_typer(worktree_app, name="worktree")

    # Phase 4 commands — Ecosystem
    from gemstack.cli.ci_cmd import ci_app
    from gemstack.cli.compare_cmd import compare
    from gemstack.cli.eval_cmd import eval_app
    from gemstack.cli.matrix_cmd import matrix
    from gemstack.cli.prompt_cmd import prompt_app
    from gemstack.cli.replay_cmd import replay
    from gemstack.cli.scaffold_cmd import scaffold_app
    from gemstack.cli.snapshot_cmd import snapshot
    from gemstack.cli.teach_cmd import teach

    app.add_typer(ci_app, name="ci")
    app.add_typer(scaffold_app, name="scaffold")
    app.add_typer(prompt_app, name="prompt")
    app.add_typer(eval_app, name="eval")
    app.command()(snapshot)
    app.command()(matrix)
    app.command()(teach)
    app.command()(compare)
    app.command()(replay)

    # Phase 5 commands — Autonomy
    from gemstack.cli.run_cmd import run

    app.command()(run)


_register_commands()
