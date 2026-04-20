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
                warnings.append("STATUS.md missing [STATE: ...] declaration")

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
        """Parse the Relevant Files section from STATUS.md content."""
        return re.findall(r"[-*]\s+`?([^\s`]+)`?", content)
