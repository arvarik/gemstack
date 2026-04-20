"""Tests for the Jinja2 template system."""

from pathlib import Path

from gemstack.project.detector import ProjectProfile, Topology
from gemstack.project.templates import create_template_env, render_agent_files


class TestCustomDelimiters:
    """Test that custom delimiters work and don't conflict with markdown."""

    def test_env_uses_custom_delimiters(self) -> None:
        env = create_template_env()

        assert env.variable_start_string == "{="
        assert env.variable_end_string == "=}"
        assert env.block_start_string == "{%%"
        assert env.block_end_string == "%%}"

    def test_standard_mustache_passes_through(self, tmp_path: Path) -> None:
        """Ensure {{ }} in templates are treated as literal text."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "test.md.j2").write_text(
            "Go template: {{ .Name }}\nGemstack var: {= name =}\n"
        )

        env = create_template_env(template_dir)
        template = env.get_template("test.md.j2")
        result = template.render(name="MyProject")

        assert "{{ .Name }}" in result  # Go template preserved
        assert "MyProject" in result  # Gemstack var rendered


class TestTemplateRendering:
    """Test rendering all 5 .agent/ templates."""

    def _make_profile(self, topologies: list[str] | None = None) -> ProjectProfile:
        """Create a test profile."""
        topos = [Topology(t) for t in (topologies or ["backend"])]
        return ProjectProfile(
            name="test-project",
            root=Path("/var/tmp/test"),  # noqa: S108
            topologies=topos,
            language="python",
            runtime="cpython",
            framework="fastapi",
            package_manager="uv",
            dev_command="uv run uvicorn app:app --reload",
            test_command="uv run pytest",
            build_command="uv build",
            lint_command="uv run ruff check .",
            has_tests=True,
            has_database=True,
        )

    def test_renders_all_five_files(self, tmp_path: Path) -> None:
        profile = self._make_profile()
        agent_dir = tmp_path / ".agent"

        created = render_agent_files(profile, agent_dir)

        assert len(created) == 5
        assert "ARCHITECTURE.md" in created
        assert "STYLE.md" in created
        assert "TESTING.md" in created
        assert "PHILOSOPHY.md" in created
        assert "STATUS.md" in created

    def test_architecture_contains_topology(self, tmp_path: Path) -> None:
        profile = self._make_profile(["backend", "ml-ai"])
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "ARCHITECTURE.md").read_text()

        assert "backend" in content
        assert "ml-ai" in content
        assert "Model Ledger" in content  # ML/AI conditional section

    def test_architecture_no_mlai_section(self, tmp_path: Path) -> None:
        profile = self._make_profile(["backend"])
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "ARCHITECTURE.md").read_text()

        assert "Model Ledger" not in content

    def test_style_uses_python_conventions(self, tmp_path: Path) -> None:
        profile = self._make_profile()
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "STYLE.md").read_text()

        assert "snake_case" in content
        assert "PascalCase" in content

    def test_testing_has_backend_matrix(self, tmp_path: Path) -> None:
        profile = self._make_profile(["backend"])
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "TESTING.md").read_text()

        assert "Backend Route Coverage" in content

    def test_testing_has_frontend_matrix(self, tmp_path: Path) -> None:
        profile = self._make_profile(["frontend"])
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "TESTING.md").read_text()

        assert "Frontend Component State" in content

    def test_testing_no_frontend_matrix_for_backend(self, tmp_path: Path) -> None:
        profile = self._make_profile(["backend"])
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "TESTING.md").read_text()

        assert "Frontend Component State" not in content

    def test_status_has_stub_tracker_for_fullstack(self, tmp_path: Path) -> None:
        profile = self._make_profile(["frontend", "backend"])
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "STATUS.md").read_text()

        assert "Stub Audit Tracker" in content

    def test_status_has_prompt_tracker_for_mlai(self, tmp_path: Path) -> None:
        profile = self._make_profile(["ml-ai"])
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "STATUS.md").read_text()

        assert "Prompt Versioning" in content

    def test_status_initialized_state(self, tmp_path: Path) -> None:
        profile = self._make_profile()
        agent_dir = tmp_path / ".agent"

        render_agent_files(profile, agent_dir)
        content = (agent_dir / "STATUS.md").read_text()

        assert "[STATE: INITIALIZED]" in content

    def test_creates_agent_dir_if_missing(self, tmp_path: Path) -> None:
        profile = self._make_profile()
        agent_dir = tmp_path / "deep" / "nested" / ".agent"

        render_agent_files(profile, agent_dir)

        assert agent_dir.exists()
        assert (agent_dir / "ARCHITECTURE.md").exists()


class TestLanguageVariants:
    """Test template rendering for different languages."""

    def test_go_style(self, tmp_path: Path) -> None:
        profile = ProjectProfile(
            name="go-app",
            root=Path("/var/tmp/go-app"),  # noqa: S108
            topologies=[Topology.BACKEND],
            language="go",
        )
        agent_dir = tmp_path / ".agent"
        render_agent_files(profile, agent_dir)
        content = (agent_dir / "STYLE.md").read_text()

        assert "PascalCase" in content
        assert "godoc" in content

    def test_typescript_style(self, tmp_path: Path) -> None:
        profile = ProjectProfile(
            name="ts-app",
            root=Path("/var/tmp/ts-app"),  # noqa: S108
            topologies=[Topology.FRONTEND],
            language="typescript",
        )
        agent_dir = tmp_path / ".agent"
        render_agent_files(profile, agent_dir)
        content = (agent_dir / "STYLE.md").read_text()

        assert "camelCase" in content

    def test_testing_npm_commands(self, tmp_path: Path) -> None:
        profile = ProjectProfile(
            name="ts-app",
            root=Path("/var/tmp/ts-app"),  # noqa: S108
            topologies=[Topology.FRONTEND],
            language="typescript",
            package_manager="npm",
            test_command="npm test",
        )
        agent_dir = tmp_path / ".agent"
        render_agent_files(profile, agent_dir)
        content = (agent_dir / "TESTING.md").read_text()

        assert "npm install" in content
