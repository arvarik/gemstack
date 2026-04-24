"""Tests for the context drift detection module."""

from pathlib import Path

from gemstack.utils.differ import ContextDiffer, DriftReport


class TestDriftReport:
    """Tests for the DriftReport dataclass."""

    def test_no_drift(self) -> None:
        report = DriftReport()
        assert not report.has_drift
        assert "No drift detected" in report.to_markdown()

    def test_has_drift_with_new_deps(self) -> None:
        report = DriftReport(new_dependencies=["express"])
        assert report.has_drift
        md = report.to_markdown()
        assert "New Dependencies" in md
        assert "`express`" in md

    def test_has_drift_with_stale_refs(self) -> None:
        report = DriftReport(stale_file_refs=["src/old.py"])
        assert report.has_drift
        assert "Stale File References" in report.to_markdown()

    def test_has_drift_with_env_vars(self) -> None:
        report = DriftReport(new_env_vars=["NEW_API_KEY"])
        assert report.has_drift
        assert "New Environment Variables" in report.to_markdown()


class TestContextDiffer:
    """Tests for the ContextDiffer analyzer."""

    def test_analyze_no_agent_dir(self, tmp_path: Path) -> None:
        differ = ContextDiffer()
        report = differ.analyze(tmp_path)
        assert not report.has_drift

    def test_analyze_empty_project(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n")
        (agent_dir / "STATUS.md").write_text("[STATE: INITIALIZED]\n")

        differ = ContextDiffer()
        report = differ.analyze(tmp_path)
        assert not report.has_drift

    def test_detects_stale_file_refs(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n")
        (agent_dir / "STATUS.md").write_text(
            "## Relevant Files\n\n- `src/missing.py`\n- `src/existing.py`\n"
        )
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "existing.py").touch()

        differ = ContextDiffer()
        report = differ.analyze(tmp_path)
        assert "src/missing.py" in report.stale_file_refs
        assert "src/existing.py" not in report.stale_file_refs

    def test_detects_env_drift(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text(
            "# Architecture\n\n## Configuration\n\n`DATABASE_URL` is required.\n"
        )
        (tmp_path / ".env.example").write_text("DATABASE_URL=postgres://...\nNEW_SECRET=abc\n")

        differ = ContextDiffer()
        report = differ.analyze(tmp_path)
        assert "NEW_SECRET" in report.new_env_vars

    def test_architecture_only_flag(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n")
        (tmp_path / ".env.example").write_text("NEW_VAR=abc\n")
        (agent_dir / "STATUS.md").write_text("## Relevant Files\n\n- `missing.py`\n")

        differ = ContextDiffer()
        report = differ.analyze(tmp_path, architecture_only=True)
        # Env and stale refs should NOT be checked
        assert not report.new_env_vars
        assert not report.stale_file_refs

    def test_env_only_flag(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n")
        (tmp_path / ".env.example").write_text("NEW_VAR=abc\n")

        differ = ContextDiffer()
        report = differ.analyze(tmp_path, env_only=True)
        assert "NEW_VAR" in report.new_env_vars


class TestDependencyExtraction:
    """Tests for dependency extraction from manifest files."""

    def test_extracts_node_deps(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text(
            "# Architecture\n\n## Tech Stack\n\n| `react` |\n"
        )
        (tmp_path / "package.json").write_text(
            '{"dependencies": {"react": "^18", "express": "^4"}, '
            '"devDependencies": {"vitest": "^1"}}'
        )

        differ = ContextDiffer()
        report = differ.analyze(tmp_path)
        # express and vitest are not in ARCHITECTURE.md
        assert "express" in report.new_dependencies
        assert "vitest" in report.new_dependencies

    def test_extracts_python_deps(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text(
            "# Arch\n\n## Tech Stack\n\n| `fastapi` |\n"
        )
        (tmp_path / "pyproject.toml").write_text(
            '[project]\ndependencies = ["fastapi>=0.100", "uvicorn>=0.20"]\n'
        )

        differ = ContextDiffer()
        report = differ.analyze(tmp_path)
        assert "uvicorn" in report.new_dependencies
        assert "fastapi" not in report.new_dependencies
