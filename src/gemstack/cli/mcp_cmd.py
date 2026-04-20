"""gemstack mcp — MCP server management."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()

mcp_app = typer.Typer(name="mcp", help="Model Context Protocol server management")


@mcp_app.command()
def serve(
    project_root: Path = typer.Argument(".", help="Project root directory"),
    transport: str = typer.Option("stdio", help="Transport mode: 'stdio' or 'sse'"),
    port: int = typer.Option(8765, help="Port for SSE transport"),
) -> None:
    """Start the Gemstack MCP server."""
    try:
        from gemstack.mcp.server import create_server
    except ImportError:
        console.print(
            "[red]❌ MCP extra not installed. Install with: pip install gemstack[mcp][/red]"
        )
        raise typer.Exit(code=1) from None

    project_root = project_root.resolve()

    if not (project_root / ".agent").exists():
        console.print(
            "[yellow]⚠️  No .agent/ directory found at "
            f"{project_root}. The server will have limited context.[/yellow]"
        )

    if transport not in ("stdio", "sse"):
        console.print(f"[red]❌ Unknown transport: '{transport}'. Use 'stdio' or 'sse'.[/red]")
        raise typer.Exit(code=1)

    # FastMCP configures host/port via constructor, not via run()
    server_kwargs: dict[str, object] = {}
    if transport == "sse":
        server_kwargs["port"] = port
        server_kwargs["host"] = "127.0.0.1"

    server = create_server(project_root, **server_kwargs)
    server.run(transport=transport)


@mcp_app.command()
def register(
    gemini_cli: bool = typer.Option(False, "--gemini-cli", help="Register with Gemini CLI"),
    claude_desktop: bool = typer.Option(
        False, "--claude-desktop", help="Register with Claude Desktop"
    ),
    cursor: bool = typer.Option(False, "--cursor", help="Register with Cursor"),
    cline: bool = typer.Option(False, "--cline", help="Register with Cline"),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root (for Cursor)"),
) -> None:
    """Register the MCP server with an agent's configuration."""
    if not any([gemini_cli, claude_desktop, cursor, cline]):
        console.print(
            "[yellow]⚠️  Specify at least one target: "
            "--gemini-cli, --claude-desktop, --cursor, or --cline[/yellow]"
        )
        raise typer.Exit(code=1)

    from gemstack.mcp.registrar import register_mcp_server

    messages = register_mcp_server(
        gemini_cli=gemini_cli,
        claude_desktop=claude_desktop,
        cursor=cursor,
        cline=cline,
        project_root=project_root.resolve(),
    )

    for msg in messages:
        console.print(msg)
