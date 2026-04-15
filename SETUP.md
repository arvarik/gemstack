# Gemstack Installation & Setup

## Prerequisites

- **Antigravity** or **Gemini CLI** installed and configured
- Git
- Node.js (only needed if setting up Gemini CLI commands via the TOML generator script)

---

## Installation (Setting Up on a New Machine)

If you clone this repository to a new machine, run the following steps to wire up the global slash commands for both Antigravity and Gemini CLI.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/gemstack.git ~/Documents/github/gemstack
cd ~/Documents/github/gemstack
```

### 2. Set Up Antigravity Global Slash Commands

Antigravity discovers global workflows from `~/.gemini/antigravity/global_workflows/`. We **symlink** (not copy) the source files into this directory so that edits to gemstack propagate instantly.

```bash
# Create the global workflows directory if it doesn't exist
mkdir -p ~/.gemini/antigravity/global_workflows

# Symlink all roles (9 files)
for f in $(pwd)/roles/*.md; do
  ln -sfn "$f" ~/.gemini/antigravity/global_workflows/$(basename "$f")
done

# Symlink all phases (10 files)
for f in $(pwd)/phases/*.md; do
  ln -sfn "$f" ~/.gemini/antigravity/global_workflows/$(basename "$f")
done

# Symlink all composed workflows (5 files)
for f in $(pwd)/workflows/*.md; do
  ln -sfn "$f" ~/.gemini/antigravity/global_workflows/$(basename "$f")
done

# Symlink all topology profiles (6 files)
for f in $(pwd)/topologies/*.md; do
  ln -sfn "$f" ~/.gemini/antigravity/global_workflows/$(basename "$f")
done
```

**Why symlinks?** If you copy the files, changes to gemstack won't propagate to the global workflows directory. Symlinks ensure you edit once, see the update everywhere.

**Verify it worked:**
```bash
ls -la ~/.gemini/antigravity/global_workflows/
# Every file should show -> /path/to/gemstack/roles|phases|workflows|topologies/filename.md
```

> **Important:** Every `.md` file in `roles/`, `phases/`, `workflows/`, and `topologies/` **must** have YAML frontmatter at the top for Antigravity to register it as a slash command:
> ```yaml
> ---
> name: role-or-phase-name
> description: Short description of what this command does
> ---
> ```

### 3. Set Up Gemini CLI Commands (Optional)

Gemini CLI requires `.toml` definitions in `~/.gemini/commands/`. This script generates TOML wrappers that point to your gemstack source files.

Save this as `setup-gemini.js` in the gemstack root and run with `node setup-gemini.js`:

```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

const geminiCommandsDir = path.join(os.homedir(), '.gemini', 'commands');
const dirs = {
  roles: path.join(process.cwd(), 'roles'),
  phases: path.join(process.cwd(), 'phases'),
  workflows: path.join(process.cwd(), 'workflows'),
  topologies: path.join(process.cwd(), 'topologies'),
};

for (const [type, sourceDir] of Object.entries(dirs)) {
  const destDir = path.join(geminiCommandsDir, type);
  fs.mkdirSync(destDir, { recursive: true });

  if (!fs.existsSync(sourceDir)) continue;
  const files = fs.readdirSync(sourceDir).filter(f => f.endsWith('.md'));

  for (const file of files) {
    const name = path.basename(file, '.md');
    const sourcePath = path.join(sourceDir, file);
    const tomlPath = path.join(destDir, `${name}.toml`);

    const tomlContent = `description = "Adopt the ${name} ${type.replace(/s$/, '')}"\nprompt = """\n!{cat ${sourcePath}}\n\nPlease apply this ${type.replace(/s$/, '')} to my following request:\n{{args}}\n"""\n`;
    fs.writeFileSync(tomlPath, tomlContent);
    console.log(`Created TOML for /${type}/${name}`);
  }
}
```

Run it:
```bash
node setup-gemini.js
rm setup-gemini.js
```

Then, in any active Gemini CLI terminal, type `/commands reload`.

---

## Bootstrapping a New Project with AI

You do not need to manually fill out the `.agent/` context files for a new project. Gemstack includes an AI-powered bootstrapping script that deeply analyzes your codebase and populates the templates with concrete, project-specific facts.

### Steps

1. **Copy the templates** from `gemstack/context/` into the root of your target project:
   ```bash
   # From the root of your target project:
   cp -r /path/to/gemstack/context/.agent .agent
   cp -r /path/to/gemstack/context/docs docs
   cp /path/to/gemstack/context/context_prompt.md context_prompt.md
   cp /path/to/gemstack/context/.env.example .env.example
   ```
   > **Note:** Copy the *contents* of `context/`, not the `context/` directory itself. The `.agent/` and `docs/` folders should live at your project root.

2. **Run the bootstrapping prompt.** In your project, ask your LLM:
   > "Please read `@context_prompt.md` and follow the instructions to bootstrap this project."

3. **What the LLM does:** It deeply analyzes your actual codebase (`package.json`, `go.mod`, schemas, `Makefile`, UI components, `.env.example`, etc.) and overwrites the `.agent/` templates with highly specific facts. This includes:
   - Detecting the project topology (`[frontend]`, `[backend, ml-ai]`, etc.)
   - Mapping the tech stack with pinned versions
   - Documenting API contracts and database schemas
   - Extracting style rules, anti-patterns, and naming conventions
   - Setting up test matrices based on active topologies
   - Absorbing any legacy context files (`.cursorrules`, `GEMINI.md`, `CLAUDE.md`)

4. **Clean up.** Once bootstrapped, delete `context_prompt.md` from the project — its job is done.

5. **Your repo is now Gemstack-aligned** and ready for the `/ideate` phase.

### What Gets Created

After bootstrapping, your project will have:

```text
.agent/
├── ARCHITECTURE.md     # Includes ## 0. Project Topology, tech stack, API contracts,
│                       # data models, env vars, and dev commands
├── STYLE.md            # Design system tokens, code patterns, anti-patterns (FORBIDDEN)
├── TESTING.md          # Test commands, scenario tables, topology-specific matrices
├── PHILOSOPHY.md       # Product soul, core beliefs, anti-goals
└── STATUS.md           # Initialized to "Project Bootstrapped", lifecycle checkboxes

docs/
├── explorations/       # Ready for ideate phase output
├── designs/            # Ready for design phase output
├── plans/              # Ready for plan phase output
└── archive/            # Ready for shipped feature docs

.env.example            # All env vars with placeholder values and comments
```

---

## Topology Migration (Existing Projects)

If you have existing projects that were bootstrapped before the topology system was added, use the [Gemstack Topology Migration Guide](../gemstack_migration.md) to upgrade them. The migration adds three things per repo:

1. `## 0. Project Topology` declaration in `ARCHITECTURE.md`
2. Topology-specific testing matrices in `TESTING.md` (Route Coverage, State Matrix, Eval Thresholds)
3. Topology-specific tracking sections in `STATUS.md` (Stub Tracker, Prompt Changelog)

The migration guide provides self-contained, copy-pasteable prompts for each of the 8 repositories being migrated.

---

## Adding a New Role, Phase, Workflow, or Topology

1. **Create the source file.** Create `new-file.md` inside the appropriate directory (`roles/`, `phases/`, `workflows/`, or `topologies/`).

2. **Add YAML frontmatter** at the very top of the file. This is required for Antigravity to register it as a slash command:
   ```yaml
   ---
   name: new-file
   description: Short description of what this command does
   ---
   # Title
   ...
   ```

3. **Symlink to Antigravity global workflows:**
   ```bash
   ln -sfn $(pwd)/roles/new-file.md ~/.gemini/antigravity/global_workflows/new-file.md
   ```
   Replace `roles/` with the appropriate directory (`phases/`, `workflows/`, or `topologies/`).

4. **For Gemini CLI:** Create a `new-file.toml` in `~/.gemini/commands/roles/` (or appropriate subdirectory) using the same `!{cat ...}` format as the others. Run `/commands reload` in the CLI.

5. **Commit to gemstack.** The source file lives in this repo. The symlink makes it globally available.

---

## Quick Reference

| What | Where | Count |
|------|-------|-------|
| Role definitions | `roles/*.md` | 9 |
| Phase definitions | `phases/*.md` | 10 |
| Composed workflows | `workflows/*.md` | 5 |
| Topology profiles | `topologies/*.md` | 6 |
| Context templates | `context/` | 7 files + dirs |
| Global distribution | `~/.gemini/antigravity/global_workflows/` | 30 symlinks |
| Migration guide | `../gemstack_migration.md` | 8 repo prompts |