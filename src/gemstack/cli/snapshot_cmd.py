"""gemstack snapshot — Portable context bundles.

Creates a single-file snapshot of the project's agent context,
suitable for pasting into AI chat windows or onboarding new team members.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from gemstack.core.fileutil import write_atomic

console = Console()

_AGENT_FILES = [
    "ARCHITECTURE.md",
    "STYLE.md",
    "TESTING.md",
    "PHILOSOPHY.md",
    "STATUS.md",
]


def snapshot(
    output: Path = typer.Option(
        "gemstack-snapshot.md", "--output", "-o", help="Output file path"
    ),
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
    compact: bool = typer.Option(
        False, "--compact", help="Minimal snapshot (<8k tokens)"
    ),
    for_step: str = typer.Option(
        "", "--for-step", help="Tune context for a specific workflow step"
    ),
) -> None:
    """Create a portable snapshot of the project's agent context."""
    project_root = project_root.resolve()
    agent_dir = project_root / ".agent"

    if not agent_dir.exists():
        console.print(
            "[red]❌ No .agent/ directory found. "
            "Run `gemstack init` first.[/red]"
        )
        raise typer.Exit(code=1)

    parts: list[str] = [
        f"# Gemstack Context Snapshot — {project_root.name}\n",
        f"_Generated for: {for_step or 'general context'}_\n",
    ]

    if for_step:
        # Use the compiler for step-specific context
        _snapshot_for_step(parts, project_root, for_step, compact)
    else:
        _snapshot_full(parts, agent_dir, project_root, compact)

    content = "\n".join(parts)
    output = output.resolve()
    write_atomic(output, content)

    token_est = len(content) // 4
    console.print(f"[green]✅ Snapshot saved to {output.name}[/green]")
    console.print(f"[dim]{len(content):,} chars (~{token_est:,} tokens)[/dim]")


def _snapshot_full(
    parts: list[str],
    agent_dir: Path,
    project_root: Path,
    compact: bool,
) -> None:
    """Assemble full snapshot from .agent/ files."""
    for filename in _AGENT_FILES:
        path = agent_dir / filename
        if path.exists():
            content = path.read_text()
            if compact:
                # Truncate each file to ~1500 chars for compact mode
                content = content[:1500]
                if len(content) == 1500:
                    content += "\n\n_...truncated for compact mode..._"
            parts.append(f"\n---\n## {filename}\n\n{content}")

    # Include relevant source excerpts if not compact
    if not compact:
        import re

        status_path = agent_dir / "STATUS.md"
        if status_path.exists():
            status_content = status_path.read_text()
            section_match = re.search(
                r"##\s*Relevant Files\s*\n(.*?)(?=\n##|\Z)",
                status_content,
                re.DOTALL,
            )
            if section_match:
                parts.append("\n---\n## Relevant Source Files\n")
                for match in re.finditer(
                    r"[-*]\s*`?([^\s`]+)`?", section_match.group(1)
                ):
                    filepath = match.group(1).strip()
                    full_path = project_root / filepath
                    if full_path.exists() and full_path.is_file():
                        try:
                            src = full_path.read_text()[:3000]
                            parts.append(
                                f"\n### `{filepath}`\n\n```\n{src}\n```\n"
                            )
                        except OSError:
                            pass


def _snapshot_for_step(
    parts: list[str],
    project_root: Path,
    step: str,
    compact: bool,
) -> None:
    """Use the compiler to generate a step-specific snapshot."""
    try:
        from gemstack.core.compiler import ContextCompiler

        compiler = ContextCompiler()
        max_tokens = 2000 if compact else None
        result = compiler.compile(
            step=step,
            project_root=project_root,
            max_tokens=max_tokens,
        )
        parts.append(f"\n---\n## Compiled Context for `{step}`\n")
        parts.append(result.total_content)
    except FileNotFoundError:
        parts.append(f"\n[Unknown step: {step}]\n")
