"""Base protocol for agent adapters."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


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
    """Protocol that all agent adapters must implement."""

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
