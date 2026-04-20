"""Plugin system for extending Gemstack — v1.0 Stable API.

Uses pluggy for hook-based extensibility. Plugins register via the
``gemstack`` entry_points group in their pyproject.toml.

Requires the ``gemstack[plugins]`` optional dependency (pluggy).
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any

# Re-export the stable API version
from gemstack.plugins.hooks import PLUGIN_API_VERSION

if TYPE_CHECKING:
    import pluggy

logger = logging.getLogger(__name__)

# Module-level singleton — lazily initialised
_plugin_manager: pluggy.PluginManager | None = None
_plugin_manager_lock = threading.Lock()


def get_plugin_manager() -> pluggy.PluginManager:
    """Create and return the global Gemstack plugin manager.

    Discovers plugins via the ``gemstack`` entry_points group.
    The manager is cached as a module-level singleton so repeated calls
    are cheap.  Thread-safe via double-checked locking.

    Raises:
        ImportError: If pluggy is not installed.
    """
    global _plugin_manager
    if _plugin_manager is not None:
        return _plugin_manager

    with _plugin_manager_lock:
        # Re-check after acquiring lock (double-checked locking)
        if _plugin_manager is not None:
            return _plugin_manager

        try:
            import pluggy as _pluggy
        except ImportError as e:
            msg = (
                "Plugin system requires the 'plugins' extra. "
                "Install with: pip install gemstack[plugins]"
            )
            raise ImportError(msg) from e

        from gemstack.plugins.hooks import GemstackHookSpec

        pm = _pluggy.PluginManager("gemstack")
        pm.add_hookspecs(GemstackHookSpec)

        # Discover installed plugins via entry_points
        try:
            pm.load_setuptools_entrypoints("gemstack")
        except Exception as e:
            # Never crash due to a bad plugin
            logger.warning(f"Failed to load some plugins: {e}")

        _plugin_manager = pm
        return pm


def reset_plugin_manager() -> None:
    """Reset the cached plugin manager (mainly for testing)."""
    global _plugin_manager
    _plugin_manager = None


def get_plugin_topologies() -> list[dict[str, str]]:
    """Convenience: collect custom topologies from all loaded plugins.

    Returns a list of dicts, each with keys ``name``, ``description``,
    and ``content``.  Returns an empty list if pluggy is not installed
    or no plugins provide topologies.
    """
    try:
        pm = get_plugin_manager()
    except ImportError:
        return []

    results: list[dict[str, str]] = []
    try:
        # pluggy returns a list-of-lists (one per plugin)
        for topology_list in pm.hook.gemstack_register_topologies():
            if isinstance(topology_list, list):
                results.extend(topology_list)
    except Exception as e:
        logger.warning(f"Error collecting plugin topologies: {e}")

    return results


def fire_post_init(project_root: Any, profile: Any) -> None:
    """Fire the ``gemstack_post_init`` hook if plugins are available."""
    try:
        pm = get_plugin_manager()
        pm.hook.gemstack_post_init(project_root=project_root, profile=profile)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Plugin post-init hook error: {e}")


def fire_pre_compile(step: str, sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Fire ``gemstack_pre_compile`` hook.

    Returns the (possibly modified) sections list.
    """
    try:
        pm = get_plugin_manager()
        results = pm.hook.gemstack_pre_compile(step=step, sections=sections)
        # Take the last non-None result (pluggy convention)
        for result in reversed(results):
            if result is not None:
                return result  # type: ignore[no-any-return]
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Plugin pre-compile hook error: {e}")
    return sections


def fire_post_compile(step: str, compiled: str) -> str:
    """Fire ``gemstack_post_compile`` hook.

    Returns the (possibly modified) compiled string.
    """
    try:
        pm = get_plugin_manager()
        results = pm.hook.gemstack_post_compile(step=step, compiled=compiled)
        for result in reversed(results):
            if result is not None:
                return result  # type: ignore[no-any-return]
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Plugin post-compile hook error: {e}")
    return compiled


def fire_pre_run(step: str, feature: str) -> None:
    """Fire ``gemstack_pre_run`` hook before autonomous execution."""
    try:
        pm = get_plugin_manager()
        pm.hook.gemstack_pre_run(step=step, feature=feature)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Plugin pre-run hook error: {e}")


def fire_post_run(step: str, result: Any) -> None:
    """Fire ``gemstack_post_run`` hook after autonomous execution."""
    try:
        pm = get_plugin_manager()
        pm.hook.gemstack_post_run(step=step, result=result)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Plugin post-run hook error: {e}")


def get_api_version() -> str:
    """Return the current plugin API version string."""
    return PLUGIN_API_VERSION


def fire_register_checks(project_root: Any) -> list[str]:
    """Fire ``gemstack_register_checks`` hook and run all plugin checks.

    Returns a flat list of error strings from all plugin-provided validators.
    Returns an empty list if pluggy is not installed or no plugins provide checks.
    """
    errors: list[str] = []
    try:
        pm = get_plugin_manager()
        # Each plugin returns a list of check callables
        for check_list in pm.hook.gemstack_register_checks():
            if not isinstance(check_list, list):
                continue
            for check_fn in check_list:
                try:
                    result = check_fn(project_root)
                    if isinstance(result, list):
                        errors.extend(result)
                except Exception as e:
                    logger.warning(f"Plugin check error: {e}")
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Plugin register_checks hook error: {e}")
    return errors
