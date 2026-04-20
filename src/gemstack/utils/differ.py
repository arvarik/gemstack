"""Context drift detection — compares .agent/ documentation against codebase reality.

Detects when the actual project state has drifted from what's documented
in the .agent/ files, enabling proactive context maintenance.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    """Report of drift between .agent/ docs and actual codebase."""

    new_dependencies: list[str] = field(default_factory=list)
    removed_dependencies: list[str] = field(default_factory=list)
    new_env_vars: list[str] = field(default_factory=list)
    removed_env_vars: list[str] = field(default_factory=list)
    stale_file_refs: list[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        """Whether any drift was detected."""
        return bool(
            self.new_dependencies
            or self.removed_dependencies
            or self.new_env_vars
            or self.removed_env_vars
            or self.stale_file_refs
        )

    def to_markdown(self) -> str:
        """Render the drift report as markdown."""
        if not self.has_drift:
            return "✅ No drift detected. `.agent/` is in sync with the codebase."

        parts = ["# Context Drift Report\n"]

        if self.new_dependencies:
            parts.append("## New Dependencies (not in ARCHITECTURE.md)\n")
            for dep in self.new_dependencies:
                parts.append(f"- `{dep}`")
            parts.append("")

        if self.removed_dependencies:
            parts.append("## Removed Dependencies (still in ARCHITECTURE.md)\n")
            for dep in self.removed_dependencies:
                parts.append(f"- `{dep}`")
            parts.append("")

        if self.new_env_vars:
            parts.append("## New Environment Variables (not in ARCHITECTURE.md)\n")
            for var in self.new_env_vars:
                parts.append(f"- `{var}`")
            parts.append("")

        if self.removed_env_vars:
            parts.append("## Removed Environment Variables (still documented)\n")
            for var in self.removed_env_vars:
                parts.append(f"- `{var}`")
            parts.append("")

        if self.stale_file_refs:
            parts.append("## Stale File References in STATUS.md\n")
            for ref in self.stale_file_refs:
                parts.append(f"- `{ref}`")
            parts.append("")

        return "\n".join(parts)


class ContextDiffer:
    """Detects drift between .agent/ context and actual codebase state.

    Performs three categories of drift analysis:
    1. Dependency drift — new/removed deps vs ARCHITECTURE.md
    2. Environment variable drift — .env.example vs ARCHITECTURE.md
    3. Stale file references — STATUS.md references vs filesystem
    """

    def analyze(
        self,
        project_root: Path,
        *,
        architecture_only: bool = False,
        env_only: bool = False,
    ) -> DriftReport:
        """Scan codebase and compare against .agent/ documentation.

        Args:
            project_root: Path to the project root.
            architecture_only: Only check dependency drift.
            env_only: Only check env variable drift.

        Returns:
            DriftReport with all detected drift items.
        """
        report = DriftReport()
        arch_path = project_root / ".agent" / "ARCHITECTURE.md"
        status_path = project_root / ".agent" / "STATUS.md"

        if not arch_path.exists():
            logger.warning("No .agent/ARCHITECTURE.md found — skipping drift analysis")
            return report

        arch_content = arch_path.read_text()

        if not env_only:
            self._check_dependency_drift(project_root, arch_content, report)

        if not architecture_only:
            self._check_env_drift(project_root, arch_content, report)

        if not architecture_only and not env_only and status_path.exists():
            self._check_stale_refs(project_root, status_path, report)

        return report

    def _check_dependency_drift(self, root: Path, arch_content: str, report: DriftReport) -> None:
        """Compare actual dependencies against ARCHITECTURE.md documentation."""
        actual_deps = self._extract_actual_deps(root)
        documented_deps = self._extract_documented_deps(arch_content)

        if not actual_deps and not documented_deps:
            return

        # Normalize for comparison (lowercase, strip whitespace)
        actual_normalized = {d.lower().strip() for d in actual_deps}
        documented_normalized = {d.lower().strip() for d in documented_deps}

        report.new_dependencies = sorted(actual_normalized - documented_normalized)
        report.removed_dependencies = sorted(documented_normalized - actual_normalized)

    def _check_env_drift(self, root: Path, arch_content: str, report: DriftReport) -> None:
        """Compare .env.example variables against ARCHITECTURE.md documentation."""
        actual_vars = self._extract_env_vars(root)
        documented_vars = self._extract_documented_env_vars(arch_content)

        if not actual_vars and not documented_vars:
            return

        report.new_env_vars = sorted(actual_vars - documented_vars)
        report.removed_env_vars = sorted(documented_vars - actual_vars)

    def _check_stale_refs(self, root: Path, status_path: Path, report: DriftReport) -> None:
        """Check if file references in STATUS.md still exist."""
        content = status_path.read_text()

        # Scope to ## Relevant Files section
        section_match = re.search(
            r"##\s*Relevant Files\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL,
        )
        if not section_match:
            return

        section = section_match.group(1)
        for match in re.finditer(r"[-*]\s*`?([^\s`]+)`?", section):
            filepath = match.group(1).strip()
            if (
                filepath
                and not filepath.startswith(("(", "_", "#"))
                and not (root / filepath).exists()
            ):
                report.stale_file_refs.append(filepath)

    # --- Extractors ---

    def _extract_actual_deps(self, root: Path) -> set[str]:
        """Extract actual dependencies from manifest files."""
        deps: set[str] = set()

        # Node.js
        pkg_json = root / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text())
                for key in ("dependencies", "devDependencies"):
                    deps.update(data.get(key, {}).keys())
            except (json.JSONDecodeError, OSError):
                pass

        # Python
        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            try:
                import sys

                if sys.version_info >= (3, 11):
                    import tomllib
                else:
                    import tomli as tomllib
                data = tomllib.loads(pyproject.read_text())
                for dep_str in data.get("project", {}).get("dependencies", []):
                    name = re.split(r"[>=<!~\[\s]", dep_str)[0].strip().lower()
                    if name:
                        deps.add(name)
            except Exception:  # noqa: S110
                pass

        # Go
        go_mod = root / "go.mod"
        if go_mod.exists():
            try:
                content = go_mod.read_text()
                for match in re.finditer(r"^\s+(\S+)\s+v", content, re.MULTILINE):
                    deps.add(match.group(1))
            except OSError:
                pass

        return deps

    def _extract_documented_deps(self, arch_content: str) -> set[str]:
        """Extract dependency names mentioned in ARCHITECTURE.md.

        Looks for deps in markdown tables, bullet lists with backticks,
        and the Tech Stack section.
        """
        deps: set[str] = set()

        # Match backtick-quoted dependency names in table rows or bullet points
        # Pattern: | `dep-name` | or - `dep-name`
        for match in re.finditer(r"[|*-]\s*`([^`]+)`", arch_content):
            candidate = match.group(1).strip()
            # Filter out non-dependency items (file paths, commands, etc.)
            if "/" not in candidate and " " not in candidate and not candidate.startswith("."):
                deps.add(candidate.lower())

        return deps

    def _extract_env_vars(self, root: Path) -> set[str]:
        """Extract variable names from .env.example or .env.sample."""
        for name in (".env.example", ".env.sample", ".env.template"):
            path = root / name
            if path.exists():
                try:
                    content = path.read_text()
                    return {
                        match.group(1)
                        for match in re.finditer(r"^([A-Z_][A-Z0-9_]*)=", content, re.MULTILINE)
                    }
                except OSError:
                    pass
        return set()

    def _extract_documented_env_vars(self, arch_content: str) -> set[str]:
        """Extract env var names from ARCHITECTURE.md.

        Looks for patterns like `DATABASE_URL` in environment sections.
        """
        env_vars: set[str] = set()

        # Look for environment variable patterns in backticks
        for match in re.finditer(r"`([A-Z_][A-Z0-9_]*)`", arch_content):
            candidate = match.group(1)
            # Only include things that look like env vars (ALL_CAPS_WITH_UNDERSCORES)
            if re.match(r"^[A-Z][A-Z0-9_]{2,}$", candidate):
                env_vars.add(candidate)

        return env_vars
