"""Base protocol for agent adapters."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass
class InstallResult:
    """Result of an adapter install operation."""

    success: bool
    installed_count: int
    skipped_count: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@runtime_checkable
class AgentAdapter(Protocol):
    """Protocol that all installable agent adapters must implement."""

    @property
    def name(self) -> str:
        """Human-readable adapter name."""
        ...

    @property
    def is_available(self) -> bool:
        """Whether this agent tool is installed on the system."""
        ...

    def install(self, data_dir: Path, copy_mode: bool = False) -> InstallResult:
        """Install Gemstack commands for this agent."""
        ...

    def uninstall(self) -> InstallResult:
        """Remove Gemstack commands for this agent."""
        ...

    def verify(self) -> list[str]:
        """Verify installation integrity. Returns list of issues."""
        ...


@runtime_checkable
class ExportAdapter(Protocol):
    """Protocol for adapters that export context to a file."""

    def export(self, project_root: Path) -> str:
        """Generate formatted content from the project.

        Args:
            project_root: Path to the project root.

        Returns:
            The complete exported content as a string.
        """
        ...


def read_agent_context(project_root: Path, agent_files: list[tuple[str, str]]) -> str:
    """Helper to read and concatenate .agent/ file contents.

    Args:
        project_root: The project base path.
        agent_files: List of (filename, section title) tuples.

    Returns:
        Concatenated markdown text block.
    """
    agent_dir = project_root / ".agent"
    parts: list[str] = []

    for filename, section_title in agent_files:
        path = agent_dir / filename
        if path.exists():
            try:
                content = path.read_text().strip()
                parts.append(f"## {section_title}\n\n{content}\n\n---\n\n")
            except OSError as e:
                logger.warning(f"Failed to read {path}: {e}")

    return "".join(parts)
