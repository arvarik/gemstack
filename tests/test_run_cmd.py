"""Tests for the gemstack run CLI command."""

from __future__ import annotations

from pathlib import Path

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
        (agent_dir / "STATUS.md").write_text(
            "# Status\n\n[STATE: INITIALIZED]\n"
        )
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n")
        return tmp_path

    def test_dry_run_succeeds(self, project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "run", "step1-spec", "Test feature",
                "--project", str(project),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_unknown_step_fails(self, project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "run", "step99-invalid", "Test feature",
                "--project", str(project),
                "--dry-run",
            ],
        )
        assert result.exit_code == 1

    def test_missing_agent_dir_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "run", "step1-spec", "Test feature",
                "--project", str(tmp_path),
            ],
        )
        assert result.exit_code == 1
        assert "gemstack init" in result.output

    def test_panel_shows_step_info(self, project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "run", "step1-spec", "My feature",
                "--project", str(project),
                "--dry-run",
            ],
        )
        assert "step1-spec" in result.output
        assert "My feature" in result.output
