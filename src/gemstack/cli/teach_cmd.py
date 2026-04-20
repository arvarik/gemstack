"""gemstack teach — Interactive tutorial.

Walks new users through the Gemstack 5-step workflow
using a temporary sample project.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

_STEPS = [
    {
        "title": "Step 1: Spec — Define the Feature",
        "body": (
            "The first step is to clearly define what you're building.\n\n"
            "• Write a feature spec in `docs/explorations/`\n"
            "• Define acceptance criteria and user stories\n"
            "• Run `/step1-spec` to compile the context for your AI agent\n\n"
            "[dim]The agent receives your ARCHITECTURE.md, STYLE.md, and the spec "
            "to produce a detailed design document.[/dim]"
        ),
    },
    {
        "title": "Step 2: Trap — Write Failing Tests",
        "body": (
            "Before writing any code, lay the 'trap'.\n\n"
            "• Create a task plan breaking the feature into components\n"
            "• Write failing test suites that define the contract\n"
            "• Run `/step2-trap` to get the agent to produce these artifacts\n\n"
            "[dim]This ensures your tests exist BEFORE code, preventing "
            "the common AI failure mode of writing tests that pass by accident.[/dim]"
        ),
    },
    {
        "title": "Step 3: Build — Implement Until Tests Pass",
        "body": (
            "Now the agent writes code to make the tests pass.\n\n"
            "• Run `/step3-build` to start the implementation loop\n"
            "• The agent receives all context + failing tests\n"
            "• It iterates until the test suite is green\n\n"
            "[dim]The compiled context includes topology guardrails, ensuring "
            "the agent follows your project's conventions.[/dim]"
        ),
    },
    {
        "title": "Step 4: Audit — Security & Logic Review",
        "body": (
            "A fresh-context review catches what the builder missed.\n\n"
            "• Run `/step4-audit` to start the review\n"
            "• The auditor checks for security issues, logic bugs, and drift\n"
            "• Findings go into AUDIT_FINDINGS.md\n"
            "• If findings exist, the router reroutes back to Step 3\n\n"
            "[dim]This creates an adversarial feedback loop that "
            "dramatically improves code quality.[/dim]"
        ),
    },
    {
        "title": "Step 5: Ship — Integrate and Deploy",
        "body": (
            "Once the audit is clean, ship it!\n\n"
            "• Run `/step5-ship` to integrate and merge\n"
            "• The agent creates the PR, updates STATUS.md\n"
            "• Feature artifacts are archived to `docs/archive/`\n"
            "• STATUS.md state becomes SHIPPED\n\n"
            "[dim]The lifecycle is complete. Run `gemstack replay <feature>` "
            "to generate a retrospective report.[/dim]"
        ),
    },
]


def teach(
    step: int = typer.Option(
        0, "--step", "-s", help="Jump to a specific step (1-5)"
    ),
) -> None:
    """Interactive tutorial walking through the Gemstack workflow."""
    if step < 0 or step > 5:
        console.print("[red]❌ Step must be between 1 and 5.[/red]")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            "[bold cyan]Welcome to the Gemstack Tutorial![/bold cyan]\n\n"
            "This interactive walkthrough covers the 5-step workflow.\n"
            "Press [bold]Enter[/bold] to continue, [bold]q[/bold] to quit.",
            title="🎓 gemstack teach",
            border_style="cyan",
        )
    )

    # Create a temporary sample project for hands-on practice
    tmp_dir = tempfile.mkdtemp(prefix="gemstack-tutorial-")
    tmp_path = Path(tmp_dir)

    try:
        # Set up sample project structure
        _setup_sample_project(tmp_path)
        console.print(f"[dim]Sample project created at: {tmp_path}[/dim]\n")

        start = (step - 1) if step >= 1 else 0
        for i, step_data in enumerate(_STEPS[start:], start=start + 1):
            console.print(
                Panel(
                    step_data["body"],
                    title=f"📘 {step_data['title']}",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

            if i < len(_STEPS):
                try:
                    response = input("\n  Press Enter for next step (q to quit): ")
                    if response.strip().lower() == "q":
                        break
                except (EOFError, KeyboardInterrupt):
                    break

        console.print("\n[green]✅ Tutorial complete![/green]")
        console.print("[dim]Start using Gemstack: `gemstack init` in your project.[/dim]")

    finally:
        # Clean up
        shutil.rmtree(tmp_dir, ignore_errors=True)
        console.print("[dim]Cleaned up tutorial project.[/dim]")


def _setup_sample_project(root: Path) -> None:
    """Create a minimal sample project for tutorial practice."""
    (root / "src").mkdir()
    (root / "src" / "main.py").write_text(
        '"""Sample application."""\n\nprint("Hello, Gemstack!")\n'
    )
    (root / "tests").mkdir()
    (root / "tests" / "test_main.py").write_text(
        '"""Sample test."""\n\n\ndef test_hello():\n    assert True\n'
    )
    (root / "pyproject.toml").write_text(
        '[project]\nname = "tutorial-app"\nversion = "0.1.0"\n'
        'dependencies = ["fastapi"]\n'
    )
