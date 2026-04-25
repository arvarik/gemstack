"""Main CLI entry point for Gemstack."""

import logging
import os
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer

from gemstack.cli.context import CliContext, console, err_console, handle_error
from gemstack.errors import GemstackError

app = typer.Typer(
    name="gemstack",
    help="Opinionated AI agent orchestration framework for software engineering.",
    no_args_is_help=False,
    invoke_without_command=True,
    rich_markup_mode="rich",
)


def _gemstack_excepthook(exc_type, exc_value, exc_traceback):  # type: ignore
    """Global exception handler for GemstackErrors.

    Known GemstackErrors are displayed as structured panels.
    Unexpected exceptions generate a crash dump file with full
    debugging context so issues can be diagnosed without local
    reproduction.
    """
    if issubclass(exc_type, GemstackError):
        handle_error(exc_value)
    else:
        # Generate crash dump before falling back to default output
        crash_path = _write_crash_dump(exc_type, exc_value, exc_traceback)
        if crash_path:
            err_console.print(
                f"\n[bold red]Unexpected error — crash report saved to:[/bold red]\n"
                f"  [dim]{crash_path}[/dim]\n"
                f"[dim]Please include this file when reporting a bug.[/dim]\n"
            )
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _write_crash_dump(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: object,
) -> Path | None:
    """Write a structured crash dump for post-mortem debugging.

    The dump includes the full traceback, Python/OS/gemstack versions,
    the .agent/ directory listing, and environment variable keys
    (values are redacted for security).
    """
    try:
        from platformdirs import user_config_dir

        from gemstack import __version__

        crashes_dir = Path(user_config_dir("gemstack")) / "crashes"
        crashes_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        crash_path = crashes_dir / f"gemstack-crash-{ts}.log"

        tb_text = "".join(
            traceback.format_exception(exc_value)
        )

        # Collect .agent/ file listing from cwd
        agent_dir = Path.cwd() / ".agent"
        if agent_dir.exists():
            agent_listing = "\n".join(
                f"  {f.name} ({f.stat().st_size} bytes)"
                for f in sorted(agent_dir.iterdir())
                if f.is_file()
            )
        else:
            agent_listing = "  (no .agent/ directory in cwd)"

        # Redacted environment keys
        env_keys = ", ".join(sorted(os.environ.keys()))

        report = (
            f"=== Gemstack Crash Report ==="
            f"\nTimestamp: {ts}"
            f"\nGemstack Version: {__version__}"
            f"\nPython: {sys.version}"
            f"\nPlatform: {platform.system()} {platform.machine()}"
            f"\nCWD: {Path.cwd()}"
            f"\n\n--- .agent/ Directory ---"
            f"\n{agent_listing}"
            f"\n\n--- Environment Keys (values redacted) ---"
            f"\n{env_keys}"
            f"\n\n--- Traceback ---"
            f"\n{tb_text}"
        )

        crash_path.write_text(report, encoding="utf-8")
        return crash_path
    except Exception:
        # Never let crash-dump logic itself crash the process
        return None


sys.excepthook = _gemstack_excepthook


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from gemstack import __version__

        console.print(f"gemstack {__version__}")
        raise typer.Exit()


def _print_banner() -> None:
    """Print the colorful Gemstack ASCII art banner."""
    from gemstack import __version__

    # Gradient colors: blue → green → dark_orange
    lines = [
        ("[bold blue]   ██████╗ ███████╗███╗   ███╗[/bold blue]"
         "[bold blue]███████╗████████╗ █████╗  ██████╗██╗  ██╗[/bold blue]"),
        ("[bold blue]  ██╔════╝ ██╔════╝████╗ ████║[/bold blue]"
         "[bold green]██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝[/bold green]"),
        ("[bold green]  ██║  ███╗█████╗  ██╔████╔██║[/bold green]"
         "[bold green]███████╗   ██║   ███████║ ██║     █████╔╝[/bold green]"),
        ("[bold green]  ██║   ██║██╔══╝  ██║╚██╔╝██║[/bold green]"
         "[bold dark_orange]╚════██║   ██║   ██╔══██║ ██║     ██╔═██╗[/bold dark_orange]"),
        ("[bold dark_orange]  ╚██████╔╝███████╗██║ ╚═╝ ██║[/bold dark_orange]"
         "[bold dark_orange]███████║   ██║   ██║  ██║╚██████╗██║  ██╗[/bold dark_orange]"),
        ("[bold dark_orange]   ╚═════╝ ╚══════╝╚═╝     ╚═╝[/bold dark_orange]"
         "[bold dark_orange]╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝[/bold dark_orange]"),
    ]

    console.print()
    for line in lines:
        console.print(line)

    console.print()
    console.print(
        f"  [dim]v{__version__}[/dim]  "
        "[bold]Opinionated AI agent orchestration framework[/bold]"
    )
    console.print(
        "  [dim]Built for Gemini CLI & Antigravity[/dim]"
    )
    console.print()
    console.print("  [cyan]Get started:[/cyan]")
    console.print("    gemstack config set gemini-api-key <KEY>  [dim]Configure API key[/dim]")
    console.print("    gemstack init --ai            [dim]Initialize a project with AI[/dim]")
    console.print("    gemstack teach                [dim]Interactive 9-lesson tutorial[/dim]")
    console.print("    gemstack --help               [dim]See all commands[/dim]")
    console.print()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root directory", resolve_path=True),
    ] = Path("."),
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug logging")] = False,
    json_logs: Annotated[
        bool,
        typer.Option(
            "--json-logs",
            help="Emit structured JSON logs to stderr (for CI/CD pipelines)",
        ),
    ] = False,
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
    # Show banner when no subcommand is given (bare `gemstack`)
    if ctx.invoked_subcommand is None:
        _print_banner()
        raise typer.Exit()

    ctx.obj = CliContext(project_root=project, verbose=verbose, debug=debug)

    log_level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)

    if json_logs:
        from gemstack.cli.json_log_formatter import JsonLogFormatter

        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonLogFormatter())
        logging.basicConfig(level=log_level, handlers=[handler])
    else:
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


# --- Rich help panel names for command grouping ---
_SETUP = "Setup & Config"
_WORKFLOW = "Workflow & Lifecycle"
_CONTEXT = "Context & Analysis"
_TOOLING = "Tooling & Integrations"
_MULTI = "Multi-Project"
_MLAI = "ML/AI"
_DX = "DX & Learning"


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

    # ── Setup & Config ──────────────────────────────────────
    app.command(rich_help_panel=_SETUP)(init)
    app.command(rich_help_panel=_SETUP)(install)
    app.command(rich_help_panel=_SETUP)(uninstall)
    app.command(rich_help_panel=_SETUP)(doctor)

    from gemstack.cli.config_cmd import config_app

    app.add_typer(config_app, name="config", rich_help_panel=_SETUP)

    # ── Workflow & Lifecycle ────────────────────────────────
    from gemstack.cli.phase_cmd import phase
    from gemstack.cli.route_cmd import route
    from gemstack.cli.start_cmd import start

    app.command(rich_help_panel=_WORKFLOW)(status)
    app.command(rich_help_panel=_WORKFLOW)(route)
    app.command(rich_help_panel=_WORKFLOW)(start)
    app.command(rich_help_panel=_WORKFLOW)(phase)

    from gemstack.cli.run_cmd import run

    app.command(rich_help_panel=_WORKFLOW)(run)

    # ── Context & Analysis ──────────────────────────────────
    from gemstack.cli.compare_cmd import compare
    from gemstack.cli.compile_cmd import compile
    from gemstack.cli.diagnose_cmd import diagnose
    from gemstack.cli.diff_cmd import diff
    from gemstack.cli.export_cmd import export
    from gemstack.cli.migrate_cmd import migrate
    from gemstack.cli.replay_cmd import replay
    from gemstack.cli.snapshot_cmd import snapshot

    app.command(rich_help_panel=_CONTEXT)(compile)
    app.command(rich_help_panel=_CONTEXT)(check)
    app.command(rich_help_panel=_CONTEXT)(diff)
    app.command(rich_help_panel=_CONTEXT)(diagnose)
    app.command(rich_help_panel=_CONTEXT)(migrate)
    app.command(rich_help_panel=_CONTEXT)(export)
    app.command(rich_help_panel=_CONTEXT)(snapshot)
    app.command(rich_help_panel=_CONTEXT)(compare)
    app.command(rich_help_panel=_CONTEXT)(replay)

    # ── Tooling & Integrations ──────────────────────────────
    from gemstack.cli.ci_cmd import ci_app
    from gemstack.cli.hook_cmd import hook_app
    from gemstack.cli.mcp_cmd import mcp_app
    from gemstack.cli.scaffold_cmd import scaffold_app
    from gemstack.cli.worktree_cmd import worktree_app

    app.add_typer(hook_app, name="hook", rich_help_panel=_TOOLING)
    app.add_typer(mcp_app, name="mcp", rich_help_panel=_TOOLING)
    app.add_typer(worktree_app, name="worktree", rich_help_panel=_TOOLING)
    app.add_typer(ci_app, name="ci", rich_help_panel=_TOOLING)
    app.add_typer(scaffold_app, name="scaffold", rich_help_panel=_TOOLING)

    # ── Multi-Project ───────────────────────────────────────
    from gemstack.cli.batch_cmd import batch_app
    from gemstack.cli.matrix_cmd import matrix
    from gemstack.cli.registry_cmd import registry_app

    app.command(rich_help_panel=_MULTI)(matrix)
    app.add_typer(registry_app, name="registry", rich_help_panel=_MULTI)
    app.add_typer(batch_app, name="batch", rich_help_panel=_MULTI)

    # ── ML/AI ───────────────────────────────────────────────
    from gemstack.cli.eval_cmd import eval_app
    from gemstack.cli.prompt_cmd import prompt_app

    app.add_typer(prompt_app, name="prompt", rich_help_panel=_MLAI)
    app.add_typer(eval_app, name="eval", rich_help_panel=_MLAI)

    # ── DX & Learning ──────────────────────────────────────
    from gemstack.cli.tail_cmd import tail
    from gemstack.cli.teach_cmd import teach

    app.command(rich_help_panel=_DX)(tail)
    app.command(rich_help_panel=_DX)(teach)


_register_commands()
