"""Tests for the matrix command."""

from pathlib import Path

from gemstack.cli.matrix_cmd import _discover_projects, _get_project_status


class TestProjectDiscovery:
    def test_discovers_gemstack_projects(self, tmp_path: Path) -> None:
        # Create two projects with .agent/
        p1 = tmp_path / "project1" / ".agent"
        p1.mkdir(parents=True)
        p2 = tmp_path / "project2" / ".agent"
        p2.mkdir(parents=True)
        # And one without
        (tmp_path / "not-gemstack").mkdir()

        projects = _discover_projects(tmp_path)
        assert len(projects) == 2
        names = [p.name for p in projects]
        assert "project1" in names
        assert "project2" in names

    def test_no_projects_found(self, tmp_path: Path) -> None:
        projects = _discover_projects(tmp_path)
        assert len(projects) == 0


class TestProjectStatus:
    def test_extracts_state(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "[STATE: IN_PROGRESS]\n\n## Current Focus\n\nOAuth feature\n"
        )

        status = _get_project_status(tmp_path)
        assert status["state"] == "IN_PROGRESS"
        assert status["feature"] == "OAuth feature"

    def test_missing_status_file(self, tmp_path: Path) -> None:
        status = _get_project_status(tmp_path)
        assert status["state"] == "UNKNOWN"
        assert status["health"] == "❌"

    def test_healthy_project(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: INITIALIZED]\n")

        status = _get_project_status(tmp_path)
        assert status["health"] == "✅"
