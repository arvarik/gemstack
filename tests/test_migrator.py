"""Tests for the topology migration module."""

from pathlib import Path

from gemstack.core.migrator import TopologyMigrator


class TestTopologyMigrator:
    """Tests for TopologyMigrator."""

    def _setup_agent_dir(self, tmp_path: Path) -> Path:
        """Create a minimal .agent/ directory for testing."""
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n\nProject details.\n")
        (agent_dir / "TESTING.md").write_text("# Testing Strategy\n\nTest details.\n")
        (agent_dir / "STATUS.md").write_text(
            "[STATE: INITIALIZED]\n\n## Current Focus\n\nSetup\n"
        )
        return agent_dir

    def test_adds_topology_to_architecture(self, tmp_path: Path) -> None:
        self._setup_agent_dir(tmp_path)

        migrator = TopologyMigrator()
        result = migrator.migrate(tmp_path, ["backend", "frontend"])

        assert "ARCHITECTURE.md" in result.files_modified
        content = (tmp_path / ".agent" / "ARCHITECTURE.md").read_text()
        assert "**Topology:** [backend, frontend]" in content

    def test_skips_existing_topology(self, tmp_path: Path) -> None:
        agent_dir = self._setup_agent_dir(tmp_path)
        # Pre-existing topology
        arch_content = (agent_dir / "ARCHITECTURE.md").read_text()
        arch_content = arch_content.replace(
            "# Architecture", "# Architecture\n\n**Topology:** [backend]"
        )
        (agent_dir / "ARCHITECTURE.md").write_text(arch_content)

        migrator = TopologyMigrator()
        result = migrator.migrate(tmp_path, ["backend"])

        assert "ARCHITECTURE.md already has a topology declaration" in result.warnings

    def test_adds_testing_matrix_backend(self, tmp_path: Path) -> None:
        self._setup_agent_dir(tmp_path)

        migrator = TopologyMigrator()
        result = migrator.migrate(tmp_path, ["backend"])

        assert "TESTING.md" in result.files_modified
        content = (tmp_path / ".agent" / "TESTING.md").read_text()
        assert "Backend Route Coverage" in content

    def test_adds_testing_matrix_frontend(self, tmp_path: Path) -> None:
        self._setup_agent_dir(tmp_path)

        migrator = TopologyMigrator()
        migrator.migrate(tmp_path, ["frontend"])

        content = (tmp_path / ".agent" / "TESTING.md").read_text()
        assert "Frontend Component State Matrix" in content

    def test_adds_status_tracker(self, tmp_path: Path) -> None:
        self._setup_agent_dir(tmp_path)

        migrator = TopologyMigrator()
        result = migrator.migrate(tmp_path, ["backend"])

        assert "STATUS.md" in result.files_modified
        content = (tmp_path / ".agent" / "STATUS.md").read_text()
        assert "Stub Audit Tracker" in content

    def test_adds_ml_ai_tracker(self, tmp_path: Path) -> None:
        self._setup_agent_dir(tmp_path)

        migrator = TopologyMigrator()
        migrator.migrate(tmp_path, ["ml-ai"])

        content = (tmp_path / ".agent" / "STATUS.md").read_text()
        assert "Prompt Versioning Changelog" in content

    def test_no_agent_dir(self, tmp_path: Path) -> None:
        migrator = TopologyMigrator()
        result = migrator.migrate(tmp_path, ["backend"])

        assert not result.files_modified
        assert "No .agent/ directory found" in result.warnings

    def test_idempotent(self, tmp_path: Path) -> None:
        """Running migrate twice should not duplicate sections."""
        self._setup_agent_dir(tmp_path)
        migrator = TopologyMigrator()

        migrator.migrate(tmp_path, ["backend"])
        migrator.migrate(tmp_path, ["backend"])

        # Second run should not modify TESTING.md or STATUS.md
        # (only ARCHITECTURE.md will warn about existing topology)
        content = (tmp_path / ".agent" / "TESTING.md").read_text()
        assert content.count("Backend Route Coverage") == 1
