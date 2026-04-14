# Gemstack: Agentic Development Framework

A complete framework for standardizing AI Agent orchestration across all your software projects. Whether you are using Gemini CLI, Antigravity, Claude Code, or any LLM-based coding tool, Gemstack defines a unified system of composable **roles** (how the agent thinks), **phases** (what process the agent follows), and **project context** (the boundaries and rules of the specific codebase).

This repository serves as your **single source of truth**. By defining roles, phases, and templates here, you ensure consistent, high-quality, and non-hallucinated AI output across multiple projects and tech stacks. 

## Directory Structure

*   `roles/`: Contains markdown files defining agent mindsets (e.g., `architect.md`, `product-visionary.md`).
*   `phases/`: Contains markdown files defining the workflow steps (e.g., `plan.md`, `build.md`).
*   `context/`: Contains the master templates for project-specific rules (e.g., `ARCHITECTURE.md`, `STYLE.md`, `TESTING.md`) and the AI bootstrapping script.
*   `roles_phases.md`: The original master document containing all definitions.

---

## 1. Global Skills: Roles & Phases

The `roles/` and `phases/` folders act as global commands. You edit the markdown files here, and they become instantly available as slash commands (`/`) in both **Gemini CLI** and **Antigravity**.

### How It Works
*   **Antigravity:** Uses the `.md` files directly via symlinks. It requires a YAML frontmatter block (e.g., `--- name: architect ---`) at the top of each file.
*   **Gemini CLI:** Uses `.toml` wrappers that dynamically read (inject) the contents of your `.md` files using the `!{cat ...}` shell command.

Because both tools reference the files in this repository, **any edits you make to the files in `roles/` or `phases/` will instantly apply globally across all your projects.**

### Usage Example
In Gemini CLI (namespaced):
> `/roles:principal-frontend-engineer /phases:build Help me implement the UI component defined in the plan.`

In Antigravity (flat):
> `/principal-frontend-engineer /build Help me implement the UI component defined in the plan.`

---

## 2. Project Boundaries: The `.agent/` Context

While roles and phases are global, every project has unique rules (tech stack, CSS tokens, database constraints). The `context/` folder in this repository solves the "context drift" problem by providing a standardized `.agent/` directory for all your repos.

### The Standardized Structure
Every repository you build should contain this structure at its root:
```text
.agent/
├── STATUS.md           # where we are, what to do next, relevant file pointers
├── ARCHITECTURE.md     # how the system is built, data models, API contracts
├── STYLE.md            # code and visual patterns, explicit anti-patterns
├── TESTING.md          # test methods, scenarios, results with evidence
└── PHILOSOPHY.md       # product soul - why this exists, core beliefs

.env.example            # all required env vars with placeholder values and comments

docs/
├── explorations/       # ideate phase output
├── designs/            # design phase output
├── plans/              # plan phase output
└── archive/            # shipped feature docs
```

### Feature Lifecycle Flow
```
ideate --> design --> plan --> build --> test ----> review --> ship
                       ^        ^         |          |
                       |        |         v          |
                       |        +------ fix  <-------+ (localized bugs)
                       |        (scoped bug fixes
                       |         return to test)
                       |                             |
                       +-----------------------------+ (architectural issues
                        (structural problems go back    skip fix, return to
                         to plan + build, not fix)      plan + build)
```

### Role x Phase Matrix
*(📝 = Produces/Updates Markdown files | 💻 = Produces/Modifies Code or Infra)*

| Role | Ideate | Design | Plan | Build | Fix | Test | Review | Ship |
|---|---|---|---|---|---|---|---|---|
| Product Visionary | 📝 Primary | | | | | | 📝 Periodic | |
| UI/UX Designer | 📝 Secondary | 📝 Primary | | | | | | |
| Architect | | 📝 Primary | 📝 Advisory | | | | 📝 Primary | |
| Backend Engineer | 📝 Secondary | 📝 Secondary | 📝 Primary | 💻 Primary | 💻 Primary | | | |
| Frontend Engineer | 📝 Secondary | 📝 Secondary | 📝 Primary | 💻 Primary | 💻 Primary | | | |
| ML Engineer | 📝 Secondary | 📝 Primary | 📝 Primary | 💻 Primary | 💻 Primary | 💻/📝 Primary | | |
| QA Engineer | | | | | | 💻/📝 Primary | | |
| Security Engineer | | | | | | | 📝 Primary | 📝 Advisory |
| DevOps Engineer | | | | | | | | 💻 Primary |

### Bootstrapping a New Project with AI
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