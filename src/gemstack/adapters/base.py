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
    """Protocol that all installable agent adapters must implement.

    Adapters are responsible for installing/uninstalling Gemstack
    workflow commands into a specific AI agent tool (e.g., Gemini CLI,
    Cursor, Claude Desktop).

    Example — a minimal adapter for a custom agent::

        class MyAgentAdapter:
            @property
            def name(self) -> str:
                return "My Agent"

            @property
            def is_available(self) -> bool:
                return shutil.which("myagent") is not None

            def install(self, data_dir: Path, copy_mode: bool = False) -> InstallResult:
                target = Path.home() / ".myagent" / "workflows"
                target.mkdir(parents=True, exist_ok=True)
                count = 0
                for md_file in data_dir.glob("*.md"):
                    (target / md_file.name).write_text(md_file.read_text())
                    count += 1
                return InstallResult(success=True, installed_count=count, skipped_count=0)

            def uninstall(self) -> InstallResult:
                return InstallResult(success=True, installed_count=0, skipped_count=0)

            def verify(self) -> list[str]:
                return []
    """

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
