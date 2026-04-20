"""Integration tests for the plugin system.

Validates the full cycle: plugin registration → topology discovery →
hook firing. This is the Phase 4 exit criteria test.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gemstack.plugins import (
    fire_post_compile,
    fire_post_init,
    fire_pre_compile,
    get_plugin_topologies,
    reset_plugin_manager,
)


@pytest.fixture(autouse=True)
def _reset_pm() -> None:
    """Reset the plugin manager singleton between tests."""
    reset_plugin_manager()
    yield  # type: ignore[misc]
    reset_plugin_manager()


class TestPluginTopologyRegistration:
    """Exit criteria: a mock plugin registers a topology and it's discoverable."""

    def test_no_plugins_returns_empty(self) -> None:
        # With pluggy installed but no plugins registered
        try:
            topos = get_plugin_topologies()
            assert isinstance(topos, list)
        except ImportError:
            pytest.skip("pluggy not installed")

    def test_plugin_registers_topology(self) -> None:
        """Simulate a third-party plugin registering a 'mobile' topology."""
        try:
            from gemstack.plugins import get_plugin_manager
            from gemstack.plugins.hooks import hookimpl
        except ImportError:
            pytest.skip("pluggy not installed")

        class MobilePlugin:
            @hookimpl
            def gemstack_register_topologies(self) -> list[dict[str, str]]:
                return [{
                    "name": "mobile",
                    "description": "iOS/Android mobile app guardrails",
                    "content": "# Mobile Topology\n\nMobile-specific rules.",
                }]

        pm = get_plugin_manager()
        pm.register(MobilePlugin())

        topos = get_plugin_topologies()
        assert len(topos) >= 1
        names = [t["name"] for t in topos]
        assert "mobile" in names

    def test_multiple_plugins_register_topologies(self) -> None:
        """Multiple plugins can register topologies."""
        try:
            from gemstack.plugins import get_plugin_manager
            from gemstack.plugins.hooks import hookimpl
        except ImportError:
            pytest.skip("pluggy not installed")

        class PluginA:
            @hookimpl
            def gemstack_register_topologies(self) -> list[dict[str, str]]:
                return [{"name": "mobile", "description": "Mobile", "content": "m"}]

        class PluginB:
            @hookimpl
            def gemstack_register_topologies(self) -> list[dict[str, str]]:
                return [{"name": "iot", "description": "IoT", "content": "i"}]

        pm = get_plugin_manager()
        pm.register(PluginA())
        pm.register(PluginB())

        topos = get_plugin_topologies()
        names = [t["name"] for t in topos]
        assert "mobile" in names
        assert "iot" in names


class TestPluginHooks:
    """Tests for plugin hook firing."""

    def test_fire_post_init_noop_without_pluggy(self, tmp_path: Path) -> None:
        """post_init should not crash even if pluggy is not installed."""
        with patch("gemstack.plugins.get_plugin_manager", side_effect=ImportError):
            fire_post_init(tmp_path, MagicMock())
            # Should not raise

    def test_fire_pre_compile_passthrough(self) -> None:
        """pre_compile returns sections unchanged if no plugins modify them."""
        sections = [("Header", "content")]
        result = fire_pre_compile("step1-spec", sections)
        assert result == sections

    def test_fire_post_compile_passthrough(self) -> None:
        """post_compile returns compiled unchanged if no plugins modify it."""
        compiled = "compiled context"
        result = fire_post_compile("step1-spec", compiled)
        assert result == compiled

    def test_fire_pre_compile_with_plugin(self) -> None:
        """A plugin can modify sections via pre_compile hook."""
        try:
            from gemstack.plugins import get_plugin_manager
            from gemstack.plugins.hooks import hookimpl
        except ImportError:
            pytest.skip("pluggy not installed")

        class ModifyPlugin:
            @hookimpl
            def gemstack_pre_compile(
                self, step: str, sections: list[tuple[str, str]]
            ) -> list[tuple[str, str]]:
                return [*sections, ("Plugin Section", "injected by plugin")]

        pm = get_plugin_manager()
        pm.register(ModifyPlugin())

        sections = [("Header", "content")]
        result = fire_pre_compile("step1-spec", sections)
        assert len(result) == 2
        assert result[1][0] == "Plugin Section"

    def test_fire_post_compile_with_plugin(self) -> None:
        """A plugin can modify compiled output via post_compile hook."""
        try:
            from gemstack.plugins import get_plugin_manager
            from gemstack.plugins.hooks import hookimpl
        except ImportError:
            pytest.skip("pluggy not installed")

        class ModifyPlugin:
            @hookimpl
            def gemstack_post_compile(self, step: str, compiled: str) -> str:
                return compiled + "\n\n<!-- Plugin was here -->"

        pm = get_plugin_manager()
        pm.register(ModifyPlugin())

        result = fire_post_compile("step1-spec", "original content")
        assert "Plugin was here" in result


class TestPluginManagerSingleton:
    """Tests for the lazy-initialized singleton pattern."""

    def test_singleton_returns_same_instance(self) -> None:
        try:
            from gemstack.plugins import get_plugin_manager

            pm1 = get_plugin_manager()
            pm2 = get_plugin_manager()
            assert pm1 is pm2
        except ImportError:
            pytest.skip("pluggy not installed")

    def test_reset_clears_singleton(self) -> None:
        try:
            from gemstack.plugins import get_plugin_manager

            pm1 = get_plugin_manager()
            reset_plugin_manager()
            pm2 = get_plugin_manager()
            assert pm1 is not pm2
        except ImportError:
            pytest.skip("pluggy not installed")


class TestPhase5Hooks:
    """P1-5: Tests for gemstack_pre_run and gemstack_post_run hooks."""

    def test_fire_pre_run_noop_without_pluggy(self) -> None:
        """pre_run should not crash even if pluggy is not installed."""
        from gemstack.plugins import fire_pre_run

        with patch(
            "gemstack.plugins.get_plugin_manager", side_effect=ImportError
        ):
            fire_pre_run("step1-spec", "test feature")  # Should not raise

    def test_fire_post_run_noop_without_pluggy(self) -> None:
        """post_run should not crash even if pluggy is not installed."""
        from gemstack.plugins import fire_post_run

        with patch(
            "gemstack.plugins.get_plugin_manager", side_effect=ImportError
        ):
            fire_post_run("step1-spec", MagicMock())  # Should not raise

    def test_fire_pre_run_calls_hook(self) -> None:
        """A registered plugin's pre_run hook should be called."""
        try:
            from gemstack.plugins import fire_pre_run, get_plugin_manager
            from gemstack.plugins.hooks import hookimpl
        except ImportError:
            pytest.skip("pluggy not installed")

        class RunPlugin:
            called = False

            @hookimpl
            def gemstack_pre_run(self, step: str, feature: str) -> None:
                RunPlugin.called = True

        pm = get_plugin_manager()
        pm.register(RunPlugin())

        fire_pre_run("step1-spec", "test")
        assert RunPlugin.called

    def test_fire_post_run_calls_hook(self) -> None:
        """A registered plugin's post_run hook should be called."""
        try:
            from gemstack.plugins import fire_post_run, get_plugin_manager
            from gemstack.plugins.hooks import hookimpl
        except ImportError:
            pytest.skip("pluggy not installed")

        class RunPlugin:
            received_step = None
            received_result = None

            @hookimpl
            def gemstack_post_run(self, step: str, result: object) -> None:
                RunPlugin.received_step = step
                RunPlugin.received_result = result

        pm = get_plugin_manager()
        pm.register(RunPlugin())

        mock_result = MagicMock()
        fire_post_run("step3-build", mock_result)
        assert RunPlugin.received_step == "step3-build"
        assert RunPlugin.received_result is mock_result

    def test_fire_pre_run_exception_isolation(self) -> None:
        """A crashing pre_run plugin should not propagate."""
        try:
            from gemstack.plugins import fire_pre_run, get_plugin_manager
            from gemstack.plugins.hooks import hookimpl
        except ImportError:
            pytest.skip("pluggy not installed")

        class BadPlugin:
            @hookimpl
            def gemstack_pre_run(self, step: str, feature: str) -> None:
                raise RuntimeError("plugin crashed")

        pm = get_plugin_manager()
        pm.register(BadPlugin())

        # Should not raise — exception is caught and logged
        fire_pre_run("step1-spec", "test")

