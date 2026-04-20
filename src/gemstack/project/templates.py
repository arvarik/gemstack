"""Jinja2 template engine with markdown-safe delimiters.

Uses custom delimiters to avoid conflicts with Go templates, Mustache,
and other common markdown patterns.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, FileSystemLoader, PackageLoader

if TYPE_CHECKING:
    from gemstack.project.detector import ProjectProfile

logger = logging.getLogger(__name__)


def create_template_env(template_dir: Path | None = None) -> Environment:
    """Create a Jinja2 environment with markdown-safe custom delimiters.

    Uses `{= =}` for variables, `{%% %%}` for blocks, and `{## ##}` for comments.
    These are chosen to avoid conflicts with:
    - Standard markdown (no conflict)
    - HTML tags `< >` (the `<< >>` alternative conflicts with HTML)
    - Go templates `{{ }}` (the standard delimiters conflict)
    - Mustache/Handlebars `{{ }}` (standard delimiters conflict)
    """
    if template_dir and template_dir.exists():
        loader: FileSystemLoader | PackageLoader = FileSystemLoader(str(template_dir))
    else:
        loader = PackageLoader("gemstack", "templates")

    return Environment(
        loader=loader,
        block_start_string="{%%",
        block_end_string="%%}",
        variable_start_string="{=",
        variable_end_string="=}",
        comment_start_string="{##",
        comment_end_string="##}",
        autoescape=False,  # noqa: S701 — generating markdown, not HTML
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_agent_files(profile: ProjectProfile, agent_dir: Path) -> list[str]:
    """Render all 5 .agent/ files from Jinja2 templates.

    Args:
        profile: The detected project profile.
        agent_dir: The target .agent/ directory.

    Returns:
        List of created file names.
    """
    env = create_template_env()
    created: list[str] = []

    # Build template context from profile
    context = _build_template_context(profile)

    templates = [
        "architecture.md.j2",
        "style.md.j2",
        "testing.md.j2",
        "philosophy.md.j2",
        "status.md.j2",
    ]

    agent_dir.mkdir(parents=True, exist_ok=True)

    for template_name in templates:
        output_name = template_name.replace(".j2", "").upper()
        # Convert architecture.md → ARCHITECTURE.md
        if output_name == "ARCHITECTURE.MD":
            output_name = "ARCHITECTURE.md"
        elif output_name == "STYLE.MD":
            output_name = "STYLE.md"
        elif output_name == "TESTING.MD":
            output_name = "TESTING.md"
        elif output_name == "PHILOSOPHY.MD":
            output_name = "PHILOSOPHY.md"
        elif output_name == "STATUS.MD":
            output_name = "STATUS.md"

        try:
            template = env.get_template(template_name)
            content = template.render(**context)
            (agent_dir / output_name).write_text(content)
            created.append(output_name)
            logger.info(f"Rendered .agent/{output_name}")
        except Exception as e:
            logger.warning(f"Failed to render template {template_name}: {e}")

    return created


def _build_template_context(profile: ProjectProfile) -> dict[str, Any]:
    """Build the Jinja2 template context from a ProjectProfile."""
    return {
        "name": profile.name,
        "topologies": [t.value for t in profile.topologies] if profile.topologies else ["TBD"],
        "language": profile.language,
        "runtime": profile.runtime,
        "framework": profile.framework,
        "package_manager": profile.package_manager,
        "frontend": profile.framework
        if any(t.value == "frontend" for t in profile.topologies)
        else None,
        "backend": profile.framework
        if any(t.value == "backend" for t in profile.topologies)
        else None,
        "database": "Yes" if profile.has_database else None,
        "dev_command": profile.dev_command,
        "test_command": profile.test_command,
        "build_command": profile.build_command,
        "lint_command": profile.lint_command,
        "has_tests": profile.has_tests,
        "has_ci": profile.has_ci,
        "env_file": str(profile.env_file.name) if profile.env_file else None,
    }
