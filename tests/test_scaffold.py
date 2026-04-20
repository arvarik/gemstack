"""Tests for the scaffold command."""

from pathlib import Path

from gemstack.cli.scaffold_cmd import (
    _detect_language,
    _scaffold_python_route,
    _scaffold_python_test,
)


class TestLanguageDetection:
    def test_detects_python(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").touch()
        assert _detect_language(tmp_path) == "python"

    def test_detects_go(self, tmp_path: Path) -> None:
        (tmp_path / "go.mod").touch()
        assert _detect_language(tmp_path) == "go"

    def test_detects_typescript(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").touch()
        (tmp_path / "tsconfig.json").touch()
        assert _detect_language(tmp_path) == "typescript"

    def test_detects_javascript(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").touch()
        assert _detect_language(tmp_path) == "javascript"

    def test_unknown_project(self, tmp_path: Path) -> None:
        assert _detect_language(tmp_path) == "unknown"


class TestPythonScaffolding:
    def test_scaffold_route_creates_files(self, tmp_path: Path) -> None:
        _scaffold_python_route(tmp_path, "/api/v1/notifications")

        route_file = tmp_path / "src" / "routes" / "api_v1_notifications.py"
        assert route_file.exists()
        content = route_file.read_text()
        assert "handle_api_v1_notifications" in content

        test_file = tmp_path / "tests" / "test_api_v1_notifications.py"
        assert test_file.exists()

    def test_scaffold_test_creates_file(self, tmp_path: Path) -> None:
        _scaffold_python_test(tmp_path, "notifications")

        test_file = tmp_path / "tests" / "test_notifications.py"
        assert test_file.exists()
        content = test_file.read_text()
        assert "class TestNotifications" in content
        assert "import pytest" in content
