# Gemstack: Agentic Development Framework

A complete framework for building personal software projects using AI agents (Gemini CLI, Antigravity, Claude Code, or any LLM-based coding tool). It defines a system of composable **roles** (how the agent thinks) and **phases** (what process the agent follows) that together produce consistent, high-quality output across multiple projects and tech stacks.

This repository serves as your **single source of truth**. You edit the markdown files here, and they are globally available as slash commands (`/`) in both **Gemini CLI** and **Antigravity**.

## Directory Structure

*   `roles/`: Contains markdown files defining agent mindsets (e.g., `architect.md`, `product-visionary.md`).
*   `phases/`: Contains markdown files defining the workflow steps (e.g., `plan.md`, `build.md`).
*   `roles_phases.md`: The original master document containing all definitions.

## How It Works

*   **Antigravity:** Uses the `.md` files directly. It requires a YAML frontmatter block (e.g., `--- name: architect ---`) at the top of each file and requires the files to be symlinked directly into `~/.agent/workflows/`.
*   **Gemini CLI:** Uses `.toml` wrappers in `~/.gemini/commands/`. These TOML files dynamically read (inject) the contents of your `.md` files using the `!{cat ...}` shell command.

Because both tools reference the files in this repository, **any edits you make to the files in `roles/` or `phases/` will instantly apply globally across all your projects.**

---

## Installation (Setting up on a new computer)

If you clone this repository to a new machine, run the following steps to wire up the slash commands for both Gemini CLI and Antigravity.

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/gemstack.git ~/Documents/github/gemstack
cd ~/Documents/github/gemstack
```

### 2. Setup Antigravity (Global Slash Commands)
Antigravity looks for `.md` files in `~/.agent/workflows/`. It does not read subdirectories, so we symlink the files directly.

```bash
# Create the global workflows directory
mkdir -p ~/.agent/workflows

# Symlink all roles and phases directly into the workflows folder
find $(pwd)/roles -name "*.md" -exec ln -sfn {} ~/.agent/workflows/ \;
find $(pwd)/phases -name "*.md" -exec ln -sfn {} ~/.agent/workflows/ \;
```
*Note: The `.md` files in this repo already contain the required YAML frontmatter.*

### 3. Setup Gemini CLI (Global Slash Commands)
Gemini CLI requires `.toml` definitions in `~/.gemini/commands/`. We use a quick Node.js script to generate these wrappers so they dynamically load your markdown files.

Run this script from the root of the `gemstack` repository:

```javascript
// Save this as setup-gemini.js and run with `node setup-gemini.js`
const fs = require('fs');
const path = require('path');
const os = require('os');

const geminiCommandsDir = path.join(os.homedir(), '.gemini', 'commands');
const repoRolesDir = path.join(process.cwd(), 'roles');
const repoPhasesDir = path.join(process.cwd(), 'phases');

// Ensure directories exist
fs.mkdirSync(path.join(geminiCommandsDir, 'roles'), { recursive: true });
fs.mkdirSync(path.join(geminiCommandsDir, 'phases'), { recursive: true });

function generateToml(sourceDir, destDir, type) {
    const files = fs.readdirSync(sourceDir).filter(f => f.endsWith('.md'));
    
    for (const file of files) {
        const name = path.basename(file, '.md');
        const sourcePath = path.join(sourceDir, file);
        const tomlPath = path.join(destDir, `${name}.toml`);
        
        const tomlContent = `description = "Adopt the ${name} ${type}"
prompt = """
!{cat ${sourcePath}}

Please apply this ${type} to my following request:
{{args}}
"""
`;
        fs.writeFileSync(tomlPath, tomlContent);
        console.log(`Created TOML for /${type}s:${name}`);
    }
}

generateToml(repoRolesDir, path.join(geminiCommandsDir, 'roles'), 'role');
generateToml(repoPhasesDir, path.join(geminiCommandsDir, 'phases'), 'phase');
```

Run it:
```bash
node setup-gemini.js
rm setup-gemini.js
```
Then, in any active Gemini CLI terminal, type `/commands reload`.

---

## Usage

### In Gemini CLI
Because we placed the TOML files in subdirectories, they are namespaced:
*   `/roles:architect`
*   `/roles:principal-backend-engineer`
*   `/phases:build`
*   `/phases:plan`

**Example:**
> `/roles:principal-frontend-engineer /phases:build Help me implement the UI component defined in the plan.`

### In Antigravity
Because Antigravity doesn't support subdirectories for workflows, the commands appear directly as their filenames:
*   `/architect`
*   `/principal-backend-engineer`
*   `/build`
*   `/plan`

**Example:**
> `/principal-frontend-engineer /build Help me implement the UI component defined in the plan.`

---

## Adding a New Role or Phase

If you want to create a brand new role or phase in the future:

1. **Create the file:** Create `new-role.md` inside the `roles/` (or `phases/`) directory.
2. **Add Frontmatter:** You MUST add YAML frontmatter at the very top for Antigravity to see it:
   ```yaml
   ---
   name: new-role
   description: Adopt the new-role role
   ---
   # Role: New Role
   ...
   ```
3. **Link to Antigravity:**
   ```bash
   ln -sfn $(pwd)/roles/new-role.md ~/.agent/workflows/new-role.md
   ```
4. **Link to Gemini CLI:** Create a `new-role.toml` file in `~/.gemini/commands/roles/` pointing to your new markdown file, using the same `!{cat ...}` format as the others. Run `/commands reload` in the CLI.