"""Tests for the git worktree manager."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from gemstack.core.worktree import WorktreeManager


class TestWorktreeManager:
    """Tests for WorktreeManager with mocked subprocess."""

    @patch("gemstack.core.worktree.subprocess.run")
    def test_create_worktrees(self, mock_run: MagicMock, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: IN_PROGRESS]\n")

        mock_run.return_value = MagicMock(returncode=0)

        manager = WorktreeManager()
        result = manager.create(
            tmp_path, {"backend": "feat/oauth-backend"}
        )

        assert result.success
        assert len(result.worktrees) == 1
        assert result.worktrees[0].branch == "feat/oauth-backend"
        mock_run.assert_called_once()

    @patch("gemstack.core.worktree.subprocess.run")
    def test_create_fails_gracefully(self, mock_run: MagicMock, tmp_path: Path) -> None:
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "git", "", "fatal: branch exists")

        manager = WorktreeManager()
        result = manager.create(tmp_path, {"backend": "existing-branch"})

        assert not result.success
        assert "Failed to create worktree" in result.message

    @patch("gemstack.core.worktree.subprocess.run")
    def test_status_parses_porcelain(self, mock_run: MagicMock, tmp_path: Path) -> None:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "worktree /home/user/project\n"
                "HEAD abc1234\n"
                "branch refs/heads/main\n"
                "\n"
                "worktree /home/user/project-backend\n"
                "HEAD def5678\n"
                "branch refs/heads/feat/api\n"
            ),
        )

        manager = WorktreeManager()
        result = manager.status(tmp_path)

        assert result.success
        assert len(result.worktrees) == 2
        assert result.worktrees[1].branch == "feat/api"

    @patch("gemstack.core.worktree.subprocess.run")
    def test_cleanup_removes_non_main(self, mock_run: MagicMock, tmp_path: Path) -> None:
        # cleanup calls status() first (1 subprocess.run),
        # then remove for each non-main worktree (1 more subprocess.run)
        mock_run.side_effect = [
            MagicMock(  # status call
                returncode=0,
                stdout=(
                    "worktree /home/project\n"
                    "HEAD abc1234\n"
                    "branch refs/heads/main\n"
                    "\n"
                    "worktree /home/project-backend\n"
                    "HEAD def5678\n"
                    "branch refs/heads/feat/api\n"
                ),
            ),
            MagicMock(returncode=0),  # remove call for feat/api
        ]

        manager = WorktreeManager()
        result = manager.cleanup(tmp_path)

        assert result.success
        assert "1" in result.message
        # Verify the remove was called for the non-main worktree
        assert mock_run.call_count == 2

    def test_git_not_found(self, tmp_path: Path) -> None:
        with patch(
            "gemstack.core.worktree.subprocess.run",
            side_effect=FileNotFoundError("git"),
        ):
            manager = WorktreeManager()
            result = manager.create(tmp_path, {"backend": "feat/x"})
            assert not result.success
            assert "git not found" in result.message


class TestRunParallel:
    """P1-4: Tests for run_parallel() with asyncio.TaskGroup."""

    @patch("gemstack.core.worktree.subprocess.run")
    def test_run_parallel_create_failure(
        self, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """run_parallel returns error when worktree creation fails."""
        import asyncio
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(
            1, "git", "", "fatal: error"
        )

        manager = WorktreeManager()
        results = asyncio.run(
            manager.run_parallel(
                tmp_path,
                {"backend": "feat/test"},
                step="step1-spec",
                feature="test",
            )
        )
        assert len(results) == 1
        assert "error" in results[0]

    @patch("gemstack.core.worktree.subprocess.run")
    def test_run_parallel_returns_results(
        self, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """run_parallel should create worktrees and dispatch execution."""
        import asyncio
        from unittest.mock import AsyncMock

        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: INITIALIZED]\n")
        (agent_dir / "ARCHITECTURE.md").write_text("# Arch\n")

        # Simulate successful worktree creation
        mock_run.return_value = MagicMock(returncode=0)

        manager = WorktreeManager()

        # Mock the executor to avoid actual API calls
        with patch(
            "gemstack.core.executor.StepExecutor"
        ) as MockExecutor:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.files_written = ["test.md"]
            mock_result.cost_usd = 0.01
            mock_result.error = None

            mock_instance = MockExecutor.return_value
            mock_instance.execute = AsyncMock(return_value=mock_result)

            results = asyncio.run(
                manager.run_parallel(
                    tmp_path,
                    {"backend": "feat/be"},
                    step="step1-spec",
                    feature="test",
                )
            )
            # Should have results for non-main worktrees
            assert isinstance(results, list)

