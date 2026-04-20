"""gemstack export — Template and context export CLI command."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def export(
    target: str = typer.Argument(".", help="Target directory for template export"),
    format: str = typer.Option(
        "",
        "--format",
        "-f",
        help="Export format: cursor, claude, gemini",
    ),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Export templates or generate agent-specific context files."""
    project_root = project_root.resolve()

    if format:
        _export_agent_format(project_root, format)
    else:
        _export_templates(Path(target))


def _export_agent_format(project_root: Path, fmt: str) -> None:
    """Generate agent-specific context files from .agent/ data."""
    valid_formats = {"cursor", "claude", "gemini"}
    if fmt not in valid_formats:
        console.print(
            f"[red]❌ Unknown format: '{fmt}'. Valid formats: {', '.join(valid_formats)}[/red]"
        )
        raise typer.Exit(code=1)

    agent_dir = project_root / ".agent"
    if not agent_dir.exists():
        console.print("[red]❌ No .agent/ directory found. Run `gemstack init` first.[/red]")
        raise typer.Exit(code=1)

    if fmt == "cursor":
        from gemstack.adapters.cursor import CursorExportAdapter

        adapter = CursorExportAdapter()
        content = adapter.export(project_root)
        output_path = project_root / ".cursorrules"
    elif fmt == "claude":
        from gemstack.adapters.claude import ClaudeExportAdapter

        adapter = ClaudeExportAdapter()  # type: ignore[assignment]
        content = adapter.export(project_root)
        output_path = project_root / "CLAUDE.md"
    elif fmt == "gemini":
        from gemstack.adapters.gemini import GeminiExportAdapter

        adapter = GeminiExportAdapter()  # type: ignore[assignment]
        content = adapter.export(project_root)
        output_path = project_root / "GEMINI.md"
    else:
        raise typer.Exit(code=1)

    output_path.write_text(content)
    console.print(f"[green]✅ Exported to {output_path.name}[/green]")
    console.print(f"[dim]Generated from .agent/ context ({len(content):,} chars)[/dim]")


def _export_templates(target_dir: Path) -> None:
    """Copy bundled templates to a local directory for customization."""
    from importlib.resources import files

    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    template_pkg = files("gemstack.templates")
    count = 0

    for item in [
        "architecture.md.j2",
        "style.md.j2",
        "testing.md.j2",
        "philosophy.md.j2",
        "status.md.j2",
    ]:
        try:
            resource = template_pkg / item
            if hasattr(resource, "read_text"):
                content = resource.read_text()
                (target_dir / item).write_text(content)
                count += 1
        except (FileNotFoundError, TypeError):
            continue

    console.print(f"[green]✅ Exported {count} templates to {target_dir}[/green]")
    console.print(
        "[dim]Customize these templates, then set the path with:\n"
        "  gemstack config set custom-templates-dir <path>[/dim]"
    )
