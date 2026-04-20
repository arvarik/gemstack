"""Tests for the ContextCompiler module."""

from pathlib import Path

import pytest

from gemstack.orchestration.compiler import CompiledContext, ContextCompiler


class TestCompilePipeline:
    """Test the full compilation pipeline."""

    def test_compile_returns_compiled_context(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step1-spec", bootstrapped_project)

        assert isinstance(result, CompiledContext)
        assert result.total_content != ""
        assert result.token_estimate > 0
        assert len(result.sections) > 0
        assert len(result.sources) > 0

    def test_compile_includes_workflow_goal(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step1-spec", bootstrapped_project)

        assert any("Workflow Goal" in name for name, _ in result.sections)

    def test_compile_includes_agent_files(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step1-spec", bootstrapped_project)

        source_names = [name for name, _ in result.sections]
        assert "ARCHITECTURE.md" in source_names
        assert "STATUS.md" in source_names

    def test_compile_step3_includes_roles(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step3-build", bootstrapped_project)

        source_names = [name for name, _ in result.sections]
        # step3-build composites Principal Backend Engineer, Principal Frontend Engineer
        assert any("Role:" in name for name in source_names)

    def test_compile_step3_includes_phases(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step3-build", bootstrapped_project)

        source_names = [name for name, _ in result.sections]
        assert any("Phase:" in name for name in source_names)

    def test_compile_detects_topologies(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step1-spec", bootstrapped_project)

        source_names = [name for name, _ in result.sections]
        # The bootstrapped fixture has topology [frontend, backend]
        assert any("Topology:" in name for name in source_names)


class TestWorkflowParsing:
    """Test workflow step parsing."""

    def test_parse_step1(self) -> None:
        compiler = ContextCompiler()
        meta = compiler._parse_workflow_step("step1-spec")

        assert meta.name == "step1-spec"
        assert "Product Visionary" in meta.roles
        assert "Architect" in meta.roles
        assert len(meta.phases) > 0

    def test_parse_step3(self) -> None:
        compiler = ContextCompiler()
        meta = compiler._parse_workflow_step("step3-build")

        assert "Principal Backend Engineer" in meta.roles
        assert "Build" in meta.phases

    def test_parse_all_steps(self) -> None:
        compiler = ContextCompiler()
        for step in ["step1-spec", "step2-trap", "step3-build", "step4-audit", "step5-ship"]:
            meta = compiler._parse_workflow_step(step)
            assert meta.name == step
            assert len(meta.roles) > 0
            assert len(meta.phases) > 0

    def test_invalid_step_raises_error(self) -> None:
        compiler = ContextCompiler()
        with pytest.raises(FileNotFoundError):
            compiler._parse_workflow_step("step99-invalid")


class TestTokenBudget:
    """Test token estimation and truncation."""

    def test_token_estimate_is_reasonable(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step1-spec", bootstrapped_project)

        # Token estimate should be roughly content_length / 4
        expected = len(result.total_content) // 4
        assert abs(result.token_estimate - expected) < 100

    def test_truncation_respects_budget(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step1-spec", bootstrapped_project, max_tokens=500)

        assert result.truncated is True
        assert result.token_estimate <= 500

    def test_no_truncation_without_budget(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step1-spec", bootstrapped_project)

        assert result.truncated is False


class TestNoSource:
    """Test compilation without source files."""

    def test_no_source_excludes_source_sections(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        result = compiler.compile("step1-spec", bootstrapped_project, include_source=False)

        source_names = [name for name, _ in result.sections]
        assert not any(name.startswith("Source:") for name in source_names)


class TestTopologyDetection:
    """Test topology extraction from ARCHITECTURE.md."""

    def test_detects_frontend_backend(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        topologies = compiler._detect_project_topologies(bootstrapped_project)

        assert "frontend" in topologies
        assert "backend" in topologies

    def test_ignores_tbd(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("**Topology:** [TBD]")

        compiler = ContextCompiler()
        topologies = compiler._detect_project_topologies(tmp_path)

        assert topologies == []

    def test_no_architecture_returns_empty(self, tmp_path: Path) -> None:
        compiler = ContextCompiler()
        topologies = compiler._detect_project_topologies(tmp_path)
        assert topologies == []


class TestRelevantFiles:
    """Test extraction of relevant files from STATUS.md."""

    def test_extracts_file_paths(self, bootstrapped_project: Path) -> None:
        compiler = ContextCompiler()
        files = compiler._extract_relevant_files(bootstrapped_project / ".agent" / "STATUS.md")

        assert "src/app/api/auth/route.ts" in files
        assert "src/components/LoginButton.tsx" in files

    def test_no_status_returns_empty(self, tmp_path: Path) -> None:
        compiler = ContextCompiler()
        files = compiler._extract_relevant_files(tmp_path / "nonexistent.md")
        assert files == []
