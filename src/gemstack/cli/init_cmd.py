"""gemstack init — Project bootstrapping command.

Analyzes an existing project (or scaffolds a new one) and populates
the .agent/ directory with project-specific context.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.panel import Panel

if TYPE_CHECKING:
    from gemstack.core.detector import ProjectProfile

console = Console()
logger = logging.getLogger(__name__)


def init(
    project_root: Path = typer.Argument(
        ".", help="Project root directory to initialize", exists=True
    ),
    topology: str = typer.Option(
        "", "--topology", "-t", help="Explicit topology (e.g., 'backend,frontend')"
    ),
    no_ai: bool = typer.Option(
        False, "--no-ai", help="Template-only, no Gemini API calls"
    ),
    from_legacy: bool = typer.Option(
        False, "--from-legacy", help="Absorb existing context files only"
    ),
    ai: bool = typer.Option(
        False, "--ai", help="Force AI-powered deep analysis"
    ),
) -> None:
    """Initialize a Gemstack project with .agent/ directory."""
    project_root = project_root.resolve()

    console.print(
        Panel(
            f"[bold cyan]Initializing Gemstack project[/bold cyan]\n"
            f"[dim]Directory: {project_root}[/dim]",
            title="🏗️ gemstack init",
            border_style="cyan",
        )
    )

    agent_dir = project_root / ".agent"

    if agent_dir.exists():
        console.print("[yellow]⚠️  .agent/ directory already exists. Skipping.[/yellow]")
        raise typer.Exit(0)

    # Step 1: Detect project profile
    console.print("[dim]Analyzing project...[/dim]")
    from gemstack.core.detector import ProjectDetector, Topology

    detector = ProjectDetector()
    profile = detector.detect(project_root)

    # Override topologies if explicitly specified
    if topology:
        profile.topologies = [
            Topology(t.strip()) for t in topology.split(",") if t.strip()
        ]

    _print_detection_results(profile)

    # Step 2: Absorb legacy context files if requested
    if from_legacy and profile.legacy_files:
        console.print(f"[dim]Absorbing {len(profile.legacy_files)} legacy context files...[/dim]")
        # Legacy files will be available as context for AI analysis

    # Step 3: Generate .agent/ files
    use_ai = ai or (not no_ai and _has_api_key())

    if use_ai:
        console.print("[dim]Running AI-powered deep analysis...[/dim]")
        try:
            asyncio.run(_init_with_ai(project_root, profile))
        except ImportError:
            console.print(
                "[yellow]⚠️  AI extra not installed. "
                "Install with: pip install gemstack[ai][/yellow]"
            )
            console.print("[dim]Falling back to template-only mode...[/dim]")
            _init_template_only(project_root, profile)
        except Exception as e:
            console.print(
                f"[yellow]⚠️  AI analysis failed: {e}[/yellow]"
            )
            console.print("[dim]Falling back to template-only mode...[/dim]")
            _init_template_only(project_root, profile)
    else:
        _init_template_only(project_root, profile)

    # Step 4: Create docs/ lifecycle directories
    _create_docs_dirs(project_root)

    # Step 5: Fire plugin post-init hook
    from gemstack.plugins import fire_post_init

    fire_post_init(project_root, profile)

    console.print("[green]✅ Project initialized successfully![/green]")
    console.print("[dim]Run `gemstack check` to validate the setup.[/dim]")
    if not use_ai:
        console.print("[dim]Tip: Run `gemstack init --ai` to upgrade with AI analysis.[/dim]")


def _has_api_key() -> bool:
    """Check if a Gemini API key is configured."""
    import os

    from gemstack.core.config import GemstackConfig

    # Check env var first
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return True

    # Check config file
    config = GemstackConfig.load()
    return config.get_api_key() is not None


def _init_template_only(project_root: Path, profile: ProjectProfile) -> None:
    """Initialize using Jinja2 templates only (no AI)."""
    from gemstack.core.templates import render_agent_files

    agent_dir = project_root / ".agent"
    created = render_agent_files(profile, agent_dir)

    for filename in created:
        console.print(f"  [green]✔[/green] Created .agent/{filename}")


async def _init_with_ai(project_root: Path, profile: ProjectProfile) -> None:
    """Initialize using AI-powered deep analysis."""
    from gemstack.ai.bootstrap import AIBootstrapper
    from gemstack.core.config import GemstackConfig
    from gemstack.core.templates import render_agent_files

    config = GemstackConfig.load()
    model = config.default_model or "gemini-2.5-flash"

    bootstrapper = AIBootstrapper(model=model)
    result = await bootstrapper.analyze_with_fallback(profile)

    agent_dir = project_root / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    if result.ai_powered and not result.error:
        # Write AI-generated content
        ai_files = result.files()
        for filename, content in ai_files.items():
            (agent_dir / filename).write_text(content)
            console.print(f"  [green]✔[/green] Created .agent/{filename} [cyan](AI)[/cyan]")

        # Fill in any missing files with templates
        expected_files = {"ARCHITECTURE.md", "STYLE.md", "TESTING.md", "PHILOSOPHY.md", "STATUS.md"}
        missing = expected_files - set(ai_files.keys())
        if missing:
            from gemstack.core.templates import render_agent_files

            render_agent_files(profile, agent_dir)
            for filename in missing:
                console.print(f"  [green]✔[/green] Created .agent/{filename} [dim](template)[/dim]")
    else:
        if result.error:
            console.print(f"[yellow]⚠️  AI note: {result.error}[/yellow]")
        # Fall back to templates
        created = render_agent_files(profile, agent_dir)
        for filename in created:
            console.print(f"  [green]✔[/green] Created .agent/{filename}")


def _print_detection_results(profile: ProjectProfile) -> None:
    """Print a summary of what was detected."""
    from rich.table import Table

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("Language", profile.language)
    if profile.framework:
        table.add_row("Framework", profile.framework)
    if profile.package_manager:
        table.add_row("Package Manager", profile.package_manager)
    if profile.topologies:
        table.add_row("Topologies", ", ".join(t.value for t in profile.topologies))
    if profile.legacy_files:
        table.add_row("Legacy Files", ", ".join(p.name for p in profile.legacy_files))

    console.print(table)


def _create_docs_dirs(project_root: Path) -> None:
    """Create docs/ lifecycle directories with .gitkeep files."""
    for dirname in ["explorations", "designs", "plans", "archive"]:
        docs_dir = project_root / "docs" / dirname
        docs_dir.mkdir(parents=True, exist_ok=True)
        gitkeep = docs_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
        console.print(f"  [green]✔[/green] Created docs/{dirname}/")
