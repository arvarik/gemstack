# Configuration & Global Integrations

## Global Config Storage

By default, configurations and limits are maintained in standard local config directories (e.g., `~/.config/gemstack/config.toml`).

```bash
gemstack config set api-key YOUR_GEMINI_API_KEY  # Required for gemstack run
gemstack config set model gemini-2.5-pro          # Default: gemini-2.5-flash
gemstack config show                              # View current settings (keys masked)
```

## Antigravity and Gemini CLI

You can easily mount Gemstack globally alongside your system agent tools like the Gemini CLI to gain slash (`/`) command functionalities.

```bash
gemstack install     # Symlinks into Antigravity global workflow directories
gemstack uninstall   # Remove all symlinks
```

After doing so, you can utilize the AI role and lifecycle tools universally via `/architect`, `/sdet`, `/build`, etc.
