"""Agent adapters for Gemstack CLI."""

from .antigravity import AntigravityAdapter
from .base import AgentAdapter, ExportAdapter, InstallResult
from .claude import ClaudeExportAdapter
from .cursor import CursorExportAdapter
from .gemini import GeminiExportAdapter
from .gemini_cli import GeminiCLIAdapter

__all__ = [
    "AgentAdapter",
    "AntigravityAdapter",
    "ClaudeExportAdapter",
    "CursorExportAdapter",
    "ExportAdapter",
    "GeminiCLIAdapter",
    "GeminiExportAdapter",
    "InstallResult",
]
