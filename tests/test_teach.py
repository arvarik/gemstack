"""Tests for the teach command."""

from pathlib import Path

from gemstack.cli.teach_cmd import _STEPS, _setup_sample_project


class TestTutorialSteps:
    def test_has_five_steps(self) -> None:
        assert len(_STEPS) == 5

    def test_steps_have_title_and_body(self) -> None:
        for step in _STEPS:
            assert "title" in step
            assert "body" in step
            assert step["title"]
            assert step["body"]

    def test_step_titles_are_ordered(self) -> None:
        for i, step in enumerate(_STEPS, start=1):
            assert f"Step {i}" in step["title"]


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
