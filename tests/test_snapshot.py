"""Tests for the snapshot command."""

from pathlib import Path

from gemstack.cli.snapshot_cmd import _snapshot_full


class TestSnapshotFull:
    def _setup_agent(self, tmp_path: Path) -> Path:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n\nProject arch.\n")
        (agent_dir / "STATUS.md").write_text("[STATE: IN_PROGRESS]\n\n## Current Focus\n\nOAuth\n")
        (agent_dir / "STYLE.md").write_text("# Style\n")
        (agent_dir / "TESTING.md").write_text("# Testing\n")
        (agent_dir / "PHILOSOPHY.md").write_text("# Philosophy\n")
        return agent_dir

    def test_includes_all_agent_files(self, tmp_path: Path) -> None:
        agent_dir = self._setup_agent(tmp_path)
        parts: list[str] = []
        _snapshot_full(parts, agent_dir, tmp_path, compact=False)

        content = "\n".join(parts)
        assert "ARCHITECTURE.md" in content
        assert "STATUS.md" in content
        assert "STYLE.md" in content
        assert "TESTING.md" in content
        assert "PHILOSOPHY.md" in content

    def test_compact_truncates(self, tmp_path: Path) -> None:
        agent_dir = self._setup_agent(tmp_path)
        # Write a long file
        (agent_dir / "ARCHITECTURE.md").write_text("x" * 5000)

        parts: list[str] = []
        _snapshot_full(parts, agent_dir, tmp_path, compact=True)

        content = "\n".join(parts)
        assert "truncated for compact mode" in content

    def test_includes_relevant_sources(self, tmp_path: Path) -> None:
        agent_dir = self._setup_agent(tmp_path)
        (agent_dir / "STATUS.md").write_text(
            "[STATE: IN_PROGRESS]\n\n## Relevant Files\n\n- `src/main.py`\n"
        )
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('hello')")

        parts: list[str] = []
        _snapshot_full(parts, agent_dir, tmp_path, compact=False)

        content = "\n".join(parts)
        assert "src/main.py" in content
        assert "print('hello')" in content
