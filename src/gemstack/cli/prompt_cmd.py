"""gemstack prompt — Prompt template manager for ML/AI topology projects.

Manages versioned prompt files in a ``/prompts/`` directory,
tracks changes in STATUS.md, and supports version comparison.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console

from gemstack.utils.fileutil import write_atomic

console = Console()

prompt_app = typer.Typer(name="prompt", help="Prompt template manager (ML/AI)")


@prompt_app.command()
def create(
    name: str = typer.Argument(..., help="Prompt name (e.g., 'extraction')"),
    description: str = typer.Argument(..., help="Description of the prompt"),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Create a new versioned prompt template."""
    project_root = project_root.resolve()
    prompts_dir = project_root / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    prompt_dir = prompts_dir / name
    prompt_dir.mkdir(parents=True, exist_ok=True)

    version = "v1.0"
    prompt_file = prompt_dir / f"{version}.md"

    if prompt_file.exists():
        console.print(f"[yellow]⚠️  Prompt {name}/{version} already exists. Use `--force` to overwrite or bump the version.[/yellow]")
        raise typer.Exit(code=1)

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    content = (
        f"---\n"
        f"name: {name}\n"
        f"version: {version}\n"
        f"created: {now}\n"
        f"description: {description}\n"
        f"---\n\n"
        f"# {name} prompt\n\n"
        f"<!-- Write your prompt template below -->\n\n"
    )
    write_atomic(prompt_file, content)
    _update_prompt_changelog(project_root, name, version, description)

    console.print(f"[green]✅ Created prompt: {name}/{version}[/green]")


@prompt_app.command()
def bump(
    name: str = typer.Argument(..., help="Prompt name"),
    description: str = typer.Argument(..., help="What changed in this version"),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Create a new version of an existing prompt."""
    project_root = project_root.resolve()
    prompt_dir = project_root / "prompts" / name

    if not prompt_dir.exists():
        console.print(f"[red]❌ Prompt '{name}' not found. Run `gemstack prompt create {name}` to generate it.[/red]")
        raise typer.Exit(code=1)

    # Find current latest version
    versions = _get_versions(prompt_dir)
    if not versions:
        console.print(f"[red]❌ No versions found for prompt '{name}'.[/red]")
        raise typer.Exit(code=1)

    latest = versions[-1]
    # Bump minor version (v1.0 -> v1.1)
    match = re.match(r"v(\d+)\.(\d+)", latest)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        new_version = f"v{major}.{minor + 1}"
    else:
        new_version = "v1.1"

    # Copy latest content as starting point
    latest_file = prompt_dir / f"{latest}.md"
    base_content = latest_file.read_text() if latest_file.exists() else ""

    # Update frontmatter
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    new_content = re.sub(r"version:\s*v[\d.]+", f"version: {new_version}", base_content)
    new_content = re.sub(r"description:.*", f"description: {description}", new_content)
    if "created:" in new_content:
        new_content = new_content.replace(
            new_content.split("created:")[1].split("\n")[0],
            f" {now}",
        )

    new_file = prompt_dir / f"{new_version}.md"
    write_atomic(new_file, new_content)
    _update_prompt_changelog(project_root, name, new_version, description)

    console.print(f"[green]✅ Bumped {name}: {latest} → {new_version}[/green]")


@prompt_app.command("diff")
def diff_versions(
    name: str = typer.Argument(..., help="Prompt name"),
    v1: str = typer.Argument(..., help="First version (e.g., v1.0)"),
    v2: str = typer.Argument(..., help="Second version (e.g., v1.1)"),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Show differences between two prompt versions."""
    project_root = project_root.resolve()
    prompt_dir = project_root / "prompts" / name

    f1 = prompt_dir / f"{v1}.md"
    f2 = prompt_dir / f"{v2}.md"

    if not f1.exists():
        console.print(f"[red]❌ Version {v1} not found for prompt '{name}'.[/red]")
        raise typer.Exit(code=1)
    if not f2.exists():
        console.print(f"[red]❌ Version {v2} not found for prompt '{name}'.[/red]")
        raise typer.Exit(code=1)

    import difflib

    lines1 = f1.read_text().splitlines(keepends=True)
    lines2 = f2.read_text().splitlines(keepends=True)

    diff = difflib.unified_diff(lines1, lines2, fromfile=f"{name}/{v1}", tofile=f"{name}/{v2}")
    diff_text = "".join(diff)

    if diff_text:
        console.print(diff_text)
    else:
        console.print(f"[dim]No differences between {v1} and {v2}.[/dim]")


@prompt_app.command()
def rollback(
    name: str = typer.Argument(..., help="Prompt name"),
    version: str = typer.Argument(..., help="Version to rollback to"),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Rollback to a specific prompt version (mark as current)."""
    project_root = project_root.resolve()
    prompt_dir = project_root / "prompts" / name

    target_file = prompt_dir / f"{version}.md"
    if not target_file.exists():
        console.print(f"[red]❌ Version {version} not found.[/red]")
        raise typer.Exit(code=1)

    _update_prompt_changelog(project_root, name, version, f"Rolled back to {version}")
    console.print(f"[green]✅ Rolled back {name} → {version}[/green]")


# ── Helpers ────────────────────────────────────────────────────────


def _get_versions(prompt_dir: Path) -> list[str]:
    """Get sorted list of version strings from a prompt directory."""
    versions: list[str] = []
    for f in sorted(prompt_dir.glob("v*.md")):
        versions.append(f.stem)
    return versions


def _update_prompt_changelog(project_root: Path, name: str, version: str, description: str) -> None:
    """Update the Prompt Versioning Changelog in STATUS.md."""
    status_path = project_root / ".agent" / "STATUS.md"
    if not status_path.exists():
        return

    content = status_path.read_text()
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    entry = f"| {name} | {version} | {now} | {description} |"

    # Insert into the changelog table if it exists
    marker = "## Prompt Versioning Changelog"
    if marker in content:
        # Add entry after the table header
        table_end = content.find("\n\n", content.find(marker))
        if table_end == -1:
            table_end = len(content)
        content = content[:table_end] + f"\n{entry}" + content[table_end:]
        write_atomic(status_path, content)
