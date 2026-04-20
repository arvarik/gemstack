# Getting Started with Gemstack

Gemstack is built for standard Python environments but is best installed globally via a tool like `pipx` or `uv`.

## Installation Methods

### pipx (Recommended)
Since Gemstack is primarily a CLI tool, `pipx` installs it in an isolated environment while making the `gemstack` command globally available:
```bash
pipx install gemstack
pipx install 'gemstack[ai]'    # With AI bootstrapping
pipx install 'gemstack[mcp]'   # With MCP server
```

### uv (Fastest)
```bash
uv tool install gemstack
uv tool install 'gemstack[ai,mcp]'
```

### Standard pip
```bash
pip install gemstack
pip install "gemstack[all]"
```

## Initializing a Project

Navigate to your existing codebase:
```bash
cd your-project/
gemstack init
```

If you installed with AI support (`gemstack[ai]`), you can bootstrap your project using deep AI analysis:
```bash
gemstack init --ai
```
This sends your key source files to Gemini to correctly populate your `.agent/` context directories with accurate, concrete details about your stack, rather than you having to manually write them!

## First Workflow

```bash
gemstack status       # See current project state
gemstack route        # Get the recommended next action
gemstack start "Add user search"  # Initialize a new feature lifecycle
gemstack run step1-spec --feature "Add user search"  # Execute Step 1 via Gemini
```
