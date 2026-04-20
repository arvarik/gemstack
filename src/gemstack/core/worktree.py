"""Git worktree management — parallel agent execution via git worktrees.

Manages creation, status tracking, merging, and cleanup of git worktrees
to enable parallel development (e.g., frontend + backend simultaneously).
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from gemstack.core.fileutil import write_atomic

logger = logging.getLogger(__name__)


@dataclass
class WorktreeInfo:
    """Information about a single git worktree."""

    path: str
    branch: str
    commit: str = ""
    is_main: bool = False


@dataclass
class WorktreeResult:
    """Result of a worktree operation."""

    success: bool
    message: str
    worktrees: list[WorktreeInfo] = field(default_factory=list)


class WorktreeManager:
    """Manages git worktrees for parallel agent execution.

    Provides create, status, merge, and cleanup operations
    with STATUS.md integration for tracking active worktrees.
    """

    def create(
        self,
        project_root: Path,
        branches: dict[str, str],
    ) -> WorktreeResult:
        """Create worktrees for parallel development.

        Args:
            project_root: Path to the git repository root.
            branches: Dict mapping role to branch name
                      (e.g., {"backend": "feat/oauth-backend"}).

        Returns:
            WorktreeResult with created worktrees.
        """
        created: list[WorktreeInfo] = []

        for role, branch in branches.items():
            worktree_path = project_root.parent / f"{project_root.name}-{role}"

            try:
                subprocess.run(  # noqa: S603
                    ["git", "worktree", "add", str(worktree_path), "-b", branch],  # noqa: S607
                    cwd=str(project_root),
                    check=True,
                    capture_output=True,
                    text=True,
                )
                created.append(WorktreeInfo(
                    path=str(worktree_path),
                    branch=branch,
                ))
                logger.info(f"Created worktree: {worktree_path} ({branch})")
            except subprocess.CalledProcessError as e:
                return WorktreeResult(
                    success=False,
                    message=f"Failed to create worktree for {role}: {e.stderr.strip()}",
                )
            except FileNotFoundError:
                return WorktreeResult(
                    success=False,
                    message="git not found — worktrees require git",
                )

        # Update STATUS.md with active worktrees
        self._update_status_worktrees(project_root, created)

        return WorktreeResult(
            success=True,
            message=f"Created {len(created)} worktrees",
            worktrees=created,
        )

    def status(self, project_root: Path) -> WorktreeResult:
        """List active git worktrees.

        Args:
            project_root: Path to the git repository root.

        Returns:
            WorktreeResult with active worktree list.
        """
        try:
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],  # noqa: S607
                cwd=str(project_root),
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return WorktreeResult(success=False, message=str(e))

        worktrees: list[WorktreeInfo] = []
        current: dict[str, str] = {}

        for line in result.stdout.splitlines():
            if line.startswith("worktree "):
                if current:
                    worktrees.append(self._parse_worktree_entry(current))
                current = {"path": line.split(" ", 1)[1]}
            elif line.startswith("HEAD "):
                current["commit"] = line.split(" ", 1)[1][:8]
            elif line.startswith("branch "):
                current["branch"] = line.split(" ", 1)[1]
                # Strip refs/heads/ prefix
                if current["branch"].startswith("refs/heads/"):
                    current["branch"] = current["branch"][len("refs/heads/"):]

        if current:
            worktrees.append(self._parse_worktree_entry(current))

        return WorktreeResult(
            success=True,
            message=f"{len(worktrees)} worktrees found",
            worktrees=worktrees,
        )

    def merge(self, project_root: Path, branch: str | None = None) -> WorktreeResult:
        """Merge a worktree branch back into the current branch.

        Args:
            project_root: Path to the git repository root.
            branch: Branch to merge (if None, merges all worktree branches).

        Returns:
            WorktreeResult with merge status.
        """
        status = self.status(project_root)
        if not status.success:
            return status

        target_branches = (
            [branch] if branch
            else [wt.branch for wt in status.worktrees if not wt.is_main]
        )

        for target in target_branches:
            try:
                subprocess.run(  # noqa: S603
                    ["git", "merge", target, "--no-ff"],  # noqa: S607
                    cwd=str(project_root),
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logger.info(f"Merged branch: {target}")
            except subprocess.CalledProcessError as e:
                return WorktreeResult(
                    success=False,
                    message=f"Failed to merge {target}: {e.stderr.strip()}",
                )

        return WorktreeResult(
            success=True,
            message=f"Merged {len(target_branches)} branches",
        )

    def cleanup(self, project_root: Path) -> WorktreeResult:
        """Remove all non-main worktrees.

        Args:
            project_root: Path to the git repository root.

        Returns:
            WorktreeResult with cleanup status.
        """
        status = self.status(project_root)
        if not status.success:
            return status

        removed = 0
        for wt in status.worktrees:
            if wt.is_main:
                continue
            try:
                subprocess.run(  # noqa: S603
                    ["git", "worktree", "remove", wt.path, "--force"],  # noqa: S607
                    cwd=str(project_root),
                    check=True,
                    capture_output=True,
                    text=True,
                )
                removed += 1
                logger.info(f"Removed worktree: {wt.path}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to remove worktree {wt.path}: {e.stderr.strip()}")

        return WorktreeResult(
            success=True,
            message=f"Removed {removed} worktrees",
        )

    def _parse_worktree_entry(self, entry: dict[str, str]) -> WorktreeInfo:
        """Parse a porcelain worktree entry."""
        path = entry.get("path", "")
        branch = entry.get("branch", "(detached)")
        # Detect main/master regardless of refs/heads/ prefix presence
        branch_basename = branch.rsplit("/", 1)[-1] if "/" in branch else branch
        return WorktreeInfo(
            path=path,
            branch=branch,
            commit=entry.get("commit", ""),
            is_main="branch" not in entry or branch_basename in ("main", "master"),
        )

    def _update_status_worktrees(
        self, project_root: Path, worktrees: list[WorktreeInfo]
    ) -> None:
        """Update STATUS.md with active worktree information."""
        status_path = project_root / ".agent" / "STATUS.md"
        if not status_path.exists():
            return

        content = status_path.read_text()

        # Build worktree table
        table_lines = [
            "\n## Active Worktrees\n",
            "| Path | Branch | Status |",
            "|------|--------|--------|",
        ]
        for wt in worktrees:
            table_lines.append(f"| `{wt.path}` | `{wt.branch}` | Active |")
        table_content = "\n".join(table_lines) + "\n"

        # Replace existing section or append
        if "## Active Worktrees" in content:
            content = re.sub(
                r"## Active Worktrees\n.*?(?=\n## |\Z)",
                table_content.lstrip("\n"),
                content,
                flags=re.DOTALL,
            )
        else:
            content = content.rstrip() + "\n" + table_content

        write_atomic(status_path, content)

    async def run_parallel(
        self,
        project_root: Path,
        branches: dict[str, str],
        step: str,
        feature: str,
        model: str = "gemini-2.5-flash",
    ) -> list[dict[str, object]]:
        """Run a step concurrently across multiple worktrees.

        Creates worktrees, executes the step in each one via
        ``StepExecutor``, and returns a list of results.

        Uses ``asyncio.TaskGroup`` on Python 3.11+ for structured
        concurrency; falls back to sequential execution on 3.10.

        Args:
            project_root: The main project root.
            branches: Mapping of branch name → worktree label.
            step: Workflow step to execute.
            feature: Feature description.
            model: Gemini model name.

        Returns:
            List of result dicts (one per worktree).
        """
        import asyncio
        import sys

        from gemstack.core.executor import StepExecutor

        # Create worktrees first (synchronous git operations)
        create_result = self.create(project_root, branches)
        if not create_result.success:
            return [{"error": create_result.message, "branch": "all"}]

        results: list[dict[str, object]] = []

        async def _run_in_worktree(wt: WorktreeInfo) -> dict[str, object]:
            executor = StepExecutor(model=model)
            wt_path = Path(wt.path)
            result = await executor.execute(
                step=step,
                feature=feature,
                project_root=wt_path,
                dry_run=False,
            )
            return {
                "branch": wt.branch,
                "path": wt.path,
                "success": result.success,
                "files_written": result.files_written,
                "cost_usd": result.cost_usd,
                "error": result.error,
            }

        # Use TaskGroup on 3.11+, sequential fallback on 3.10
        if sys.version_info >= (3, 11):
            try:
                async with asyncio.TaskGroup() as tg:
                    tasks = [
                        tg.create_task(_run_in_worktree(wt))
                        for wt in create_result.worktrees
                        if not wt.is_main
                    ]
                results = [t.result() for t in tasks]
            except ExceptionGroup as eg:
                # Collect results from successful tasks
                for t in tasks:
                    if t.done() and not t.cancelled() and t.exception() is None:
                        results.append(t.result())
                # Add error entries for failed tasks
                for exc in eg.exceptions:
                    results.append({
                        "branch": "unknown",
                        "path": "",
                        "success": False,
                        "files_written": [],
                        "cost_usd": 0.0,
                        "error": str(exc),
                    })
        else:
            for wt in create_result.worktrees:
                if not wt.is_main:
                    result = await _run_in_worktree(wt)
                    results.append(result)

        return results

