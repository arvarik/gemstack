"""Tests for the teach command."""

from pathlib import Path

from gemstack.cli.teach_cmd import _LESSONS, _setup_sample_project


class TestTutorialLessons:
    def test_has_nine_lessons(self) -> None:
        assert len(_LESSONS) == 9

    def test_lessons_have_required_keys(self) -> None:
        for lesson in _LESSONS:
            assert "section" in lesson
            assert "title" in lesson
            assert "body" in lesson
            assert lesson["section"]
            assert lesson["title"]
            assert lesson["body"]

    def test_sections_are_ordered(self) -> None:
        sections = [lesson["section"] for lesson in _LESSONS]
        # Foundation comes first, then Lifecycle, then Power Tools
        assert sections[0] == "Foundation"
        assert sections[3] == "The 5-Step Lifecycle"
        assert sections[8] == "Power Tools"

    def test_lifecycle_steps_mention_gemstack_run(self) -> None:
        """Each lifecycle step should reference the correct CLI command."""
        for lesson in _LESSONS[3:8]:
            assert "gemstack run" in lesson["body"]

    def test_foundation_lessons_cover_key_concepts(self) -> None:
        """Foundation lessons should cover .agent/, config, and init."""
        bodies = " ".join(lesson["body"] for lesson in _LESSONS[:3])
        assert ".agent/" in bodies
        assert "ARCHITECTURE.md" in bodies
        assert "STATUS.md" in bodies
        assert "gemstack init" in bodies
        assert "gemstack config" in bodies
        assert "gemini-api-key" in bodies

    def test_power_tools_lesson_covers_essential_commands(self) -> None:
        """Power tools lesson should mention compile, route, diff, check."""
        body = _LESSONS[8]["body"]
        assert "gemstack compile" in body
        assert "gemstack route" in body
        assert "gemstack diff" in body
        assert "gemstack check" in body

    def test_step_titles_contain_step_numbers(self) -> None:
        for i, lesson in enumerate(_LESSONS[3:8], start=1):
            assert f"Step {i}" in lesson["title"]

    def test_no_slash_command_references(self) -> None:
        """Teach should use CLI commands, not slash commands like /step1-spec."""
        for lesson in _LESSONS:
            # Slash commands start with / at word boundary
            assert "/step1-spec" not in lesson["body"]
            assert "/step2-trap" not in lesson["body"]
            assert "/step3-build" not in lesson["body"]


class TestSampleProject:
    def test_creates_project_structure(self, tmp_path: Path) -> None:
        _setup_sample_project(tmp_path)

        assert (tmp_path / "src" / "main.py").exists()
        assert (tmp_path / "tests" / "test_main.py").exists()
        assert (tmp_path / "pyproject.toml").exists()

    def test_pyproject_has_dependencies(self, tmp_path: Path) -> None:
        _setup_sample_project(tmp_path)
        content = (tmp_path / "pyproject.toml").read_text()
        assert "fastapi" in content
