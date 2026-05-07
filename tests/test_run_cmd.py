"""Tests for the gemstack run CLI command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from gemstack.cli.main import app

runner = CliRunner()


class TestRunCommand:
    """Tests for the `gemstack run` CLI command."""

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("# Status\n\n[STATE: INITIALIZED]\n")
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n")
        return tmp_path

    def test_dry_run_succeeds(self, project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "run",
                "step1-spec",
                "Test feature",
                "--project",
                str(project),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_unknown_step_fails(self, project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "run",
                "step99-invalid",
                "Test feature",
                "--project",
                str(project),
                "--dry-run",
            ],
        )
        assert result.exit_code == 1

    def test_missing_agent_dir_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "run",
                "step1-spec",
                "Test feature",
                "--project",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1
        assert result.exception is not None
        assert "gemstack init" in getattr(result.exception, "suggestion", "")

    def test_panel_shows_step_info(self, project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "run",
                "step1-spec",
                "My feature",
                "--project",
                str(project),
                "--dry-run",
            ],
        )
        assert "step1-spec" in result.output
        assert "My feature" in result.output

    def test_cli_args_passed_to_executor(self, project: Path) -> None:
        """Verify CLI arguments are correctly passed to StepExecutor."""
        with patch("gemstack.orchestration.executor.StepExecutor") as mock_executor_class:
            mock_executor = mock_executor_class.return_value
            # Mock the execute method to return a successful result
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.summary.return_value = "Mock success"
            mock_executor.execute = AsyncMock(return_value=mock_result)

            result = runner.invoke(
                app,
                [
                    "run",
                    "step1-spec",
                    "Test feature",
                    "--project",
                    str(project),
                    "--model",
                    "custom-model",
                    "--max-cost",
                    "50.0",
                    "--max-tokens",
                    "10000",
                ],
            )

            assert result.exit_code == 0
            mock_executor_class.assert_called_once_with(
                model="custom-model",
                max_cost=50.0,
                max_tokens=10000,
            )

    def test_default_cli_args_passed_to_executor(self, project: Path) -> None:
        """Verify default CLI arguments are correctly passed to StepExecutor."""
        with patch("gemstack.orchestration.executor.StepExecutor") as mock_executor_class:
            mock_executor = mock_executor_class.return_value
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.summary.return_value = "Mock success"
            mock_executor.execute = AsyncMock(return_value=mock_result)

            result = runner.invoke(
                app,
                [
                    "run",
                    "step1-spec",
                    "Test feature",
                    "--project",
                    str(project),
                ],
            )

            assert result.exit_code == 0
            mock_executor_class.assert_called_once_with(
                model="gemini-3.1-pro-preview",
                max_cost=None,
                max_tokens=None,
            )
