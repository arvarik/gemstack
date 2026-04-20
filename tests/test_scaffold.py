"""Tests for the scaffold command."""

from pathlib import Path

from gemstack.project.scaffolder import Scaffolder


class TestLanguageDetection:
    def test_detects_python(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").touch()
        assert Scaffolder(tmp_path)._detect_language() == "python"

    def test_detects_go(self, tmp_path: Path) -> None:
        (tmp_path / "go.mod").touch()
        assert Scaffolder(tmp_path)._detect_language() == "go"

    def test_detects_typescript(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").touch()
        (tmp_path / "tsconfig.json").touch()
        assert Scaffolder(tmp_path)._detect_language() == "typescript"

    def test_detects_javascript(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").touch()
        assert Scaffolder(tmp_path)._detect_language() == "javascript"

    def test_unknown_project(self, tmp_path: Path) -> None:
        assert Scaffolder(tmp_path)._detect_language() == "unknown"


class TestPythonScaffolding:
    def test_scaffold_route_creates_files(self, tmp_path: Path) -> None:
        Scaffolder(tmp_path)._scaffold_python_route("/api/v1/notifications")

        route_file = tmp_path / "src" / "routes" / "api_v1_notifications.py"
        assert route_file.exists()
        content = route_file.read_text()
        assert "handle_api_v1_notifications" in content

        test_file = tmp_path / "tests" / "test_api_v1_notifications.py"
        assert test_file.exists()

    def test_scaffold_test_creates_file(self, tmp_path: Path) -> None:
        Scaffolder(tmp_path)._scaffold_python_test("notifications")

        test_file = tmp_path / "tests" / "test_notifications.py"
        assert test_file.exists()
        content = test_file.read_text()
        assert "class TestNotifications" in content
        assert "import pytest" in content
