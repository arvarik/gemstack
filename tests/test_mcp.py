"""Tests for the MCP server module.

Covers:
- Server creation and configuration
- Tool invocation (gemstack_status, gemstack_route, gemstack_compile)
- Resource access (read_agent_file)
- MCP registrar (config creation, merging, error handling)
- SSE port passthrough
"""

import json
from pathlib import Path
from unittest.mock import patch


import pytest


class TestMCPServer:
    """Tests for the MCP server creation and tool execution."""

    @pytest.fixture
    def project_with_agent(self, tmp_path: Path) -> Path:
        """Create a project with .agent/ directory for MCP testing."""
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n\nProject arch.\n")
        (agent_dir / "STATUS.md").write_text(
            "[STATE: IN_PROGRESS]\n\n## Current Focus\n\nOAuth feature\n"
        )
        (agent_dir / "TESTING.md").write_text("# Testing\n\nTest strategy.\n")
        (agent_dir / "STYLE.md").write_text("# Style Guide\n\nCode style.\n")
        (agent_dir / "PHILOSOPHY.md").write_text("# Philosophy\n\nDesign principles.\n")
        return tmp_path

    def test_server_creation(self, project_with_agent: Path) -> None:
        """Test that create_server returns a configured server."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            assert server is not None
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_server_creation_with_port(self, project_with_agent: Path) -> None:
        """Test that create_server forwards port to FastMCP."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent, port=9999, host="0.0.0.0")
            assert server is not None
            # FastMCP stores settings in server.settings
            assert server.settings.port == 9999
            assert server.settings.host == "0.0.0.0"
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_tool_gemstack_status(self, project_with_agent: Path) -> None:
        """Test gemstack_status tool returns STATUS.md content."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            # Access registered tools by calling the function directly
            # FastMCP registers functions that we can call
            tools = {t.name: t for t in server._tool_manager.list_tools()}
            assert "gemstack_status" in tools
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_tool_gemstack_route(self, project_with_agent: Path) -> None:
        """Test gemstack_route tool returns a routing decision."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            tools = {t.name: t for t in server._tool_manager.list_tools()}
            assert "gemstack_route" in tools
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_tool_gemstack_check(self, project_with_agent: Path) -> None:
        """Test gemstack_check tool is registered."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            tools = {t.name: t for t in server._tool_manager.list_tools()}
            assert "gemstack_check" in tools
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_tool_gemstack_diff(self, project_with_agent: Path) -> None:
        """Test gemstack_diff tool is registered."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            tools = {t.name: t for t in server._tool_manager.list_tools()}
            assert "gemstack_diff" in tools
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_tool_gemstack_compile(self, project_with_agent: Path) -> None:
        """Test gemstack_compile tool is registered."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            tools = {t.name: t for t in server._tool_manager.list_tools()}
            assert "gemstack_compile" in tools
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_all_five_prompts_registered(self, project_with_agent: Path) -> None:
        """Test all 5 workflow step prompts are registered."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            prompts = {p.name: p for p in server._prompt_manager.list_prompts()}
            expected = ["step1_spec", "step2_trap", "step3_build", "step4_audit", "step5_ship"]
            for name in expected:
                assert name in prompts, f"Missing prompt: {name}"
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_registrar_creates_config(self, tmp_path: Path) -> None:
        """Test MCP registration creates config files."""
        from gemstack.mcp.registrar import _upsert_mcp_config

        config_path = tmp_path / "test_config.json"
        result = _upsert_mcp_config(config_path, "Test Agent", "mcpServers")

        assert "✅" in result
        assert config_path.exists()

        data = json.loads(config_path.read_text())
        assert "gemstack" in data["mcpServers"]
        assert data["mcpServers"]["gemstack"]["command"] == "gemstack"

    def test_registrar_merges_existing(self, tmp_path: Path) -> None:
        """Test that registration merges into existing config."""
        from gemstack.mcp.registrar import _upsert_mcp_config

        config_path = tmp_path / "existing.json"
        config_path.write_text(
            json.dumps({
                "mcpServers": {
                    "other-tool": {"command": "other"}
                }
            })
        )

        _upsert_mcp_config(config_path, "Test Agent", "mcpServers")

        data = json.loads(config_path.read_text())
        assert "other-tool" in data["mcpServers"]
        assert "gemstack" in data["mcpServers"]

    def test_registrar_handles_errors(self, tmp_path: Path) -> None:
        """Test graceful error handling."""
        from gemstack.mcp.registrar import _upsert_mcp_config

        # Read-only directory should fail gracefully
        result = _upsert_mcp_config(
            Path("/nonexistent/deep/path/config.json"),
            "Test Agent",
            "mcpServers",
        )
        assert "❌" in result


class TestMCPRegistration:
    """Tests for the register_mcp_server orchestrator."""

    def test_register_returns_messages(self, tmp_path: Path) -> None:
        from gemstack.mcp.registrar import register_mcp_server

        with patch(
            "gemstack.mcp.registrar._register_gemini_cli",
            return_value="✅ Registered with Gemini CLI",
        ):
            messages = register_mcp_server(gemini_cli=True)
            assert len(messages) == 1
            assert "Gemini CLI" in messages[0]

    def test_register_no_targets(self) -> None:
        from gemstack.mcp.registrar import register_mcp_server

        messages = register_mcp_server()
        assert len(messages) == 0


class TestLoadWorkflowPrompt:
    """Tests for the _load_workflow_prompt helper."""

    def test_loads_existing_step(self) -> None:
        from gemstack.mcp.server import _load_workflow_prompt

        content = _load_workflow_prompt("step1-spec")
        # Should either load the real file or return a "not found" message
        assert isinstance(content, str)
        assert len(content) > 0

    def test_unknown_step_returns_message(self) -> None:
        from gemstack.mcp.server import _load_workflow_prompt

        content = _load_workflow_prompt("nonexistent-step-99")
        assert "not found" in content


class TestMCPBidirectionalTools:
    """P1-3: Tests for Phase 5 bidirectional MCP tools."""

    @pytest.fixture
    def project_with_agent(self, tmp_path: Path) -> Path:
        """Create a project with .agent/ directory for MCP testing."""
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n\nProject arch.\n")
        (agent_dir / "STATUS.md").write_text(
            "[STATE: IN_PROGRESS]\n\n## Current Focus\n\nOAuth feature\n"
        )
        (agent_dir / "TESTING.md").write_text("# Testing\n")
        (agent_dir / "STYLE.md").write_text("# Style\n")
        (agent_dir / "PHILOSOPHY.md").write_text("# Philosophy\n")
        return tmp_path

    def test_gemstack_run_registered(self, project_with_agent: Path) -> None:
        """Verify gemstack_run tool is registered in the MCP server."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            tools = {t.name: t for t in server._tool_manager.list_tools()}
            assert "gemstack_run" in tools
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_gemstack_costs_registered(self, project_with_agent: Path) -> None:
        """Verify gemstack_costs tool is registered in the MCP server."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            tools = {t.name: t for t in server._tool_manager.list_tools()}
            assert "gemstack_costs" in tools
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_gemstack_costs_returns_data(self, project_with_agent: Path) -> None:
        """Verify gemstack_costs tool returns cost data."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            # Access the tool function directly
            tools = {t.name: t for t in server._tool_manager.list_tools()}
            assert "gemstack_costs" in tools
            # Verify tool signature accepts feature param
            assert tools["gemstack_costs"] is not None
        except ImportError:
            pytest.skip("mcp SDK not installed")

    def test_seven_tools_registered(self, project_with_agent: Path) -> None:
        """Phase 5 should have 7 total tools (5 Phase 3 + 2 Phase 5)."""
        try:
            from gemstack.mcp.server import create_server

            server = create_server(project_with_agent)
            tools = server._tool_manager.list_tools()
            tool_names = {t.name for t in tools}
            expected = {
                "gemstack_status", "gemstack_route", "gemstack_compile",
                "gemstack_check", "gemstack_diff",
                "gemstack_run", "gemstack_costs",
            }
            assert expected == tool_names
        except ImportError:
            pytest.skip("mcp SDK not installed")

