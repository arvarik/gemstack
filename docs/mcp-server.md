# MCP Server

Gemstack works out-of-the-box with Cursor, Claude Desktop, and compatible AI IDEs using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## Running the Server

Start via standard I/O (stdio mode):
```bash
gemstack mcp serve
```

Start exposing via SSE transport:
```bash
gemstack mcp serve --transport sse --port 8765
```

## Registration

To automatically register the running MCP Server so your IDEs or CLIs can connect safely, run:
```bash
gemstack mcp register --cursor
gemstack mcp register --claude-desktop
gemstack mcp register --gemini-cli
gemstack mcp register --cline
```

## What the Server Exposes
Once successfully configured, your IDE's agent will now have the ability to explicitly read Gemstack `ARCHITECTURE.md` formats through `gemstack://agent/...` resources, and trigger drift detection checks automatically.
