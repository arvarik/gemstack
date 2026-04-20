"""Tests for the autonomous step executor."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest


class TestStepExecutor:
    """Tests for the StepExecutor class."""

    @pytest.fixture
    def project_with_agent(self, tmp_path: Path) -> Path:
        """Create a project with .agent/ directory."""
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("# Status\n\n[STATE: INITIALIZED]\n")
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n\n**Topology:** [backend]\n")
        return tmp_path

    def test_unknown_step_returns_error(self, project_with_agent: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        result = asyncio.run(
            executor.execute(
                step="step99-unknown",
                feature="test",
                project_root=project_with_agent,
            )
        )
        assert not result.success
        assert "Unknown step" in (result.error or "")

    def test_dry_run_compiles_context(self, project_with_agent: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        result = asyncio.run(
            executor.execute(
                step="step1-spec",
                feature="Add user notifications",
                project_root=project_with_agent,
                dry_run=True,
            )
        )
        assert result.success
        assert result.dry_run
        assert result.compiled_tokens > 0
        assert result.step == "step1-spec"
        assert result.feature == "Add user notifications"

    def test_dry_run_lists_expected_files(self, project_with_agent: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        result = asyncio.run(
            executor.execute(
                step="step1-spec",
                feature="test",
                project_root=project_with_agent,
                dry_run=True,
            )
        )
        assert "ARCHITECTURE.md" in result.files_written

    def test_dry_run_for_audit_step(self, project_with_agent: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        result = asyncio.run(
            executor.execute(
                step="step4-audit",
                feature="test",
                project_root=project_with_agent,
                dry_run=True,
            )
        )
        assert result.success
        assert "AUDIT_FINDINGS.md" in result.files_written

    def test_missing_agent_dir(self, tmp_path: Path) -> None:
        """Execute fails gracefully when .agent/ is missing."""
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        # The compile step will fail with FileNotFoundError
        result = asyncio.run(
            executor.execute(
                step="step1-spec",
                feature="test",
                project_root=tmp_path,
                dry_run=True,
            )
        )
        # Should fail because the compiler can't find workflow files
        # but should not crash
        assert isinstance(result.success, bool)

    def test_summary_dry_run_format(self, project_with_agent: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        result = asyncio.run(
            executor.execute(
                step="step1-spec",
                feature="test",
                project_root=project_with_agent,
                dry_run=True,
            )
        )
        summary = result.summary()
        assert "DRY RUN" in summary
        assert "step1-spec" in summary

    def test_summary_error_format(self) -> None:
        from gemstack.orchestration.executor import ExecutionResult

        result = ExecutionResult(
            step="step1-spec",
            feature="test",
            success=False,
            error="Something broke",
        )
        assert "❌" in result.summary()
        assert "Something broke" in result.summary()

    def test_summary_success_format(self) -> None:
        from gemstack.orchestration.executor import ExecutionResult

        result = ExecutionResult(
            step="step1-spec",
            feature="test",
            success=True,
            compiled_tokens=1000,
            output_tokens=500,
            cost_usd=0.01,
            files_written=["ARCHITECTURE.md"],
            next_step="/step2-trap",
            duration_seconds=2.5,
        )
        summary = result.summary()
        assert "✅" in summary
        assert "1,000" in summary
        assert "$0.01" in summary

    def test_write_heuristic_step1_spec(self, project_with_agent: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        files = executor._write_heuristic("step1-spec", "# Spec output", project_with_agent)
        assert "docs/explorations/spec-output.md" in files
        assert (project_with_agent / "docs" / "explorations" / "spec-output.md").exists()

    def test_write_heuristic_step4_audit(self, project_with_agent: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        files = executor._write_heuristic("step4-audit", "# Findings", project_with_agent)
        assert ".agent/AUDIT_FINDINGS.md" in files

    def test_write_results_with_file_blocks(self, project_with_agent: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        response = (
            "Here is the output:\n```file:docs/ARCHITECTURE.md\n# Updated Architecture\n```\n"
        )
        files = executor._write_results("step1-spec", response, project_with_agent)
        assert "docs/ARCHITECTURE.md" in files
        content = (project_with_agent / "docs" / "ARCHITECTURE.md").read_text()
        assert "Updated Architecture" in content

    def test_cost_budget_enforcement(self, project_with_agent: Path) -> None:
        """Executor respects cost limits."""
        from gemstack.orchestration.cost_tracker import CostTracker
        from gemstack.orchestration.executor import StepExecutor

        # Pre-fill cost data to exceed budget
        tracker = CostTracker(
            project_with_agent,
            max_cost_per_feature=0.01,
        )
        tracker.record(
            step="step1-spec",
            feature="test-feature",
            model="gemini-2.5-flash",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
        )

        executor = StepExecutor(max_cost=0.01)
        result = asyncio.run(
            executor.execute(
                step="step1-spec",
                feature="test-feature",
                project_root=project_with_agent,
            )
        )
        assert not result.success
        assert "limit" in (result.error or "").lower()


class TestPathTraversalGuard:
    """Tests for P0-1/P0-2: path traversal prevention."""

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        return tmp_path

    def test_rejects_parent_traversal(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        result = executor._validate_write_path("../../../etc/cron.d/backdoor", project)
        assert result is None

    def test_rejects_absolute_path(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        assert executor._validate_write_path("/etc/passwd", project) is None

    def test_rejects_empty_path(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        assert executor._validate_write_path("", project) is None
        assert executor._validate_write_path("   ", project) is None

    def test_rejects_null_bytes(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        assert executor._validate_write_path("file\x00.md", project) is None

    def test_rejects_windows_absolute(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        assert executor._validate_write_path("C:\\Windows\\foo", project) is None

    def test_accepts_valid_relative_path(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        result = executor._validate_write_path("docs/test.md", project)
        assert result is not None
        assert result.is_relative_to(project.resolve())

    def test_accepts_nested_path(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        result = executor._validate_write_path("docs/explorations/spec.md", project)
        assert result is not None

    def test_write_results_skips_traversal(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        executor = StepExecutor()
        response = (
            "```file:../../../etc/evil\n"
            "malicious content\n"
            "```\n"
            "```file:docs/good.md\n"
            "good content\n"
            "```\n"
        )
        files = executor._write_results("step1-spec", response, project)
        # Only the safe file should be written
        assert "docs/good.md" in files
        assert len(files) == 1
        assert (project / "docs" / "good.md").read_text() == "good content\n"


class TestConcurrencyLock:
    """Tests for P0-3: lockfile-based concurrency guard."""

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        (tmp_path / ".agent").mkdir()
        return tmp_path

    def test_acquire_and_release_lock(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        lock_path = StepExecutor._acquire_lock(project)
        assert lock_path is not None
        assert isinstance(lock_path, Path)
        StepExecutor._release_lock(lock_path)

    def test_lock_creates_file(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        lock_path = StepExecutor._acquire_lock(project)
        assert (project / ".agent" / ".gemstack.lock").exists()
        StepExecutor._release_lock(lock_path)

    def test_double_lock_raises(self, project: Path) -> None:
        from gemstack.orchestration.executor import StepExecutor

        lock_path = StepExecutor._acquire_lock(project)
        try:
            with pytest.raises(RuntimeError, match="already executing"):
                StepExecutor._acquire_lock(project)
        finally:
            StepExecutor._release_lock(lock_path)

    def test_release_none_is_noop(self) -> None:
        from gemstack.orchestration.executor import StepExecutor

        StepExecutor._release_lock(None)  # Should not raise
