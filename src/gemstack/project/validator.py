"""Project validator — .agent/ directory integrity checking."""

import re
from dataclasses import dataclass, field
from pathlib import Path

from gemstack.errors import ValidationError


@dataclass
class ValidationResult:
    """Result of project validation."""

    passed: bool
    errors: list[str] = field(default_factory=list)  # Blocking issues
    warnings: list[str] = field(default_factory=list)  # Non-blocking suggestions
    fixes_applied: int = 0  # If --fix was used


class ProjectValidator:
    """Validates .agent/ directory integrity.

    Includes checks for required files, Docs lifecycles, and topology configurations.
    """

    REQUIRED_FILES = [
        "ARCHITECTURE.md",
        "STYLE.md",
        "TESTING.md",
        "PHILOSOPHY.md",
        "STATUS.md",
    ]

    def validate(self, project_root: Path, auto_fix: bool = False) -> ValidationResult:
        """Validate the project's .agent/ directory.

        Checks:
        1. All 5 required .agent/ files exist
        2. ARCHITECTURE.md has a valid topology declaration
        3. STATUS.md has a valid [STATE: ...] enum
        4. docs/ lifecycle directories exist
        5. Plugin-provided checks
        6. Stale file references in STATUS.md
        """
        project_root = project_root.resolve()
        errors: list[str] = []
        warnings: list[str] = []
        fixes = 0
        agent_dir = project_root / ".agent"

        if not agent_dir.exists():
            raise ValidationError(
                "No .agent/ directory found.",
                suggestion="Run `gemstack init` to initialize this project.",
            )

        # Check 1: Required files
        for filename in self.REQUIRED_FILES:
            if not (agent_dir / filename).exists():
                errors.append(f"Missing required file: .agent/{filename}")

        # Check 2: docs/ directories
        for dirname in ["explorations", "designs", "plans", "archive"]:
            docs_dir = project_root / "docs" / dirname
            if not docs_dir.exists():
                if auto_fix:
                    docs_dir.mkdir(parents=True, exist_ok=True)
                    (docs_dir / ".gitkeep").touch()
                    fixes += 1
                else:
                    warnings.append(f"Missing directory: docs/{dirname}/ (fix with --fix)")

        # Check 3: STATUS.md check
        status_path = agent_dir / "STATUS.md"
        if status_path.exists():
            content = status_path.read_text()
            if not re.search(r"\[STATE:\s*\w+\]", content):
                suggested = self._suggest_state(content)
                warnings.append(
                    f"STATUS.md missing [STATE: ...] declaration (suggested: {suggested})"
                )

            relevant = self._extract_relevant_files(content)
            for filepath in relevant:
                if not (project_root / filepath).exists():
                    warnings.append(f"Stale reference in STATUS.md: {filepath}")

        # Check 4: ARCHITECTURE.md has topology
        arch_path = agent_dir / "ARCHITECTURE.md"
        if arch_path.exists():
            content = arch_path.read_text()
            if "Topology" not in content:
                warnings.append("ARCHITECTURE.md missing topology declaration")

        # Check 5: Plugin-registered custom checks
        from gemstack.plugins import fire_register_checks

        plugin_errors = fire_register_checks(project_root)
        errors.extend(plugin_errors)

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixes_applied=fixes,
        )

    def _extract_relevant_files(self, content: str) -> list[str]:
        """Parse the Relevant Files section from STATUS.md content.

        Only scans the '## Relevant Files' section and filters out:
        - Single characters (|, [, ], -, *)
        - Markdown syntax (##, **)
        - Non-path-like items (must contain '.' or '/')
        """
        # Scope to ## Relevant Files section
        section_match = re.search(
            r"##\s*Relevant Files\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL,
        )
        if not section_match:
            return []

        section = section_match.group(1)
        refs: list[str] = []
        for match in re.finditer(r"[-*]\s+`([^`]+)`", section):
            filepath = match.group(1).strip()
            # Filter: must look like a file path (contain . or /)
            if (
                filepath
                and len(filepath) > 1
                and ("." in filepath or "/" in filepath)
                and not filepath.startswith(("#", "**"))
            ):
                refs.append(filepath)
        return refs

    @staticmethod
    def _suggest_state(content: str) -> str:
        """Suggest a STATE enum based on STATUS.md content heuristics.

        Precedence: IN_PROGRESS > SHIPPED > INITIALIZED.
        The SHIPPED check requires strong signals (not just the word "release"
        which appears in "## Release History" headings).
        """
        lower = content.lower()
        # Check active-work signals first — they take precedence
        if "in progress" in lower or "in_progress" in lower or "todo" in lower:
            return "IN_PROGRESS"
        # Require strong shipped signals — not bare "release" (matches headings)
        if "shipped" in lower or "released v" in lower or "[state: shipped]" in lower:
            return "SHIPPED"
        return "INITIALIZED"
