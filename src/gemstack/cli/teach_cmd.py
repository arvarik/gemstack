"""gemstack teach — Interactive tutorial.

Walks new users through the Gemstack workflow with 9 lessons
covering the .agent/ context system, the 5-step lifecycle,
and essential power-user commands.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# ---------------------------------------------------------------------------
# Lesson definitions
# ---------------------------------------------------------------------------

_LESSONS: list[dict[str, str]] = [
    # ── Section 1: Foundation ──────────────────────────────────────────
    {
        "section": "Foundation",
        "title": "What Is Gemstack?",
        "body": (
            "Gemstack is an [bold]opinionated AI agent orchestration framework[/bold].\n\n"
            "The core idea is simple: every AI coding agent — Gemini CLI, Antigravity,\n"
            "Cursor, Claude Desktop, Copilot — works better when it has [cyan]structured,\n"
            "project-specific context[/cyan] before it touches your code.\n\n"
            "Gemstack provides this through a [bold].agent/[/bold] directory at the root\n"
            "of your project. It contains 5 markdown files that describe your architecture,\n"
            "coding conventions, test strategy, product philosophy, and current status.\n\n"
            "These files are [bold]vendor-agnostic[/bold] — they work with any AI agent,\n"
            "not just Google's. You define your project once, and Gemstack ensures the\n"
            "right context is always injected.\n\n"
            "[dim]Key commands:[/dim]\n"
            "  gemstack init          Create the .agent/ directory\n"
            "  gemstack init --ai     AI-powered initialization (uses Gemini API)\n"
            "  gemstack doctor        Verify your environment is set up correctly"
        ),
    },
    {
        "section": "Foundation",
        "title": "The .agent/ Context Files",
        "body": (
            "Every Gemstack project has 5 context files in [bold].agent/[/bold]:\n\n"
            "[cyan]ARCHITECTURE.md[/cyan] — The technical anchor\n"
            "  Tech stack, API contracts, database schemas, system boundaries,\n"
            "  environment variables, and directory structure.\n"
            "  [dim]Truncation priority: High (kept long)[/dim]\n\n"
            "[cyan]STYLE.md[/cyan] — Coding conventions\n"
            "  Naming rules, file organization, design tokens, and explicitly\n"
            "  FORBIDDEN anti-patterns that agents must never use.\n"
            "  [dim]Truncation priority: Medium[/dim]\n\n"
            "[cyan]TESTING.md[/cyan] — Test strategy\n"
            "  Exact test commands, scenario tables, coverage matrices.\n"
            "  Varies by topology (route coverage for backend, component\n"
            "  state matrix for frontend, eval thresholds for ML/AI).\n"
            "  [dim]Truncation priority: Medium[/dim]\n\n"
            "[cyan]PHILOSOPHY.md[/cyan] — Product soul\n"
            "  Core beliefs, anti-goals, and decision principles that anchor\n"
            "  the AI's judgment on ambiguous tradeoffs.\n"
            "  [dim]Truncation priority: Medium[/dim]\n\n"
            "[cyan]STATUS.md[/cyan] — Live state tracker\n"
            "  Current lifecycle state ([STATE: ...]), active feature, lifecycle\n"
            "  checkboxes, relevant files, and blocking issues.\n"
            "  [dim]Truncation priority: Never truncated[/dim]\n\n"
            "[dim]The deterministic phase router (gemstack route) reads STATUS.md\n"
            "to calculate the next action. Because it's never truncated, the\n"
            "router always has full state visibility.[/dim]"
        ),
    },
    {
        "section": "Foundation",
        "title": "Setup & Configuration",
        "body": (
            "[bold]Installation:[/bold]\n"
            "  pipx install 'gemstack[all]'      # Recommended (isolated)\n"
            "  uv tool install 'gemstack[all]'    # Fastest\n"
            "  pip install 'gemstack[all]'         # Standard\n\n"
            "[bold]Gemini API Key:[/bold]\n"
            "  Get a free key at [link]https://aistudio.google.com[/link]\n\n"
            "  gemstack config set gemini-api-key YOUR_KEY\n"
            "  gemstack config list               # Verify (keys masked)\n\n"
            "[bold]Default Model:[/bold]\n"
            "  The default is [cyan]gemini-3.1-pro-preview[/cyan].\n"
            "  Change it with:\n\n"
            "  gemstack config set default-model gemini-3.1-flash-lite-preview\n\n"
            "[bold]Initialize a project:[/bold]\n"
            "  cd your-project/\n"
            "  gemstack init             # Template-based (no API key needed)\n"
            "  gemstack init --ai        # AI analyzes your codebase via Gemini\n"
            "  gemstack init --topology 'frontend,backend'   # Explicit topology\n\n"
            "[bold]Verify everything:[/bold]\n"
            "  gemstack doctor           # Checks Python, Git, API key, deps\n"
            "  gemstack check            # Validates .agent/ directory integrity"
        ),
    },
    # ── Section 2: The 5-Step Lifecycle ────────────────────────────────
    {
        "section": "The 5-Step Lifecycle",
        "title": "Step 1: Spec — Define the Feature",
        "body": (
            "[bold]Goal:[/bold] Define the feature, design UX, and lock in executable\n"
            "contracts before anyone writes implementation code.\n\n"
            "[bold]Command:[/bold]\n"
            "  gemstack run step1-spec --feature \"Add user notifications\"\n\n"
            "[bold]Roles composed:[/bold]\n"
            "  • [cyan]Product Visionary[/cyan] — Defines what the feature is and why\n"
            "  • [cyan]UI/UX Designer[/cyan] — Designs the user experience\n"
            "  • [cyan]Architect[/cyan] — Exports TypeScript/OpenAPI interfaces,\n"
            "    database schemas, and API contracts to ARCHITECTURE.md\n\n"
            "[bold]What happens:[/bold]\n"
            "  1. The human provides a feature description (--feature flag)\n"
            "  2. The Product Visionary and UX Designer define user-facing behavior\n"
            "  3. The Architect translates requirements into formal contracts —\n"
            "     API endpoints, request/response shapes, database changes\n"
            "  4. Contracts are written to ARCHITECTURE.md and docs/explorations/\n\n"
            "[bold]Rule:[/bold] No application code is written in this step. Contracts\n"
            "must be locked in before proceeding.\n\n"
            "[dim]Status: [STATE: INITIALIZED] → [STATE: IN_PROGRESS][/dim]"
        ),
    },
    {
        "section": "The 5-Step Lifecycle",
        "title": "Step 2: Trap — Write Failing Tests",
        "body": (
            "[bold]Goal:[/bold] Write the task plan and a failing test suite that defines\n"
            "exactly what \"done\" means — before any implementation exists.\n\n"
            "[bold]Command:[/bold]\n"
            "  gemstack run step2-trap --feature \"Add user notifications\"\n\n"
            "[bold]Roles composed:[/bold]\n"
            "  • [cyan]Planner[/cyan] — Breaks the feature into an ordered task list\n"
            "  • [cyan]SDET[/cyan] — Writes the failing test suite based on Step 1 contracts\n\n"
            "[bold]What happens:[/bold]\n"
            "  1. Read contracts from ARCHITECTURE.md and exploration docs\n"
            "  2. Create an ordered task plan in docs/plans/\n"
            "  3. Write test cases for every contract — happy paths, edge cases, errors\n"
            "  4. ALL tests MUST fail (there's no implementation yet)\n\n"
            "[bold]Why \"Trap\"?[/bold]\n"
            "  The test suite is a trap for the Builder AI in Step 3. The Builder can't\n"
            "  claim success — it must make every test pass. This prevents the most common\n"
            "  AI failure mode: generating code that [italic]looks[/italic] correct but "
            "doesn't work.\n\n"
            "[dim]Status: [STATE: IN_PROGRESS] → [STATE: READY_FOR_BUILD][/dim]"
        ),
    },
    {
        "section": "The 5-Step Lifecycle",
        "title": "Step 3: Build — Implement Until Tests Pass",
        "body": (
            "[bold]Goal:[/bold] Implement the feature and loop against the terminal until\n"
            "every test passes with Exit Code 0.\n\n"
            "[bold]Command:[/bold]\n"
            "  gemstack run step3-build --feature \"Add user notifications\"\n\n"
            "[bold]Roles composed:[/bold]\n"
            "  • [cyan]Principal Backend Engineer[/cyan] — Server-side logic, APIs, DB\n"
            "  • [cyan]Principal Frontend Engineer[/cyan] — UI components, state, client\n\n"
            "[bold]What happens:[/bold]\n"
            "  1. Read the task plan and contracts from Steps 1-2\n"
            "  2. Write the application code to fulfill each task\n"
            "  3. Static analysis first — type-checker and linter before tests\n"
            "  4. Compiler-in-the-Loop — run the full test suite in the terminal.\n"
            "     The AI is locked in this phase until Exit Code 0.\n"
            "     It reads stderr, fixes the code, and retries autonomously\n\n"
            "[bold]Circuit breaker (Bounded Reflexion):[/bold]\n"
            "  Max 3 build-test-fix attempts. If still failing after 3 loops:\n"
            "  • Revert changes to last known-good state\n"
            "  • Write a <reflection> block explaining what failed\n"
            "  • Yield back to the SDET for test review\n\n"
            "[dim]Status: [STATE: READY_FOR_BUILD] → [STATE: READY_FOR_AUDIT][/dim]"
        ),
    },
    {
        "section": "The 5-Step Lifecycle",
        "title": "Step 4: Audit — Security & Logic Review",
        "body": (
            "[bold]Goal:[/bold] Independent review by an AI that [bold]never saw the\n"
            "Builder's reasoning[/bold] — fresh context ensures genuine objectivity.\n\n"
            "[bold]Command:[/bold]\n"
            "  gemstack run step4-audit --feature \"Add user notifications\"\n\n"
            "[bold]Roles composed:[/bold]\n"
            "  • [cyan]Security Engineer[/cyan] — Vulnerabilities, injection, auth bypass\n"
            "  • [cyan]SDET[/cyan] — Edge cases, boundary conditions, integration checks\n\n"
            "[bold]What happens:[/bold]\n"
            "  1. Starts in a completely FRESH context window — no carry-over\n"
            "  2. Reviews implementation against contracts and test results\n"
            "  3. Security audit: input validation, auth, SQLi, XSS, CSRF, PII\n"
            "  4. Logic audit: contract compliance, error handling, edge cases\n"
            "  5. Writes findings to .agent/AUDIT_FINDINGS.md\n\n"
            "[bold]Routing after audit:[/bold]\n"
            "  • No findings → Proceed to Step 5: Ship\n"
            "  • Findings exist → Automatically reroutes back to Step 3: Build\n"
            "    with audit findings attached, creating an adversarial fix loop\n\n"
            "[dim]This is the same principle behind code review in human teams:\n"
            "the reviewer evaluates the code on its own merits, not swayed\n"
            "by the author's reasoning.[/dim]"
        ),
    },
    {
        "section": "The 5-Step Lifecycle",
        "title": "Step 5: Ship — Integrate and Deploy",
        "body": (
            "[bold]Goal:[/bold] Integrate, merge, deploy, archive, and reset STATUS.md\n"
            "for the next feature.\n\n"
            "[bold]Command:[/bold]\n"
            "  gemstack run step5-ship --feature \"Add user notifications\"\n\n"
            "[bold]Roles composed:[/bold]\n"
            "  • [cyan]DevOps Engineer[/cyan] — Integration, deployment, verification\n\n"
            "[bold]What happens:[/bold]\n"
            "  1. Final integration check — ensure all branches merge cleanly\n"
            "  2. Verify CI pipeline passes (if configured)\n"
            "  3. Deploy to staging/production (project-specific)\n"
            "  4. Archive feature documents to docs/archive/\n"
            "  5. Remove AUDIT_FINDINGS.md (findings addressed)\n"
            "  6. Reset STATUS.md — clear feature, uncheck boxes, set SHIPPED\n\n"
            "[bold]After shipping:[/bold]\n"
            "  gemstack replay \"Add user notifications\"    # Retrospective report\n"
            "  gemstack start \"Next feature\"               # Begin a new cycle\n\n"
            "[dim]Status: [STATE: READY_FOR_SHIP] → [STATE: SHIPPED][/dim]"
        ),
    },
    # ── Section 3: Power Tools ─────────────────────────────────────────
    {
        "section": "Power Tools",
        "title": "Essential Commands & Concepts",
        "body": (
            "[bold cyan]Context Compiler[/bold cyan] — JIT prompt assembly\n"
            "  gemstack compile step3-build               # View full prompt\n"
            "  gemstack compile step1-spec --token-budget 100000\n"
            "  Stitches together workflow + roles + phase + topology guardrails\n"
            "  + .agent/ context + source files + plugin hooks.\n\n"
            "[bold cyan]Phase Router[/bold cyan] — Deterministic next-action\n"
            "  gemstack route\n"
            "  Reads STATUS.md and AUDIT_FINDINGS.md to tell you exactly\n"
            "  what to do next. Never guesses — evaluates a fixed decision tree.\n\n"
            "[bold cyan]Drift Detection[/bold cyan] — Keep docs in sync\n"
            "  gemstack diff\n"
            "  Detects dependency drift, env var drift, and stale file refs\n"
            "  between your codebase and .agent/ documentation.\n\n"
            "[bold cyan]Validation[/bold cyan] — Structural integrity\n"
            "  gemstack check\n"
            "  Verifies all required files exist, STATUS.md has a valid state,\n"
            "  topology is declared, and custom plugin checks pass.\n\n"
            "[bold cyan]Topology Guardrails[/bold cyan] — Domain-specific rules\n"
            "  Declare [backend], [frontend], [ml-ai], etc. in ARCHITECTURE.md.\n"
            "  The compiler injects topology-specific constraints automatically\n"
            "  (e.g., anti-mocking rules for backend, hydration safety for frontend).\n\n"
            "[bold cyan]MCP Server[/bold cyan] — IDE integration\n"
            "  gemstack mcp serve              # Start the MCP server\n"
            "  gemstack mcp register --cursor  # Register with Cursor IDE\n"
            "  Exposes compile, diff, status, and route as MCP tools."
        ),
    },
]


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------


def teach(
    lesson: int = typer.Option(
        0, "--lesson", "-l", help="Jump to a specific lesson (1-9)"
    ),
    show_list: bool = typer.Option(
        False, "--list", help="Show the lesson index and exit"
    ),
) -> None:
    """Interactive tutorial walking through the Gemstack workflow."""
    total = len(_LESSONS)

    # --list: show the lesson index
    if show_list:
        _print_lesson_index()
        raise typer.Exit()

    # Validate lesson range
    if lesson < 0 or lesson > total:
        console.print(f"[red]❌ Lesson must be between 1 and {total}.[/red]")
        raise typer.Exit(code=1)

    # Welcome banner
    console.print(
        Panel(
            "[bold cyan]Welcome to the Gemstack Tutorial![/bold cyan]\n\n"
            f"This interactive walkthrough covers {total} lessons in 3 sections:\n"
            "  [bold]Foundation[/bold] — What Gemstack is, the .agent/ system, setup\n"
            "  [bold]The 5-Step Lifecycle[/bold] — Spec → Trap → Build → Audit → Ship\n"
            "  [bold]Power Tools[/bold] — Compiler, router, drift detection, MCP\n\n"
            "Press [bold]Enter[/bold] to continue, [bold]q[/bold] to quit, "
            "[bold]i[/bold] for lesson index.",
            title="🎓 gemstack teach",
            border_style="cyan",
        )
    )

    # Create a temporary sample project
    tmp_dir = tempfile.mkdtemp(prefix="gemstack-tutorial-")
    tmp_path = Path(tmp_dir)

    try:
        _setup_sample_project(tmp_path)
        console.print(f"[dim]Sample project created at: {tmp_path}[/dim]\n")

        start = (lesson - 1) if lesson >= 1 else 0
        current_section = ""

        for i, lesson_data in enumerate(_LESSONS[start:], start=start + 1):
            # Print section header on section change
            section = lesson_data["section"]
            if section != current_section:
                current_section = section
                console.print(
                    f"\n[bold magenta]━━━ {section} ━━━[/bold magenta]\n"
                )

            # Lesson panel
            console.print(
                Panel(
                    lesson_data["body"],
                    title=(
                        f"📘 Lesson {i}/{total}: {lesson_data['title']}"
                    ),
                    border_style="blue",
                    padding=(1, 2),
                )
            )

            # Prompt for next (unless last lesson)
            if i < total:
                try:
                    response = input(
                        "\n  Press Enter for next lesson"
                        " (q to quit, i for index): "
                    )
                    resp = response.strip().lower()
                    if resp == "q":
                        break
                    if resp == "i":
                        _print_lesson_index()
                        try:
                            response = input(
                                "\n  Press Enter to continue: "
                            )
                            if response.strip().lower() == "q":
                                break
                        except (EOFError, KeyboardInterrupt):
                            break
                except (EOFError, KeyboardInterrupt):
                    break

        console.print("\n[green]✅ Tutorial complete![/green]")
        console.print(
            "[dim]Get started: run `gemstack init` in your project, or\n"
            "`gemstack init --ai` for AI-powered initialization.[/dim]"
        )

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        console.print("[dim]Cleaned up tutorial project.[/dim]")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _print_lesson_index() -> None:
    """Print a formatted lesson index table."""
    table = Table(
        title="Gemstack Tutorial — Lesson Index",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="bold", width=3, justify="right")
    table.add_column("Section", style="magenta", width=22)
    table.add_column("Lesson", width=40)

    for i, lesson_data in enumerate(_LESSONS, start=1):
        table.add_row(str(i), lesson_data["section"], lesson_data["title"])

    console.print(table)
    console.print(
        "\n[dim]Jump to any lesson: gemstack teach --lesson 4[/dim]"
    )


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
        '[project]\nname = "tutorial-app"\n'
        'version = "0.1.0"\ndependencies = ["fastapi"]\n'
    )
