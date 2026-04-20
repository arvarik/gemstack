"""Tests for the tail TUI module.

Tests the minimal mode directly. The Textual TUI tests require
the [tail] extra and are skipped if not installed.
"""


import pytest


class TestMinimalTailParsing:
    """Tests for the minimal mode parsing helpers."""

    def test_parse_state(self) -> None:
        from gemstack.cli.tail_cmd import _parse_state

        assert _parse_state("[STATE: IN_PROGRESS]") == "IN_PROGRESS"
        assert _parse_state("[STATE: INITIALIZED]") == "INITIALIZED"
        assert _parse_state("no state here") == "UNKNOWN"

    def test_parse_feature(self) -> None:
        from gemstack.cli.tail_cmd import _parse_feature

        content = "## Current Focus\n\nOAuth integration"
        assert _parse_feature(content) == "OAuth integration"

    def test_parse_feature_missing(self) -> None:
        from gemstack.cli.tail_cmd import _parse_feature

        assert _parse_feature("no focus section") == "(none)"


class TestTailAppParsing:
    """Tests for the TUI app state parsing."""

    def test_parse_lifecycle(self) -> None:
        try:
            from gemstack.tui.tail_app import GemstackTailApp
        except ImportError:
            pytest.skip("textual/watchdog not installed")

        content = "- [x] Spec\n- [x] Trap\n- [ ] Build\n- [ ] Audit\n- [ ] Ship"
        lifecycle = GemstackTailApp._parse_lifecycle(content)

        assert lifecycle["Spec"] is True
        assert lifecycle["Trap"] is True
        assert lifecycle["Build"] is False
        assert lifecycle["Audit"] is False

    def test_parse_state(self) -> None:
        try:
            from gemstack.tui.tail_app import GemstackTailApp
        except ImportError:
            pytest.skip("textual/watchdog not installed")

        assert GemstackTailApp._parse_state("[STATE: IN_PROGRESS]") == "IN_PROGRESS"
        assert GemstackTailApp._parse_state("no state") == "UNKNOWN"
