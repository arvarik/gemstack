"""MCP server exposing Gemstack project context to any MCP-compatible agent.

Uses FastMCP from the `mcp` SDK for simplified tool/resource registration.
Requires the `gemstack[mcp]` optional dependency.

Resources: Read-only access to all .agent/ markdown files.
Tools: gemstack_status, gemstack_route, gemstack_compile, gemstack_check, gemstack_diff.
Prompts: The 5 workflow step templates as reusable prompts.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def create_server(project_root: Path, **server_kwargs: object):  # type: ignore[no-untyped-def]
    """Create a FastMCP server instance bound to a project directory.

    Args:
        project_root: Path to the project root to serve context from.
        **server_kwargs: Additional keyword arguments passed to FastMCP
            constructor (e.g., host, port for SSE transport).

    Returns:
        A configured FastMCP server instance.
    """
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("gemstack", **server_kwargs)  # type: ignore[arg-type]

    # ─── Resources: Read-only access to .agent/ files ──────────────────

    @mcp.resource("gemstack://agent/{filename}")
    def read_agent_file(filename: str) -> str:
        """Read an .agent/ markdown file.

        Provides access to ARCHITECTURE.md, STYLE.md, TESTING.md,
        PHILOSOPHY.md, and STATUS.md.

        The filename is validated to prevent path traversal attacks —
        resolved path must remain within the .agent/ directory.
        """
        agent_dir = project_root / ".agent"
        path = (agent_dir / filename).resolve()

        # Guard against path traversal (e.g., "../../../etc/passwd")
        if not path.is_relative_to(agent_dir.resolve()):
            msg = f"Access denied: path traversal detected in '{filename}'"
            raise PermissionError(msg)

        if not path.exists():
            msg = f"Resource not found: .agent/{filename}"
            raise FileNotFoundError(msg)
        return path.read_text()

    # ─── Tools: Actionable operations ──────────────────────────────────

    @mcp.tool()
    def gemstack_status() -> str:
        """Get the current project status including phase, feature, and blockers."""
        status_path = project_root / ".agent" / "STATUS.md"
        if not status_path.exists():
            return "No .agent/STATUS.md found. Run `gemstack init` first."
        return status_path.read_text()

    @mcp.tool()
    def gemstack_route() -> str:
        """Get the recommended next action based on current project state."""
        from gemstack.core.router import PhaseRouter

        router = PhaseRouter()
        decision = router.route(project_root)
        return (
            f"Action: {decision.action.value}\n"
            f"Next: {decision.next_command}\n"
            f"Reason: {decision.reason}"
        )

    @mcp.tool()
    def gemstack_compile(step: str, max_tokens: int | None = None) -> str:
        """Compile the full context prompt for a specific workflow step.

        Args:
            step: Workflow step to compile (e.g., 'step1-spec', 'step3-build').
            max_tokens: Optional max token budget for the compiled context.
        """
        from gemstack.core.compiler import ContextCompiler

        compiler = ContextCompiler()
        result = compiler.compile(
            step=step,
            project_root=project_root,
            max_tokens=max_tokens,
        )
        return result.total_content

    @mcp.tool()
    def gemstack_check() -> str:
        """Validate the project's .agent/ directory integrity."""
        from gemstack.core.validator import ProjectValidator

        validator = ProjectValidator()
        result = validator.validate(project_root)
        if result.passed:
            return "✅ All checks passed"
        return (
            f"❌ {len(result.errors)} errors:\n"
            + "\n".join(f"  - {e}" for e in result.errors)
        )

    @mcp.tool()
    def gemstack_diff() -> str:
        """Detect drift between .agent/ documentation and actual codebase."""
        from gemstack.core.differ import ContextDiffer

        differ = ContextDiffer()
        report = differ.analyze(project_root)
        return report.to_markdown()

    # ─── Prompts: Reusable workflow step templates ─────────────────────

    @mcp.prompt()
    def step1_spec() -> str:
        """Gemstack workflow: Step 1 — Define the feature and lock in contracts."""
        return _load_workflow_prompt("step1-spec")

    @mcp.prompt()
    def step2_trap() -> str:
        """Gemstack workflow: Step 2 — Write the task plan and failing test suite."""
        return _load_workflow_prompt("step2-trap")

    @mcp.prompt()
    def step3_build() -> str:
        """Gemstack workflow: Step 3 — Implement until all tests pass."""
        return _load_workflow_prompt("step3-build")

    @mcp.prompt()
    def step4_audit() -> str:
        """Gemstack workflow: Step 4 — Security and logic review."""
        return _load_workflow_prompt("step4-audit")

    @mcp.prompt()
    def step5_ship() -> str:
        """Gemstack workflow: Step 5 — Integrate, merge, deploy."""
        return _load_workflow_prompt("step5-ship")

    # ─── Phase 5 Tools: Bidirectional communication ─────────────────

    @mcp.tool()
    async def gemstack_run(
        step: str,
        feature: str,
        dry_run: bool = True,
    ) -> str:
        """Execute or dry-run a Gemstack workflow step.

        Args:
            step: Workflow step (e.g., 'step1-spec', 'step3-build').
            feature: Feature description (e.g., 'Add user notifications').
            dry_run: If True, compile context only without API call.

        This tool is async-safe — it works correctly under both
        stdio and SSE MCP transports (no nested event loop).
        """
        from gemstack.core.executor import StepExecutor

        executor = StepExecutor()
        result = await executor.execute(
            step=step,
            feature=feature,
            project_root=project_root,
            dry_run=dry_run,
        )
        return result.summary()

    @mcp.tool()
    def gemstack_costs(feature: str | None = None) -> str:
        """Get cost tracking data for API usage.

        Args:
            feature: Optional feature name to filter costs for.
        """
        from gemstack.core.cost_tracker import CostTracker

        tracker = CostTracker(project_root)
        summary = tracker.get_summary(feature=feature)
        return (
            f"Total cost: ${summary.total_cost_usd:.4f}\n"
            f"Input tokens: {summary.total_input_tokens:,}\n"
            f"Output tokens: {summary.total_output_tokens:,}\n"
            f"Records: {summary.record_count}\n"
            f"By step: {summary.by_step}\n"
            f"By feature: {summary.by_feature}"
        )

    return mcp


def _load_workflow_prompt(step: str) -> str:
    """Load a bundled workflow step markdown file as a prompt."""
    from importlib.resources import files

    try:
        workflows = files("gemstack.data.workflows")
        resource = workflows / f"{step}.md"
        if hasattr(resource, "read_text"):
            return resource.read_text()
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        pass

    return f"Workflow step '{step}' not found in bundled data."
