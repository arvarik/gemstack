# Gemstack Installation & Setup

## Installation (Setting up on a new computer)

If you clone this repository to a new machine, run the following steps to wire up the slash commands for both Gemini CLI and Antigravity.

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/gemstack.git ~/Documents/github/gemstack
cd ~/Documents/github/gemstack
```

### 2. Setup Antigravity (Global Slash Commands)
Antigravity looks for `.md` files in `~/.agent/workflows/`. It does not currently follow subdirectories or symlinks reliably, so we copy the files directly.

```bash
# Create the global workflows directory
mkdir -p ~/.agent/workflows

# Copy all roles, phases, and composed workflows directly into the workflows folder
cp $(pwd)/roles/*.md ~/.agent/workflows/
cp $(pwd)/phases/*.md ~/.agent/workflows/
cp $(pwd)/workflows/*.md ~/.agent/workflows/
```

### 3. Setup Gemini CLI (Global Slash Commands)
Gemini CLI requires `.toml` definitions in `~/.gemini/commands/`. We use a quick Node.js script to generate these wrappers.

Run this script from the root of the `gemstack` repository:

```javascript
// Save this as setup-gemini.js and run with `node setup-gemini.js`
const fs = require('fs');
const path = require('path');
const os = require('os');

const geminiCommandsDir = path.join(os.homedir(), '.gemini', 'commands');
const repoRolesDir = path.join(process.cwd(), 'roles');
const repoPhasesDir = path.join(process.cwd(), 'phases');
const repoWorkflowsDir = path.join(process.cwd(), 'workflows');

// Ensure directories exist
fs.mkdirSync(path.join(geminiCommandsDir, 'roles'), { recursive: true });
fs.mkdirSync(path.join(geminiCommandsDir, 'phases'), { recursive: true });
fs.mkdirSync(path.join(geminiCommandsDir, 'workflows'), { recursive: true });

function generateToml(sourceDir, destDir, type) {
    if (!fs.existsSync(sourceDir)) return;
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
generateToml(repoWorkflowsDir, path.join(geminiCommandsDir, 'workflows'), 'workflow');
```

Run it:
```bash
node setup-gemini.js
rm setup-gemini.js
```
Then, in any active Gemini CLI terminal, type `/commands reload`.

---

## Bootstrapping a New Project with AI

You do not need to manually fill out the `.agent/` files for a new project. We have automated it:

1. Copy the contents of `gemstack/context/` into the root of your target project:
   ```bash
   # From the root of your target project:
   cp -r /path/to/gemstack/context/.agent .agent
   cp -r /path/to/gemstack/context/docs docs
   cp /path/to/gemstack/context/context_prompt.md context_prompt.md
   cp /path/to/gemstack/context/.env.example .env.example
   ```
   > **Note**: Copy the *contents* of `context/`, not the `context/` directory itself. The `.agent/` and `docs/` folders should live at your project root.

2. In your project, ask your LLM:
   > "Please read `@context_prompt.md` and follow the instructions to bootstrap this project."
3. The LLM will deeply analyze your actual codebase (`package.json`, schemas, `go.mod`, `Makefile`, UI components) and overwrite the `.agent/` templates with concrete, highly specific facts.
4. Once bootstrapped, you can delete `context_prompt.md` from the project — its job is done.
5. Your repo is now aligned with the Gemstack framework and ready for the `/ideate` phase!

---

## Adding a New Role, Phase, or Workflow

If you want to create a brand new role, phase, or composed workflow in the future:

1. **Create the file:** Create `new-file.md` inside the `roles/`, `phases/`, or `workflows/` directory.
2. **Add Frontmatter:** You MUST add YAML frontmatter at the very top for Antigravity to see it:
   ```yaml
   ---
   name: new-file
   description: Adopt the new-file behavior
   ---
   # Title
   ...
   ```
3. **Link to Antigravity:**
   ```bash
   ln -sfn $(pwd)/roles/new-file.md ~/.gemini/antigravity/global_workflows/new-file.md
   ```
4. **Link to Gemini CLI:** Create a `new-file.toml` file in `~/.gemini/commands/roles/` pointing to your new markdown file, using the same `!{cat ...}` format as the others. Run `/commands reload` in the CLI.