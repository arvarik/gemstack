"""Main CLI entry point for Gemstack."""

import logging
import sys
from pathlib import Path
from typing import Annotated

import typer

from gemstack.cli.context import CliContext, console, err_console, handle_error
from gemstack.errors import GemstackError

app = typer.Typer(
    name="gemstack",
    help="Opinionated AI agent orchestration framework for software engineering.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _gemstack_excepthook(exc_type, exc_value, exc_traceback):  # type: ignore
    """Global exception handler for GemstackErrors."""
    if issubclass(exc_type, GemstackError):
        handle_error(exc_value)
    else:
        # Fall back to default exception formatting for pure bugs
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = _gemstack_excepthook


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from gemstack import __version__

        console.print(f"gemstack {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root directory", resolve_path=True),
    ] = Path("."),
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug logging")] = False,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """Gemstack — structure your AI agent workflows."""
    ctx.obj = CliContext(project_root=project, verbose=verbose, debug=debug)

    log_level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)

    from rich.logging import RichHandler

    logging.basicConfig(
        level=log_level,
        format="%(levelname)s %(name)s: %(message)s",
        handlers=[
            RichHandler(
                level=log_level,
                console=err_console,
                show_path=False,
                markup=True,
            )
        ],
    )


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
