"""CLI integration tests for Phase 4 commands.

Uses typer.testing.CliRunner to test the actual CLI interface
(argument parsing, output, exit codes) for Phase 4 Ecosystem commands.
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from gemstack.cli.main import app

runner = CliRunner()


class TestCICommand:
    """Test gemstack ci github-actions / gitlab-ci."""

    def test_github_actions_creates_file(self, tmp_path: Path) -> None:
        output = tmp_path / "test.yml"
        result = runner.invoke(app, ["ci", "github-actions", "--output", str(output)])
        assert result.exit_code == 0
        assert output.exists()
        content = output.read_text()
        assert "gemstack check" in content
        assert "Gemstack Check" in content

    def test_gitlab_ci_creates_file(self, tmp_path: Path) -> None:
        output = tmp_path / "test.yml"
        result = runner.invoke(app, ["ci", "gitlab-ci", "--output", str(output)])
        assert result.exit_code == 0
        assert output.exists()
        content = output.read_text()
        assert "gemstack check" in content


class TestScaffoldCommand:
    """Test gemstack scaffold route/component/test."""

    def test_scaffold_python_route(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").touch()
        result = runner.invoke(app, ["scaffold", "route", "/api/v1/users", "-p", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "src" / "routes" / "api_v1_users.py").exists()
        assert (tmp_path / "tests" / "test_api_v1_users.py").exists()

    def test_scaffold_python_test(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").touch()
        result = runner.invoke(app, ["scaffold", "test", "auth", "-p", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "tests" / "test_auth.py").exists()

    def test_scaffold_unsupported_language(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["scaffold", "route", "/api/v1/foo", "-p", str(tmp_path)])
        assert result.exit_code == 1
        assert result.exception is not None
        assert "not yet supported" in str(result.exception)


class TestSnapshotCommand:
    """Test gemstack snapshot."""

    @pytest.fixture
    def project_with_agent(self, tmp_path: Path) -> Path:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n")
        (agent_dir / "STATUS.md").write_text("[STATE: IN_PROGRESS]\n")
        (agent_dir / "STYLE.md").write_text("# Style\n")
        (agent_dir / "TESTING.md").write_text("# Testing\n")
        (agent_dir / "PHILOSOPHY.md").write_text("# Philosophy\n")
        return tmp_path

    def test_snapshot_creates_file(self, project_with_agent: Path) -> None:
        output = project_with_agent / "snap.md"
        result = runner.invoke(
            app,
            ["snapshot", "-p", str(project_with_agent), "-o", str(output)],
        )
        assert result.exit_code == 0
        assert output.exists()
        content = output.read_text()
        assert "ARCHITECTURE.md" in content

    def test_snapshot_compact(self, project_with_agent: Path) -> None:
        output = project_with_agent / "snap.md"
        result = runner.invoke(
            app,
            ["snapshot", "-p", str(project_with_agent), "-o", str(output), "--compact"],
        )
        assert result.exit_code == 0
        assert output.exists()

    def test_snapshot_no_agent_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            ["snapshot", "-p", str(tmp_path), "-o", str(tmp_path / "snap.md")],
        )
        assert result.exit_code == 1


class TestMatrixCommand:
    """Test gemstack matrix."""

    def test_matrix_scan_finds_projects(self, tmp_path: Path) -> None:
        (tmp_path / "p1" / ".agent").mkdir(parents=True)
        (tmp_path / "p1" / ".agent" / "STATUS.md").write_text("[STATE: INITIALIZED]\n")
        (tmp_path / "p2" / ".agent").mkdir(parents=True)
        (tmp_path / "p2" / ".agent" / "STATUS.md").write_text("[STATE: IN_PROGRESS]\n")

        result = runner.invoke(app, ["matrix", "--scan", str(tmp_path)])
        assert result.exit_code == 0
        assert "p1" in result.stdout
        assert "p2" in result.stdout

    def test_matrix_json_output(self, tmp_path: Path) -> None:
        (tmp_path / "p1" / ".agent").mkdir(parents=True)
        (tmp_path / "p1" / ".agent" / "STATUS.md").write_text("[STATE: INITIALIZED]\n")

        result = runner.invoke(app, ["matrix", "--scan", str(tmp_path), "--json"])
        assert result.exit_code == 0
        # Parse with strict=False to handle emoji/unicode in console output
        data = json.loads(result.stdout, strict=False)
        assert isinstance(data, list)
        assert data[0]["name"] == "p1"

    def test_matrix_no_args(self) -> None:
        result = runner.invoke(app, ["matrix"])
        assert result.exit_code == 1

    def test_matrix_no_projects(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["matrix", "--scan", str(tmp_path)])
        assert result.exit_code == 1


class TestReplayCommand:
    """Test gemstack replay."""

    def test_replay_no_archive(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["replay", "--project", str(tmp_path)])
        assert result.exit_code == 1

    def test_replay_all_features(self, tmp_path: Path) -> None:
        archive = tmp_path / "docs" / "archive"
        feature = archive / "oauth"
        feature.mkdir(parents=True)
        (feature / "spec.md").write_text("# Spec\n")
        (feature / "plan.md").write_text("# Plan\n")

        result = runner.invoke(app, ["replay", "--all", "--project", str(tmp_path)])
        assert result.exit_code == 0
        assert "oauth" in result.stdout

    def test_replay_specific_feature(self, tmp_path: Path) -> None:
        archive = tmp_path / "docs" / "archive"
        feature = archive / "oauth"
        feature.mkdir(parents=True)
        (feature / "spec.md").write_text("# Spec\n")

        result = runner.invoke(app, ["replay", "oauth", "--project", str(tmp_path)])
        assert result.exit_code == 0
        assert "Spec" in result.stdout

    def test_replay_missing_feature(self, tmp_path: Path) -> None:
        archive = tmp_path / "docs" / "archive"
        archive.mkdir(parents=True)

        result = runner.invoke(app, ["replay", "nonexistent", "--project", str(tmp_path)])
        assert result.exit_code == 1


class TestTeachCommand:
    """Test gemstack teach."""

    def test_teach_invalid_step(self) -> None:
        result = runner.invoke(app, ["teach", "--step", "99"])
        assert result.exit_code == 1
        assert "between 1 and 5" in result.stdout


class TestPluginCheckIntegration:
    """Test that plugin-registered checks run during gemstack check."""

    def test_check_fires_plugin_checks(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        for f in ["ARCHITECTURE.md", "STYLE.md", "TESTING.md", "PHILOSOPHY.md", "STATUS.md"]:
            (agent_dir / f).write_text(f"# {f}\n\n[STATE: INITIALIZED]\nTopology\n")

        result = runner.invoke(app, ["check", str(tmp_path)])
        # Should pass — no plugin errors when no plugins are installed
        assert result.exit_code == 0
