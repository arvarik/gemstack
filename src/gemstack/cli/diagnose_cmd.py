"""gemstack diagnose — Unified diagnostic dashboard.

Aggregates ``doctor`` (environment), ``check`` (.agent/ integrity),
and ``diff`` (context drift) into a single report so users don't need
to remember which diagnostic command to run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from gemstack.cli.context import console


def diagnose(
    project_root: Annotated[
        Path, typer.Argument(help="Project root directory", resolve_path=True)
    ] = Path("."),
) -> None:
    """Run all diagnostics (doctor + check + diff) in a single dashboard."""
    console.print(
        Panel(
            "[bold cyan]Running unified diagnostics...[/bold cyan]",
            title="🩺 gemstack diagnose",
            border_style="cyan",
        )
    )

    issues: list[tuple[str, str, str]] = []  # (category, severity, message)

    # ── Section 1: Environment (doctor) ─────────────────────────
    issues.extend(_run_doctor_checks())

    # ── Section 2: .agent/ Integrity (check) ────────────────────
    issues.extend(_run_check_validation(project_root))

    # ── Section 3: Context Drift (diff) ─────────────────────────
    issues.extend(_run_diff_analysis(project_root))

    # ── Render unified table ────────────────────────────────────
    if not issues:
        console.print(
            Panel(
                "[bold green]All diagnostics passed![/bold green]\n"
                "[dim]Environment, .agent/ integrity, and context drift — all clear.[/dim]",
                title="✅ System Health",
                border_style="green",
            )
        )
        return

    table = Table(title="Diagnostic Results", show_lines=True)
    table.add_column("Category", style="bold", width=14)
    table.add_column("Severity", justify="center", width=8)
    table.add_column("Issue")

    has_errors = False
    for category, severity, message in issues:
        sev_style = "[red]ERROR[/red]" if severity == "ERROR" else "[yellow]WARN[/yellow]"
        if severity == "ERROR":
            has_errors = True
        table.add_row(category, sev_style, message)

    console.print(table)

    if has_errors:
        console.print(
            "\n[dim]Fix the errors above, then re-run "
            "`gemstack diagnose` to verify.[/dim]"
        )
        raise typer.Exit(code=1)


def _run_doctor_checks() -> list[tuple[str, str, str]]:
    """Run environment checks (subset of ``gemstack doctor``)."""
    import platform

    issues: list[tuple[str, str, str]] = []

    # Antigravity directory
    antigravity_dir = Path.home() / ".gemini" / "antigravity"
    if not antigravity_dir.exists():
        issues.append(("Environment", "WARN", "Antigravity directory not found"))

    # Global workflows
    workflows_dir = antigravity_dir / "global_workflows"
    if not workflows_dir.exists():
        issues.append(("Environment", "WARN", "Global workflows directory not found"))

    # Bundled data
    try:
        from importlib.resources import files

        files("gemstack.data")
    except Exception:
        issues.append(("Environment", "ERROR", "Bundled data not accessible"))

    # Platform info (informational — check for known issues)
    if platform.system() == "Windows" and not _is_wsl():
        issues.append(
            ("Environment", "WARN", "Native Windows detected — WSL is recommended")
        )

    return issues


def _run_check_validation(project_root: Path) -> list[tuple[str, str, str]]:
    """Run .agent/ validation (subset of ``gemstack check``)."""
    issues: list[tuple[str, str, str]] = []

    agent_dir = project_root / ".agent"
    if not agent_dir.exists():
        issues.append(
            (
                "Integrity",
                "ERROR",
                "No .agent/ directory found — run `gemstack init`",
            )
        )
        return issues

    try:
        from gemstack.project.validator import ProjectValidator

        validator = ProjectValidator()
        result = validator.validate(project_root, auto_fix=False)

        for err in result.errors:
            issues.append(("Integrity", "ERROR", err))
        for warn in result.warnings:
            issues.append(("Integrity", "WARN", warn))
    except Exception as e:
        issues.append(("Integrity", "ERROR", f"Validation failed: {e}"))

    return issues


def _run_diff_analysis(project_root: Path) -> list[tuple[str, str, str]]:
    """Run context drift detection (subset of ``gemstack diff``)."""
    issues: list[tuple[str, str, str]] = []

    agent_dir = project_root / ".agent"
    if not agent_dir.exists():
        # Already reported by check — skip silently
        return issues

    try:
        from gemstack.utils.differ import ContextDiffer

        differ = ContextDiffer()
        report = differ.analyze(project_root)

        if report.has_drift:
            for dep in report.new_dependencies:
                issues.append(("Drift", "WARN", f"New dependency: {dep}"))
            for dep in report.removed_dependencies:
                issues.append(("Drift", "WARN", f"Removed dependency: {dep}"))
            for var in report.new_env_vars:
                issues.append(("Drift", "WARN", f"New env var: {var}"))
            for var in report.removed_env_vars:
                issues.append(("Drift", "WARN", f"Removed env var: {var}"))
            for ref in report.stale_file_refs:
                issues.append(("Drift", "WARN", f"Stale file ref: {ref}"))
    except Exception as e:
        issues.append(("Drift", "WARN", f"Drift analysis failed: {e}"))

    return issues


def _is_wsl() -> bool:
    """Detect if running inside WSL."""
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except (FileNotFoundError, OSError):
        return False
