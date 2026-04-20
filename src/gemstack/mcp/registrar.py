"""MCP server registration — adds gemstack to agent configurations.

Supports registering with:
- Gemini CLI (~/.gemini/settings.json)
- Claude Desktop (~/Library/Application Support/Claude/claude_desktop_config.json)
- Cursor (.cursor/mcp.json)
- Cline (VS Code globalStorage cline_mcp_settings.json)
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from gemstack.core.fileutil import write_atomic

logger = logging.getLogger(__name__)

# MCP server entry to inject into agent configs
_MCP_ENTRY = {
    "command": "gemstack",
    "args": ["mcp", "serve", "--transport", "stdio"],
}


def register_mcp_server(
    *,
    gemini_cli: bool = False,
    claude_desktop: bool = False,
    cursor: bool = False,
    cline: bool = False,
    project_root: Path | None = None,
) -> list[str]:
    """Register gemstack MCP server with specified agents.

    Args:
        gemini_cli: Register with Gemini CLI.
        claude_desktop: Register with Claude Desktop.
        cursor: Register with Cursor (project-local).
        cline: Register with Cline (global).
        project_root: Project root for Cursor (project-local config).

    Returns:
        List of registration status messages.
    """
    messages: list[str] = []

    if gemini_cli:
        messages.append(_register_gemini_cli())
    if claude_desktop:
        messages.append(_register_claude_desktop())
    if cursor:
        messages.append(_register_cursor(project_root or Path(".")))
    if cline:
        messages.append(_register_cline())

    return messages


def _register_gemini_cli() -> str:
    """Register with Gemini CLI settings."""
    config_path = Path.home() / ".gemini" / "settings.json"
    return _upsert_mcp_config(config_path, "Gemini CLI", key_path="mcpServers")


def _register_claude_desktop() -> str:
    """Register with Claude Desktop config."""
    if sys.platform == "darwin":
        config_path = (
            Path.home()
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    elif sys.platform == "win32":
        config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:
        config_path = Path.home() / ".config" / "claude" / "claude_desktop_config.json"

    return _upsert_mcp_config(config_path, "Claude Desktop", key_path="mcpServers")


def _register_cursor(project_root: Path) -> str:
    """Register with Cursor project-local config."""
    config_path = project_root.resolve() / ".cursor" / "mcp.json"
    return _upsert_mcp_config(config_path, "Cursor", key_path="mcpServers")


def _register_cline() -> str:
    """Register with Cline global settings."""
    if sys.platform == "darwin":
        config_path = (
            Path.home()
            / "Library"
            / "Application Support"
            / "Code"
            / "User"
            / "globalStorage"
            / "saoudrizwan.claude-dev"
            / "settings"
            / "cline_mcp_settings.json"
        )
    elif sys.platform == "win32":
        config_path = (
            Path.home()
            / "AppData"
            / "Roaming"
            / "Code"
            / "User"
            / "globalStorage"
            / "saoudrizwan.claude-dev"
            / "settings"
            / "cline_mcp_settings.json"
        )
    else:
        config_path = (
            Path.home()
            / ".config"
            / "Code"
            / "User"
            / "globalStorage"
            / "saoudrizwan.claude-dev"
            / "settings"
            / "cline_mcp_settings.json"
        )

    return _upsert_mcp_config(config_path, "Cline", key_path="mcpServers")


def _upsert_mcp_config(config_path: Path, agent_name: str, key_path: str) -> str:
    """Read a JSON config, insert gemstack MCP entry, write back.

    Creates the file and parent directories if they don't exist.
    """
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = json.loads(config_path.read_text()) if config_path.exists() else {}

        # Initialize the mcpServers key if missing
        if key_path not in data:
            data[key_path] = {}

        data[key_path]["gemstack"] = _MCP_ENTRY

        write_atomic(config_path, json.dumps(data, indent=2) + "\n")
        return f"✅ Registered with {agent_name}: {config_path}"

    except Exception as e:
        logger.warning(f"Failed to register with {agent_name}: {e}")
        return f"❌ Failed to register with {agent_name}: {e}"
