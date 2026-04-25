"""Integration tests for CLI commands via CliRunner."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from gemstack.cli.main import app

runner = CliRunner()


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "gemstack" in result.stdout

    def test_help_flag(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "gemstack" in result.stdout.lower()

    def test_no_args_shows_help(self) -> None:
        result = runner.invoke(app, [])
        # Typer's no_args_is_help uses exit code 0 or 2 depending on version
        assert result.exit_code in (0, 2)


class TestDoctorCommand:
    """Test the doctor command."""

    def test_doctor_runs_without_crash(self) -> None:
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code in (0, 1)
        if result.exit_code == 0:
            assert "Python" in result.stdout
        else:
            assert result.exception is not None
            assert "diagnostic checks failed" in str(result.exception)


class TestCheckCommand:
    """Test the check command."""

    def test_check_fails_without_agent_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["check", str(tmp_path)])
        assert result.exit_code == 1

    def test_check_passes_bootstrapped_project(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["check", str(bootstrapped_project)])
        assert result.exit_code == 0


class TestInitCommand:
    """Test the init command."""

    def test_init_creates_agent_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path), "--no-ai"])
        assert result.exit_code == 0
        assert (tmp_path / ".agent").exists()
        assert (tmp_path / ".agent" / "ARCHITECTURE.md").exists()
        assert (tmp_path / ".agent" / "STATUS.md").exists()

    def test_init_skips_existing(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["init", str(bootstrapped_project)], input="n\n")
        assert result.exit_code == 0
        assert "already exists" in result.stdout

    def test_init_force_existing(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["init", str(bootstrapped_project), "--no-ai", "--force"])
        assert result.exit_code == 0
        assert "Analyzing project" in result.stdout

    def test_init_creates_docs_dirs(self, tmp_path: Path) -> None:
        runner.invoke(app, ["init", str(tmp_path), "--no-ai"])
        assert (tmp_path / "docs" / "explorations").exists()
        assert (tmp_path / "docs" / "designs").exists()
        assert (tmp_path / "docs" / "plans").exists()
        assert (tmp_path / "docs" / "archive").exists()

    def test_init_detects_python_project(self, python_fastapi: Path) -> None:
        result = runner.invoke(app, ["init", str(python_fastapi), "--no-ai"])
        assert result.exit_code == 0
        # Should detect FastAPI
        arch = (python_fastapi / ".agent" / "ARCHITECTURE.md").read_text()
        assert "python" in arch.lower() or "fastapi" in arch.lower()


class TestStatusCommand:
    """Test the status command."""

    def test_status_fails_without_agent(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["status", str(tmp_path)])
        assert result.exit_code == 1

    def test_status_reads_bootstrapped(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["status", str(bootstrapped_project)])
        assert result.exit_code == 0

    def test_status_json_output(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["status", str(bootstrapped_project), "--json"])
        assert result.exit_code == 0
        assert "READY_FOR_BUILD" in result.stdout


class TestCompileCommand:
    """Test the compile command — Phase 2 core."""

    def test_compile_produces_output(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(
            app, ["compile", "step1-spec", "--project", str(bootstrapped_project)]
        )
        assert result.exit_code == 0
        assert len(result.stdout) > 100

    def test_compile_includes_sections(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(
            app, ["compile", "step3-build", "--project", str(bootstrapped_project)]
        )
        assert result.exit_code == 0
        assert "Role:" in result.stdout or "Phase:" in result.stdout

    def test_compile_to_file(self, bootstrapped_project: Path, tmp_path: Path) -> None:
        output_file = tmp_path / "compiled.md"
        result = runner.invoke(
            app,
            [
                "compile",
                "step1-spec",
                "--project",
                str(bootstrapped_project),
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert len(output_file.read_text()) > 100

    def test_compile_invalid_step(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(
            app, ["compile", "step99-fake", "--project", str(bootstrapped_project)]
        )
        assert result.exit_code == 1


class TestRouteCommand:
    """Test the route command — Phase 2 core."""

    def test_route_on_bootstrapped(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["route", str(bootstrapped_project)])
        assert result.exit_code == 0
        # Bootstrapped fixture has [STATE: READY_FOR_BUILD]
        assert "step3-build" in result.stdout or "CONTINUE" in result.stdout

    def test_route_json(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["route", str(bootstrapped_project), "--json"])
        assert result.exit_code == 0
        assert "action" in result.stdout
        assert "next_command" in result.stdout

    def test_route_no_agent_blocked(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["route", str(tmp_path)])
        assert result.exit_code == 1  # Blocked exits with 1


class TestStartCommand:
    """Test the start command — Phase 2 feature lifecycle."""

    def test_start_updates_status(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(
            app, ["start", "Add Google OAuth", "--project", str(bootstrapped_project)]
        )
        assert result.exit_code == 0
        assert "Google OAuth" in result.stdout

        # Verify STATUS.md was updated
        status = (bootstrapped_project / ".agent" / "STATUS.md").read_text()
        assert "IN_PROGRESS" in status
        assert "Google OAuth" in status

    def test_start_no_agent_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["start", "Feature", "--project", str(tmp_path)])
        assert result.exit_code == 1


class TestPhaseCommand:
    """Test the phase command — Phase 2."""

    def test_phase_build(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["phase", "build", "--project", str(bootstrapped_project)])
        assert result.exit_code == 0
        assert "build" in result.stdout.lower()

        status = (bootstrapped_project / ".agent" / "STATUS.md").read_text()
        assert "READY_FOR_BUILD" in status

    def test_phase_invalid(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(app, ["phase", "explode", "--project", str(bootstrapped_project)])
        assert result.exit_code == 1


class TestConfigCommand:
    """Test the config command — Phase 2."""

    def test_config_list(self) -> None:
        result = runner.invoke(app, ["config", "list"])
        assert result.exit_code == 0
        assert "gemini-api-key" in result.stdout

    def test_config_set_and_get(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from gemstack.project.config import GemstackConfig

        config_path = tmp_path / "config.toml"
        monkeypatch.setattr(GemstackConfig, "config_path", classmethod(lambda cls: config_path))

        result = runner.invoke(app, ["config", "set", "default-model", "gemini-2.5-pro"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["config", "get", "default-model"])
        assert result.exit_code == 0
        assert "gemini-2.5-pro" in result.stdout

    def test_config_invalid_key(self) -> None:
        result = runner.invoke(app, ["config", "set", "invalid-key", "value"])
        assert result.exit_code == 1


class TestExportCommand:
    """Test the export command — Phase 2."""

    def test_export_cursor(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "export",
                "--format",
                "cursor",
                "--project",
                str(bootstrapped_project),
            ],
        )
        assert result.exit_code == 0
        assert (bootstrapped_project / ".cursorrules").exists()

    def test_export_claude(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "export",
                "--format",
                "claude",
                "--project",
                str(bootstrapped_project),
            ],
        )
        assert result.exit_code == 0
        assert (bootstrapped_project / "CLAUDE.md").exists()

    def test_export_invalid_format(self, bootstrapped_project: Path) -> None:
        result = runner.invoke(
            app,
            [
                "export",
                "--format",
                "vscode",
                "--project",
                str(bootstrapped_project),
            ],
        )
        assert result.exit_code == 1
