"""Project detector module — tech stack and topology detection.

Analyzes a project's filesystem to produce a structured ProjectProfile,
including language, framework, topology, legacy files, and inferred commands.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class Topology(str, Enum):
    """Supported project topology types."""

    BACKEND = "backend"
    FRONTEND = "frontend"
    ML_AI = "ml-ai"
    INFRASTRUCTURE = "infrastructure"
    LIBRARY_SDK = "library-sdk"


@dataclass
class ProjectProfile:
    """Complete profile of a detected project."""

    name: str
    root: Path
    topologies: list[Topology] = field(default_factory=list)

    # Tech stack
    language: str = "unknown"
    runtime: str | None = None  # node, deno, bun, cpython
    framework: str | None = None  # next, vite, fastapi, chi, flask
    package_manager: str | None = None  # npm, pnpm, pip, poetry, uv, go mod

    # Detected files
    manifest_file: Path | None = None  # package.json, pyproject.toml, go.mod
    config_files: list[Path] = field(default_factory=list)
    env_file: Path | None = None  # .env.example
    test_config: Path | None = None  # vitest.config, pytest.ini

    # Legacy context
    legacy_files: list[Path] = field(default_factory=list)
    existing_agent_dir: bool = False

    # Structure
    source_dirs: list[Path] = field(default_factory=list)
    has_database: bool = False
    has_tests: bool = False
    has_ci: bool = False

    # Inferred commands
    dev_command: str | None = None
    test_command: str | None = None
    build_command: str | None = None
    lint_command: str | None = None


# --- Dependency keywords for topology inference ---

_FRONTEND_NODE_DEPS = frozenset({
    "react", "react-dom", "next", "vue", "nuxt", "svelte", "@sveltejs/kit",
    "solid-js", "astro", "angular", "@angular/core", "vite",
})

_BACKEND_NODE_DEPS = frozenset({
    "express", "fastify", "hono", "koa", "nestjs", "@nestjs/core",
    "hapi", "@hapi/hapi",
})

_MLAI_NODE_DEPS = frozenset({
    "@google/genai", "openai", "anthropic", "langchain", "@langchain/core",
    "ai", "@ai-sdk/openai",
})

_BACKEND_PYTHON_DEPS = frozenset({
    "fastapi", "flask", "django", "starlette", "litestar", "sanic",
    "uvicorn", "gunicorn",
})

_MLAI_PYTHON_DEPS = frozenset({
    "google-genai", "openai", "anthropic", "langchain", "langchain-core",
    "torch", "tensorflow", "transformers", "scikit-learn", "keras",
    "huggingface-hub", "datasets", "accelerate", "vllm",
})

_BACKEND_GO_DEPS = frozenset({
    "github.com/go-chi/chi", "github.com/gin-gonic/gin",
    "github.com/labstack/echo", "github.com/gofiber/fiber",
    "github.com/gorilla/mux",
})

_LEGACY_CONTEXT_FILES = [
    ".cursorrules", "GEMINI.md", "CLAUDE.md", "AGENTS.md",
]

_CONFIG_GLOBS = [
    "tsconfig.json", "vite.config.*", "next.config.*",
    "tailwind.config.*", "Dockerfile", "docker-compose.yml",
    "docker-compose.yaml", ".eslintrc*", "biome.json",
    ".prettierrc*", "Makefile", ".golangci.yml", "sqlc.yaml",
]


class ProjectDetector:
    """Analyzes a project's filesystem and produces a ProjectProfile.

    Detection Strategy (ordered by priority):
    1. package.json → Node.js project
    2. pyproject.toml / setup.py → Python project
    3. go.mod → Go project
    4. Cargo.toml → Rust project
    5. docker-compose.yml without application code → infrastructure
    6. File extension scan as fallback
    """

    def detect(self, project_root: Path) -> ProjectProfile:
        """Detect the project profile from the filesystem.

        Must not crash on malformed manifests — all parsing is
        wrapped in try/except for robustness.
        """
        project_root = project_root.resolve()
        profile = ProjectProfile(name=project_root.name, root=project_root)

        logger.debug(f"Scanning {project_root} for project indicators")

        # Detect manifest and language
        self._detect_node(project_root, profile)
        self._detect_python(project_root, profile)
        self._detect_go(project_root, profile)
        self._detect_rust(project_root, profile)

        # Infrastructure detection (only if no app code detected)
        if profile.language == "unknown":
            self._detect_infrastructure(project_root, profile)

        # Detect legacy context files
        self._detect_legacy(project_root, profile)

        # Detect config files, env, tests, CI
        self._detect_config_files(project_root, profile)
        self._detect_env(project_root, profile)
        self._detect_tests(project_root, profile)
        self._detect_ci(project_root, profile)
        self._detect_database(project_root, profile)

        # Check for existing .agent/ directory
        profile.existing_agent_dir = (project_root / ".agent").exists()

        # Infer source directories
        self._detect_source_dirs(project_root, profile)

        logger.info(
            f"Detected: language={profile.language}, "
            f"framework={profile.framework}, "
            f"topologies={[t.value for t in profile.topologies]}"
        )

        return profile

    # --- Language-specific detectors ---

    def _detect_node(self, root: Path, profile: ProjectProfile) -> None:
        """Detect Node.js projects from package.json."""
        pkg_json = root / "package.json"
        if not pkg_json.exists():
            return

        try:
            data = json.loads(pkg_json.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Malformed package.json: {e}")
            # Still mark as Node.js even if parsing fails
            profile.language = "typescript"
            profile.manifest_file = pkg_json
            return

        profile.manifest_file = pkg_json
        profile.language = "typescript" if (root / "tsconfig.json").exists() else "javascript"
        profile.runtime = "node"

        # Detect package manager
        if (root / "pnpm-lock.yaml").exists():
            profile.package_manager = "pnpm"
        elif (root / "yarn.lock").exists():
            profile.package_manager = "yarn"
        elif (root / "bun.lockb").exists():
            profile.package_manager = "bun"
            profile.runtime = "bun"
        else:
            profile.package_manager = "npm"

        # Collect all dependencies
        all_deps: set[str] = set()
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            all_deps.update(data.get(key, {}).keys())

        # Framework detection
        if "next" in all_deps:
            profile.framework = "next"
        elif "nuxt" in all_deps:
            profile.framework = "nuxt"
        elif "@sveltejs/kit" in all_deps:
            profile.framework = "sveltekit"
        elif "vite" in all_deps:
            profile.framework = "vite"

        # Topology inference
        if all_deps & _FRONTEND_NODE_DEPS:
            profile.topologies.append(Topology.FRONTEND)
            logger.debug("Detected frontend topology from Node.js deps")

        if all_deps & _BACKEND_NODE_DEPS:
            profile.topologies.append(Topology.BACKEND)
            logger.debug("Detected backend topology from Node.js deps")

        if all_deps & _MLAI_NODE_DEPS:
            profile.topologies.append(Topology.ML_AI)
            logger.debug("Detected ML/AI topology from Node.js deps")

        # Infer commands from scripts
        scripts = data.get("scripts", {})
        if "dev" in scripts:
            profile.dev_command = f"{profile.package_manager} run dev"
        elif "start" in scripts:
            profile.dev_command = f"{profile.package_manager} run start"

        if "test" in scripts:
            profile.test_command = f"{profile.package_manager} test"

        if "build" in scripts:
            profile.build_command = f"{profile.package_manager} run build"

        if "lint" in scripts:
            profile.lint_command = f"{profile.package_manager} run lint"

    def _detect_python(self, root: Path, profile: ProjectProfile) -> None:
        """Detect Python projects from pyproject.toml or setup.py."""
        pyproject = root / "pyproject.toml"
        setup_py = root / "setup.py"

        if not pyproject.exists() and not setup_py.exists():
            return

        # Don't override Node.js detection
        if profile.language != "unknown":
            return

        profile.language = "python"
        profile.runtime = "cpython"

        if pyproject.exists():
            profile.manifest_file = pyproject
            self._parse_pyproject(pyproject, profile)
        elif setup_py.exists():
            profile.manifest_file = setup_py
            # setup.py parsing is minimal — just detect python
            profile.package_manager = "pip"

    def _parse_pyproject(self, pyproject: Path, profile: ProjectProfile) -> None:
        """Parse pyproject.toml for dependencies and tools."""
        import sys

        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib

        try:
            data = tomllib.loads(pyproject.read_text())
        except Exception as e:
            logger.warning(f"Malformed pyproject.toml: {e}")
            return

        # Detect package manager
        build_backend = data.get("build-system", {}).get("build-backend", "")
        if "hatch" in build_backend:
            profile.package_manager = "uv"  # Hatch projects often use uv
        elif "poetry" in build_backend:
            profile.package_manager = "poetry"
        elif "flit" in build_backend:
            profile.package_manager = "flit"
        else:
            profile.package_manager = "pip"

        # Check for uv
        if (profile.root / "uv.lock").exists():
            profile.package_manager = "uv"

        # Parse dependencies for topology inference
        dep_names: set[str] = set()
        for dep_str in data.get("project", {}).get("dependencies", []):
            name = re.split(r"[>=<!~\[\s]", dep_str)[0].strip().lower()
            if name:
                dep_names.add(name)

        # Also check optional dependencies
        for extra_deps in data.get("project", {}).get("optional-dependencies", {}).values():
            for dep_str in extra_deps:
                name = re.split(r"[>=<!~\[\s]", dep_str)[0].strip().lower()
                if name:
                    dep_names.add(name)

        # Framework detection
        if "fastapi" in dep_names:
            profile.framework = "fastapi"
        elif "flask" in dep_names:
            profile.framework = "flask"
        elif "django" in dep_names:
            profile.framework = "django"

        # Topology inference
        if dep_names & _BACKEND_PYTHON_DEPS:
            profile.topologies.append(Topology.BACKEND)

        if dep_names & _MLAI_PYTHON_DEPS:
            profile.topologies.append(Topology.ML_AI)

        # Infer commands
        scripts = data.get("project", {}).get("scripts", {})
        if scripts:
            first_script = next(iter(scripts.keys()))
            if profile.package_manager == "uv":
                profile.dev_command = f"uv run {first_script}"
            else:
                profile.dev_command = f"python -m {first_script}"

        # Check for tool configs
        if "tool" in data:
            tools = data["tool"]
            if "pytest" in tools or "pytest.ini_options" in tools.get("pytest", {}):
                profile.test_command = (
                    "uv run pytest" if profile.package_manager == "uv" else "pytest"
                )
            if "ruff" in tools:
                profile.lint_command = (
                    "uv run ruff check ." if profile.package_manager == "uv" else "ruff check ."
                )
            if "mypy" in tools:
                lint = profile.lint_command or ""
                mypy_cmd = "uv run mypy ." if profile.package_manager == "uv" else "mypy ."
                profile.lint_command = f"{lint} && {mypy_cmd}" if lint else mypy_cmd

    def _detect_go(self, root: Path, profile: ProjectProfile) -> None:
        """Detect Go projects from go.mod."""
        go_mod = root / "go.mod"
        if not go_mod.exists():
            return

        if profile.language != "unknown":
            return

        profile.language = "go"
        profile.runtime = "go"
        profile.manifest_file = go_mod
        profile.package_manager = "go mod"

        try:
            content = go_mod.read_text()
        except OSError as e:
            logger.warning(f"Failed to read go.mod: {e}")
            return

        # Check for backend frameworks
        for dep in _BACKEND_GO_DEPS:
            if dep in content:
                profile.topologies.append(Topology.BACKEND)
                # Extract framework name from path
                profile.framework = dep.split("/")[-1]
                break

        # Check for cmd/ directory (indicates a backend service)
        if (root / "cmd").is_dir() and Topology.BACKEND not in profile.topologies:
            profile.topologies.append(Topology.BACKEND)

        # Check for internal/ (library pattern if no cmd/)
        if (root / "pkg").is_dir() and not (root / "cmd").is_dir():
            profile.topologies.append(Topology.LIBRARY_SDK)

        # Infer commands
        if (root / "Makefile").exists():
            profile.dev_command = "make run"
            profile.test_command = "go test -race ./..."
            profile.build_command = "make build"
            profile.lint_command = "golangci-lint run"
        else:
            profile.test_command = "go test -race ./..."
            profile.build_command = "go build ./..."
            profile.lint_command = "go vet ./..."

    def _detect_rust(self, root: Path, profile: ProjectProfile) -> None:
        """Detect Rust projects from Cargo.toml."""
        cargo_toml = root / "Cargo.toml"
        if not cargo_toml.exists():
            return

        if profile.language != "unknown":
            return

        profile.language = "rust"
        profile.runtime = "rust"
        profile.manifest_file = cargo_toml
        profile.package_manager = "cargo"
        profile.test_command = "cargo test"
        profile.build_command = "cargo build"
        profile.lint_command = "cargo clippy"

    def _detect_infrastructure(self, root: Path, profile: ProjectProfile) -> None:
        """Detect infrastructure-only projects."""
        compose_files = list(root.glob("docker-compose.y*ml"))
        terraform = list(root.glob("*.tf"))
        k8s = (root / "k8s").is_dir() or (root / "kubernetes").is_dir()

        if compose_files or terraform or k8s:
            profile.topologies.append(Topology.INFRASTRUCTURE)
            profile.language = "yaml"
            if compose_files:
                profile.manifest_file = compose_files[0]

    # --- Supporting detectors ---

    def _detect_legacy(self, root: Path, profile: ProjectProfile) -> None:
        """Detect legacy context files that can be absorbed."""
        for filename in _LEGACY_CONTEXT_FILES:
            path = root / filename
            if path.exists():
                profile.legacy_files.append(path)
                logger.info(f"Detected legacy context file: {filename}")

    def _detect_config_files(self, root: Path, profile: ProjectProfile) -> None:
        """Detect config files in the project root."""
        for pattern in _CONFIG_GLOBS:
            for match in root.glob(pattern):
                if match.is_file():
                    profile.config_files.append(match)

    def _detect_env(self, root: Path, profile: ProjectProfile) -> None:
        """Detect .env.example file."""
        for name in [".env.example", ".env.sample", ".env.template"]:
            path = root / name
            if path.exists():
                profile.env_file = path
                break

    def _detect_tests(self, root: Path, profile: ProjectProfile) -> None:
        """Detect test infrastructure."""
        test_dirs = ["tests", "test", "__tests__", "spec"]
        for d in test_dirs:
            if (root / d).is_dir():
                profile.has_tests = True
                break

        # Test config files
        test_configs = [
            "vitest.config.ts", "vitest.config.js", "jest.config.ts", "jest.config.js",
            "pytest.ini", "conftest.py", "playwright.config.ts",
        ]
        for cfg in test_configs:
            path = root / cfg
            if path.exists():
                profile.test_config = path
                profile.has_tests = True
                break

    def _detect_ci(self, root: Path, profile: ProjectProfile) -> None:
        """Detect CI configuration."""
        ci_paths = [
            root / ".github" / "workflows",
            root / ".gitlab-ci.yml",
            root / ".circleci",
            root / "Jenkinsfile",
        ]
        profile.has_ci = any(p.exists() for p in ci_paths)

    def _detect_database(self, root: Path, profile: ProjectProfile) -> None:
        """Detect database usage."""
        db_indicators = [
            root / "prisma" / "schema.prisma",
            root / "migrations",
            root / "alembic.ini",
            root / "drizzle.config.ts",
        ]
        profile.has_database = any(p.exists() for p in db_indicators)

    def _detect_source_dirs(self, root: Path, profile: ProjectProfile) -> None:
        """Detect source code directories."""
        candidates = ["src", "lib", "app", "cmd", "internal", "pkg", "server", "api"]
        for d in candidates:
            path = root / d
            if path.is_dir():
                profile.source_dirs.append(path)
