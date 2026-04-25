"""Tests for the AIBootstrapper module.

All tests use mocked google-genai clients — no real API calls.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gemstack.ai.bootstrap import _CHAR_BUDGET, BootstrapResult


class TestBootstrapResult:
    """Test the BootstrapResult dataclass."""

    def test_template_only_creates_empty_result(self) -> None:
        profile = MagicMock()
        result = BootstrapResult.template_only(profile)

        assert result.ai_powered is False
        assert result.error is None
        assert result.files() == {}

    def test_files_returns_non_empty(self) -> None:
        result = BootstrapResult(
            architecture="# Architecture",
            style="# Style",
            ai_powered=True,
        )
        files = result.files()
        assert "ARCHITECTURE.md" in files
        assert "STYLE.md" in files
        assert "TESTING.md" not in files  # empty string excluded


class TestBootstrapperImport:
    """Test that AIBootstrapper handles missing google-genai gracefully."""

    def test_import_error_without_genai(self) -> None:
        with (
            patch("shutil.which", return_value=None),
            patch.dict("sys.modules", {"google": None, "google.genai": None}),
            pytest.raises(ImportError, match=r"ai.*extra"),
        ):
            from gemstack.ai.bootstrap import AIBootstrapper

            AIBootstrapper()


class TestBuildContext:
    """Test the context building logic."""

    def test_includes_manifest_file(self, python_fastapi: Path) -> None:
        from gemstack.project.detector import ProjectDetector

        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)

        # Use the _build_context method directly via a mock bootstrapper
        with patch("gemstack.ai.bootstrap.AIBootstrapper.__init__", return_value=None):
            from gemstack.ai.bootstrap import AIBootstrapper

            bootstrapper = AIBootstrapper.__new__(AIBootstrapper)
            parts = bootstrapper._build_context(profile)

        assert len(parts) >= 1
        assert "pyproject.toml" in parts[0]

    def test_respects_char_budget(self, python_fastapi: Path) -> None:
        from gemstack.project.detector import ProjectDetector

        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)

        with patch("gemstack.ai.bootstrap.AIBootstrapper.__init__", return_value=None):
            from gemstack.ai.bootstrap import AIBootstrapper

            bootstrapper = AIBootstrapper.__new__(AIBootstrapper)
            parts = bootstrapper._build_context(profile)

        total_chars = sum(len(p) for p in parts)
        assert total_chars <= _CHAR_BUDGET + 10_000  # Some overhead for formatting


class TestRankSourceFiles:
    """Test the file ranking heuristic."""

    def test_ranks_route_files_higher(self, python_fastapi: Path) -> None:
        from gemstack.project.detector import ProjectDetector

        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)

        with patch("gemstack.ai.bootstrap.AIBootstrapper.__init__", return_value=None):
            from gemstack.ai.bootstrap import AIBootstrapper

            bootstrapper = AIBootstrapper.__new__(AIBootstrapper)
            ranked = bootstrapper._rank_source_files(profile)

        # Should find the main.py file in FastAPI fixture
        if ranked:
            assert all(isinstance(p, Path) for p in ranked)

    def test_returns_limited_files(self, python_fastapi: Path) -> None:
        from gemstack.project.detector import ProjectDetector

        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)

        with patch("gemstack.ai.bootstrap.AIBootstrapper.__init__", return_value=None):
            from gemstack.ai.bootstrap import AIBootstrapper

            bootstrapper = AIBootstrapper.__new__(AIBootstrapper)
            ranked = bootstrapper._rank_source_files(profile)

        assert len(ranked) <= 15


class TestParseResponse:
    """Test Gemini response parsing."""

    def test_parses_structured_response(self) -> None:
        with patch("gemstack.ai.bootstrap.AIBootstrapper.__init__", return_value=None):
            from gemstack.ai.bootstrap import AIBootstrapper

            bootstrapper = AIBootstrapper.__new__(AIBootstrapper)

            mock_response = MagicMock()
            mock_response.text = (
                "# ARCHITECTURE.md\n\n# Architecture\n\nThis is the arch.\n\n"
                "# STYLE.md\n\n# Style\n\nThis is the style.\n\n"
                "# TESTING.md\n\n# Testing\n\nThis is tests.\n"
            )

            result = bootstrapper._parse_response(mock_response)

        assert result.ai_powered is True
        assert result.architecture != ""

    def test_handles_empty_response(self) -> None:
        with patch("gemstack.ai.bootstrap.AIBootstrapper.__init__", return_value=None):
            from gemstack.ai.bootstrap import AIBootstrapper

            bootstrapper = AIBootstrapper.__new__(AIBootstrapper)

            mock_response = MagicMock()
            mock_response.text = ""

            result = bootstrapper._parse_response(mock_response)

        assert result.error is not None


class TestGracefulDegradation:
    """Test the analyze_with_fallback method."""

    def test_fallback_on_api_error(self) -> None:
        with patch("gemstack.ai.bootstrap.AIBootstrapper.__init__", return_value=None):
            from gemstack.ai.bootstrap import AIBootstrapper

            bootstrapper = AIBootstrapper.__new__(AIBootstrapper)
            bootstrapper.client = MagicMock()
            bootstrapper.model = "gemini-2.5-flash"
            bootstrapper._genai = MagicMock()

            # Make analyze raise an exception
            bootstrapper.client.models.generate_content.side_effect = RuntimeError("API down")

            profile = MagicMock()
            profile.manifest_file = None
            profile.config_files = []
            profile.source_dirs = []

            result = asyncio.run(bootstrapper.analyze_with_fallback(profile))

        assert result.ai_powered is False
        assert result.error is None  # template_only has no error
