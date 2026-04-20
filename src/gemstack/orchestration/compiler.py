"""Context/prompt compiler — JIT prompt assembly.

The heart of Gemstack's value: dynamically stitches together the exact
combination of role definitions, phase instructions, topology guardrails,
and project-specific context needed for a given workflow step.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)


class WorkflowMeta(NamedTuple):
    """Parsed metadata from a workflow step file."""

    name: str
    description: str
    roles: list[str]
    phases: list[str]


@dataclass
class CompiledContext:
    """Result of context compilation."""

    sections: list[tuple[str, str]] = field(default_factory=list)
    total_content: str = ""
    token_estimate: int = 0
    sources: list[str] = field(default_factory=list)
    truncated: bool = False


class ContextCompiler:
    """Compiles context for a specific workflow step.

    Performs JIT (Just-In-Time) prompt assembly by:
    1. Parsing the workflow .md to extract required roles and phases
    2. Loading role definitions from bundled data
    3. Loading phase definitions from bundled data
    4. Loading topology guardrails from project's ARCHITECTURE.md
    5. Loading project context (.agent/ files)
    6. Loading relevant source files from STATUS.md
    7. Stitching everything with clear section boundaries
    8. Optionally truncating to fit within token budget
    """

    # Known valid workflow steps
    VALID_STEPS = frozenset(
        {
            "step1-spec",
            "step2-trap",
            "step3-build",
            "step4-audit",
            "step5-ship",
        }
    )

    def compile(
        self,
        step: str,
        project_root: Path,
        include_source: bool = True,
        max_tokens: int | None = None,
    ) -> CompiledContext:
        """Assemble a complete system prompt for the given workflow step.

        Args:
            step: Workflow step name (e.g., "step1-spec", "step3-build").
            project_root: Path to the project root directory.
            include_source: Whether to include source files from STATUS.md.
            max_tokens: Optional max token budget for truncation.

        Returns:
            CompiledContext with all sections stitched together.

        Raises:
            FileNotFoundError: If the workflow step file cannot be found.
        """
        sections: list[tuple[str, str]] = []

        # 1. Parse workflow step
        workflow_meta = self._parse_workflow_step(step)
        sections.append(("Workflow Goal", f"# {workflow_meta.description}\n"))

        # 2. Load roles
        for role in workflow_meta.roles:
            content = self._load_bundled("roles", role)
            if content:
                sections.append((f"Role: {role}", content))

        # 3. Load phases
        for phase in workflow_meta.phases:
            content = self._load_bundled("phases", phase)
            if content:
                sections.append((f"Phase: {phase}", content))

        # 4. Load topology guardrails
        topologies = self._detect_project_topologies(project_root)
        for topo in topologies:
            content = self._load_bundled("topologies", topo)
            if content:
                sections.append((f"Topology: {topo}", content))

        # 5. Load .agent/ context
        agent_dir = project_root / ".agent"
        for agent_file in ["ARCHITECTURE.md", "STYLE.md", "TESTING.md", "STATUS.md"]:
            path = agent_dir / agent_file
            if path.exists():
                try:
                    sections.append((agent_file, path.read_text(encoding="utf-8")))
                except (OSError, UnicodeDecodeError) as e:
                    logger.warning(f"Failed to read {path}: {e}")

        # 6. Source files from STATUS.md → Relevant Files
        if include_source:
            relevant = self._extract_relevant_files(agent_dir / "STATUS.md")
            for filepath in relevant:
                full_path = project_root / filepath
                if full_path.exists() and full_path.is_file():
                    try:
                        content = full_path.read_text(encoding="utf-8")
                        sections.append((f"Source: {filepath}", f"```file-content\n{content}\n```"))
                    except (OSError, UnicodeDecodeError) as e:
                        logger.warning(f"Failed to read source file {filepath}: {e}")

        # 7. Add the full workflow content as routing protocol
        workflow_content = self._load_workflow_content(step)
        if workflow_content:
            sections.append(("Workflow Protocol", workflow_content))

        # 7.5. Fire plugin pre-compile hook
        from gemstack.plugins import fire_pre_compile

        sections = fire_pre_compile(step, sections)

        # 8. Stitch with section boundaries
        total = self._stitch(sections)

        # 9. Truncate if needed
        token_estimate = len(total) // 4
        truncated = False
        if max_tokens and token_estimate > max_tokens:
            total = self._truncate(sections, max_tokens)
            truncated = True
            token_estimate = max_tokens

        # 9.5. Fire plugin post-compile hook
        from gemstack.plugins import fire_post_compile

        total = fire_post_compile(step, total)
        token_estimate = len(total) // 4

        return CompiledContext(
            sections=sections,
            total_content=total,
            token_estimate=token_estimate,
            sources=[name for name, _ in sections],
            truncated=truncated,
        )

    def _parse_workflow_step(self, step: str) -> WorkflowMeta:
        """Parse a workflow step .md file to extract metadata.

        Reads the YAML frontmatter for name/description and the
        ## Composition section for roles and phases.
        """
        content = self._load_workflow_content(step)
        if not content:
            msg = f"Workflow step '{step}' not found in bundled data."
            raise FileNotFoundError(msg)

        # Parse YAML frontmatter (between --- delimiters)
        name = step
        description = ""
        fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            name_match = re.search(r"name:\s*(.+)", fm)
            if name_match:
                name = name_match.group(1).strip()
            desc_match = re.search(r'description:\s*"?([^"]+)"?', fm)
            if desc_match:
                description = desc_match.group(1).strip()

        # Parse Composition section for roles and phases
        roles: list[str] = []
        phases: list[str] = []

        roles_match = re.search(r"\*\*Roles?:\*\*\s*(.+)", content)
        if roles_match:
            roles_str = roles_match.group(1)
            roles = [
                r.strip().strip("`") for r in re.split(r",\s*", roles_str) if r.strip().strip("`")
            ]

        phases_match = re.search(r"\*\*Phases?:\*\*\s*(.+)", content)
        if phases_match:
            phases_str = phases_match.group(1)
            phases = [
                p.strip().strip("`") for p in re.split(r",\s*", phases_str) if p.strip().strip("`")
            ]

        logger.debug(f"Parsed workflow {step}: roles={roles}, phases={phases}")

        return WorkflowMeta(
            name=name,
            description=description,
            roles=roles,
            phases=phases,
        )

    def _load_workflow_content(self, step: str) -> str | None:
        """Load the raw content of a workflow step .md file."""
        from importlib.resources import files

        try:
            workflows = files("gemstack.data.workflows")
            resource = workflows / f"{step}.md"
            if hasattr(resource, "read_text"):
                return resource.read_text()
        except (FileNotFoundError, ModuleNotFoundError, TypeError):
            pass

        # Fallback: try the source repo's workflows/ directory
        # This handles editable installs and development mode
        try:
            import gemstack

            pkg_root = Path(gemstack.__file__).parent.parent.parent
            workflow_path = pkg_root / "workflows" / f"{step}.md"
            if workflow_path.exists():
                return workflow_path.read_text()
        except (AttributeError, OSError):
            pass

        return None

    def _load_bundled(self, category: str, name: str) -> str | None:
        """Load a bundled markdown file by category and name.

        Args:
            category: One of 'roles', 'phases', 'topologies'.
            name: The name to match (e.g., 'Product Visionary', 'Build', 'backend').

        Returns:
            The markdown content, or None if not found.
        """
        from importlib.resources import files

        # Convert display name to filename
        # "Product Visionary" → "product-visionary.md"
        # "Principal Backend Engineer" → "principal-backend-engineer.md"
        # "Build" → "build.md"
        filename = name.lower().replace(" ", "-") + ".md"

        # Try bundled data first
        try:
            data_pkg = files(f"gemstack.data.{category}")
            resource = data_pkg / filename
            if hasattr(resource, "read_text"):
                return resource.read_text()
        except (FileNotFoundError, ModuleNotFoundError, TypeError):
            pass

        # Fallback: try the source repo directory
        try:
            import gemstack

            pkg_root = Path(gemstack.__file__).parent.parent.parent
            path = pkg_root / category / filename
            if path.exists():
                return path.read_text()
        except (AttributeError, OSError):
            pass

        logger.warning(f"Could not load bundled {category}/{filename}")
        return None

    def _detect_project_topologies(self, project_root: Path) -> list[str]:
        """Extract topology declarations from ARCHITECTURE.md.

        Parses lines like: **Topology:** [frontend, backend]
        """
        arch_path = project_root / ".agent" / "ARCHITECTURE.md"
        if not arch_path.exists():
            return []

        try:
            content = arch_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        match = re.search(r"\*\*Topology:\*\*\s*\[([^\]]+)\]", content)
        if not match:
            return []

        topologies = [t.strip() for t in match.group(1).split(",") if t.strip()]
        # Filter out placeholder values
        return [t for t in topologies if t.lower() != "tbd"]

    def _extract_relevant_files(self, status_path: Path) -> list[str]:
        """Extract file paths from the Relevant Files section of STATUS.md."""
        if not status_path.exists():
            return []

        try:
            content = status_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        # Find the "## Relevant Files" section
        section_match = re.search(
            r"##\s*Relevant Files\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL,
        )
        if not section_match:
            return []

        section = section_match.group(1)
        files: list[str] = []

        # Extract file paths, allowing spaces
        for line in section.splitlines():
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                filepath = line[1:].strip().strip("`").strip()
                if filepath and not filepath.startswith("(") and not filepath.startswith("_"):
                    files.append(filepath)

        return files

    def _stitch(self, sections: list[tuple[str, str]]) -> str:
        """Stitch sections with clear markdown boundaries."""
        parts: list[str] = []
        for name, content in sections:
            parts.append(f"{'=' * 60}\n## {name}\n{'=' * 60}\n\n{content}\n")
        return "\n".join(parts)

    def _truncate(self, sections: list[tuple[str, str]], max_tokens: int) -> str:
        """Truncate sections to fit within token budget.

        Truncation priority (remove first):
        1. Source files (lowest priority)
        2. Workflow Protocol
        3. Topology guardrails
        4. .agent/ context files
        5. Phase definitions
        6. Role definitions (highest priority — keep these last)
        7. Workflow Goal (never truncated)
        """
        # Priority ordering: lower number = keep longer
        priority_order: dict[str, int] = {}
        for name, _ in sections:
            if name == "Workflow Goal":
                priority_order[name] = 0
            elif name.startswith("Role:"):
                priority_order[name] = 1
            elif name.startswith("Phase:"):
                priority_order[name] = 2
            elif name in ("ARCHITECTURE.md", "STYLE.md", "TESTING.md", "STATUS.md"):
                priority_order[name] = 3
            elif name.startswith("Topology:"):
                priority_order[name] = 4
            elif name == "Workflow Protocol":
                priority_order[name] = 5
            elif name.startswith("Source:"):
                priority_order[name] = 6
            else:
                priority_order[name] = 5

        # Sort sections by priority (keep high-priority first)
        sorted_sections = sorted(
            sections,
            key=lambda s: priority_order.get(s[0], 5),
        )

        # Build from highest priority until budget exceeded
        kept: list[tuple[str, str]] = []
        total_chars = 0
        char_budget = max_tokens * 4

        for name, content in sorted_sections:
            section_chars = len(content) + len(name) + 130  # overhead for delimiters
            if total_chars + section_chars <= char_budget:
                kept.append((name, content))
                total_chars += section_chars
            else:
                logger.debug(f"Truncated section: {name}")

        return self._stitch(kept)
