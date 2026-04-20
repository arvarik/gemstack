"""gemstack hook — Git hook integration for process enforcement."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()

hook_app = typer.Typer(name="hook", help="Git hook management")

# Hook scripts — bash shebang, delegates to gemstack CLI
_HOOKS: dict[str, str] = {
    "pre-commit": """\
#!/usr/bin/env bash
# Gemstack pre-commit hook — validates .agent/ integrity
# Installed by: gemstack hook install

if command -v gemstack &> /dev/null; then
    gemstack check --project "$(git rev-parse --show-toplevel)" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ gemstack check failed. Fix .agent/ issues before committing."
        exit 1
    fi
fi
""",
    "pre-push": """\
#!/usr/bin/env bash
# Gemstack pre-push hook — prevents pushing unfinished features
# Installed by: gemstack hook install

if command -v gemstack &> /dev/null; then
    ROOT="$(git rev-parse --show-toplevel)"
    STATUS_FILE="$ROOT/.agent/STATUS.md"
    if [ -f "$STATUS_FILE" ]; then
        STATE=$(grep -oP '\\[STATE:\\s*\\K\\w+' "$STATUS_FILE" 2>/dev/null || echo "")
        if [ "$STATE" = "IN_PROGRESS" ]; then
            echo "⚠️  STATUS.md state is IN_PROGRESS. Complete or update before pushing."
            echo "   Run: gemstack phase <next-phase>"
            exit 1
        fi
    fi
fi
""",
    "post-merge": """\
#!/usr/bin/env bash
# Gemstack post-merge hook — checks for context drift after merge
# Installed by: gemstack hook install

if command -v gemstack &> /dev/null; then
    ROOT="$(git rev-parse --show-toplevel)"
    if [ -d "$ROOT/.agent" ]; then
        echo "🔍 Checking for context drift after merge..."
        gemstack diff --project "$ROOT" 2>/dev/null || true
    fi
fi
""",
}


@hook_app.command()
def install(
    pre_commit: bool = typer.Option(False, "--pre-commit", help="Install only pre-commit hook"),
    pre_push: bool = typer.Option(False, "--pre-push", help="Install only pre-push hook"),
    post_merge: bool = typer.Option(False, "--post-merge", help="Install only post-merge hook"),
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Install git hooks that enforce Gemstack conventions."""
    project_root = project_root.resolve()
    hooks_dir = project_root / ".git" / "hooks"

    if not hooks_dir.exists():
        console.print("[red]❌ No .git/hooks/ directory found. Are you in a git repository?[/red]")
        raise typer.Exit(code=1)

    # Determine which hooks to install
    if pre_commit or pre_push or post_merge:
        selected: dict[str, str] = {}
        if pre_commit:
            selected["pre-commit"] = _HOOKS["pre-commit"]
        if pre_push:
            selected["pre-push"] = _HOOKS["pre-push"]
        if post_merge:
            selected["post-merge"] = _HOOKS["post-merge"]
    else:
        selected = _HOOKS

    count = 0
    for hook_name, script in selected.items():
        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            # Check if it's a gemstack-managed hook
            existing = hook_path.read_text()
            if "Gemstack" not in existing and "gemstack" not in existing:
                console.print(
                    f"  [yellow]⚠️[/yellow] Skipping {hook_name} (non-Gemstack hook already exists)"
                )
                continue

        hook_path.write_text(script)
        hook_path.chmod(0o755)
        console.print(f"  [green]✔[/green] Installed {hook_name}")
        count += 1

    console.print(f"[green]✅ Installed {count} git hooks[/green]")


@hook_app.command()
def uninstall(
    project_root: Path = typer.Option(".", "--project", "-p", help="Project root directory"),
) -> None:
    """Remove all Gemstack git hooks."""
    project_root = project_root.resolve()
    hooks_dir = project_root / ".git" / "hooks"

    if not hooks_dir.exists():
        console.print("[yellow]⚠️  No .git/hooks/ directory found.[/yellow]")
        return

    count = 0
    for hook_name in _HOOKS:
        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            content = hook_path.read_text()
            if "Gemstack" in content or "gemstack" in content:
                hook_path.unlink()
                console.print(f"  [green]✔[/green] Removed {hook_name}")
                count += 1

    console.print(f"[green]✅ Removed {count} Gemstack hooks[/green]")
