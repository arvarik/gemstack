"""Gemstack plugin hook specifications — v1.0 Stable API.

Requires the ``gemstack[plugins]`` optional dependency (pluggy).

.. versionadded:: 1.0
    Plugin API locked. All hooks documented below are guaranteed to
    remain backward-compatible through the 1.x release series.
    New hooks may be added but existing signatures will not change.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

#: Stable plugin API version. Third-party plugins can check this
#: to verify compatibility with the host Gemstack installation.
PLUGIN_API_VERSION = "1.0"

try:
    import pluggy

    hookspec = pluggy.HookspecMarker("gemstack")
    hookimpl = pluggy.HookimplMarker("gemstack")
except ImportError:
    # Provide no-op stubs if pluggy isn't installed
    # so the module can still be imported for type checking
    def hookspec(func: Any) -> Any:  # type: ignore[misc]
        """No-op hookspec marker when pluggy is not installed."""
        return func

    def hookimpl(func: Any) -> Any:  # type: ignore[misc]
        """No-op hookimpl marker when pluggy is not installed."""
        return func


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from gemstack.project.detector import ProjectProfile


class GemstackHookSpec:
    """Hook specifications for Gemstack plugins.

    Third-party packages implement these hooks and register via
    ``[project.entry-points."gemstack"]`` in their ``pyproject.toml``.

    All hooks are optional — plugins only need to implement the hooks
    they care about.

    .. versionadded:: 1.0
    """

    # ── Lifecycle hooks ────────────────────────────────────────────

    @hookspec
    def gemstack_post_init(self, project_root: Path, profile: ProjectProfile) -> None:
        """Called after ``gemstack init`` completes.

        Plugins can add custom files, modify generated content, etc.

        Args:
            project_root: Path to the initialized project.
            profile: Detected project profile (language, topology, etc.).

        .. versionadded:: 0.4.0
        """
        ...

    @hookspec
    def gemstack_pre_run(self, step: str, feature: str) -> None:
        """Called before ``gemstack run`` executes a step.

        Plugins can perform validation, logging, or setup.

        Args:
            step: Workflow step being executed (e.g., "step1-spec").
            feature: Feature description string.

        .. versionadded:: 1.0
        """
        ...

    @hookspec
    def gemstack_post_run(self, step: str, result: Any) -> None:
        """Called after ``gemstack run`` completes a step.

        Plugins can perform cleanup, notifications, or post-processing.

        Args:
            step: Workflow step that was executed.
            result: An ``ExecutionResult`` instance with execution details.

        .. versionadded:: 1.0
        """
        ...

    # ── Compilation hooks ──────────────────────────────────────────

    @hookspec
    def gemstack_pre_compile(
        self, step: str, sections: list[tuple[str, str]]
    ) -> list[tuple[str, str]]:
        """Called before context compilation stitches sections together.

        Plugins can modify, add, or remove sections from the compiled context.
        Must return the (possibly modified) sections list.

        Args:
            step: Workflow step being compiled.
            sections: List of (section_name, content) tuples.

        Returns:
            The (possibly modified) sections list.

        .. versionadded:: 0.4.0
        """
        return sections

    @hookspec
    def gemstack_post_compile(self, step: str, compiled: str) -> str:
        """Called after context compilation.

        Plugins can post-process the compiled context string.
        Must return the (possibly modified) compiled string.

        Args:
            step: Workflow step being compiled.
            compiled: The fully compiled context string.

        Returns:
            The (possibly modified) compiled string.

        .. versionadded:: 0.4.0
        """
        return compiled

    # ── Extension hooks ────────────────────────────────────────────

    @hookspec
    def gemstack_register_topologies(self) -> list[dict[str, str]]:
        """Register custom topology profiles.

        Returns a list of dicts with keys:
            - ``name``: topology identifier (e.g., "mobile")
            - ``description``: human-readable description
            - ``content``: markdown content of the topology profile

        .. versionadded:: 0.4.0
        """
        return []

    @hookspec
    def gemstack_register_roles(self) -> list[dict[str, str]]:
        """Register custom role definitions.

        Returns a list of dicts with keys:
            - ``name``: role identifier
            - ``description``: human-readable description
            - ``content``: markdown content of the role definition

        .. versionadded:: 0.4.0
        """
        return []

    @hookspec
    def gemstack_register_checks(self) -> list[Callable[..., Any]]:
        """Register custom validation checks for ``gemstack check``.

        Each callable receives a ``project_root: Path`` argument and returns
        a list of error strings (empty list if check passes).

        .. versionadded:: 0.4.0
        """
        return []
