"""Gemini-powered deep codebase analysis for bootstrapping .agent/ files.

This module is optional — it requires the `google-genai` package, which
is only installed with `pip install gemstack[ai]`.
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gemstack.project.detector import ProjectProfile

logger = logging.getLogger(__name__)

# Maximum character budget for context sent to the API
_CHAR_BUDGET = 48_000  # ~12k tokens

# File patterns ranked by relevance for API submission
_HIGH_PRIORITY_PATTERNS = [
    re.compile(r"(route|handler|controller|endpoint|api)", re.IGNORECASE),
    re.compile(r"(schema|model|entity|types?\.)", re.IGNORECASE),
]
_MEDIUM_PRIORITY_PATTERNS = [
    re.compile(r"(config|middleware|auth)", re.IGNORECASE),
]
_EXCLUDED_PATTERNS = [
    re.compile(r"(node_modules|\.git|__pycache__|\.next|dist|build|vendor)", re.IGNORECASE),
    re.compile(r"\.(pyc|pyo|so|dylib|whl|egg|lock)$", re.IGNORECASE),
]


@dataclass
class BootstrapResult:
    """Result of AI-powered codebase analysis."""

    architecture: str = ""
    style: str = ""
    testing: str = ""
    philosophy: str = ""
    status: str = ""
    ai_powered: bool = False
    error: str | None = None

    @classmethod
    def template_only(cls, profile: ProjectProfile) -> BootstrapResult:
        """Create a template-only result (no AI analysis)."""
        return cls(
            ai_powered=False,
            error=None,
        )

    def files(self) -> dict[str, str]:
        """Return a mapping of filename → content for non-empty files."""
        result: dict[str, str] = {}
        if self.architecture:
            result["ARCHITECTURE.md"] = self.architecture
        if self.style:
            result["STYLE.md"] = self.style
        if self.testing:
            result["TESTING.md"] = self.testing
        if self.philosophy:
            result["PHILOSOPHY.md"] = self.philosophy
        if self.status:
            result["STATUS.md"] = self.status
        return result


class AIBootstrapper:
    """Uses Gemini to deeply analyze a codebase and populate .agent/ files.

    This module is async-first because the Gemini SDK supports async natively
    and bootstrapping may involve multiple API calls.
    """

    def __init__(self, model: str = "gemini-3.1-pro-preview") -> None:
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "The 'ai' extra is required for AI bootstrapping. "
                "Install with: pip install gemstack[ai]"
            ) from None
        from gemstack.project.config import GemstackConfig

        config = GemstackConfig.load()
        api_key = config.get_api_key()

        self._genai = genai
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            # Fall back to env vars (which the SDK checks automatically)
            self.client = genai.Client()

        self.model = model

    async def analyze(self, profile: ProjectProfile) -> BootstrapResult:
        """Send key source files to Gemini for deep analysis.

        Strategy:
        1. Send manifest file + config files as context (~2k tokens)
        2. Send a sample of source files selected by relevance (~10k tokens)
        3. Send the context_prompt.md as system instruction (~5k tokens)
        4. Parse the structured response into individual .agent/ files

        Total: ~17k tokens input → ~8k tokens output
        Cost per bootstrap: ~$0.02 with gemini-2.5-flash
        """
        # Build the context payload
        context_parts = self._build_context(profile)

        # Load the system instruction from bundled data
        system_instruction = self._load_system_instruction()

        # Call Gemini (run sync SDK in thread to avoid blocking)
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=context_parts,
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.2,  # Low temperature for factual extraction
                    "max_output_tokens": 8192,
                },
            )
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise

        return self._parse_response(response)

    async def analyze_with_fallback(self, profile: ProjectProfile) -> BootstrapResult:
        """Attempt AI analysis with graceful fallback to template-only mode."""
        try:
            return await self.analyze(profile)
        except Exception as e:
            logger.warning(
                f"AI bootstrapping failed ({e}). "
                "Falling back to template-only mode. "
                "Run `gemstack init --ai` later to upgrade."
            )
            return BootstrapResult.template_only(profile)

    def _build_context(self, profile: ProjectProfile) -> list[str]:
        """Select and format source files for API submission.

        File selection priority:
        1. Manifest files (package.json, pyproject.toml, go.mod)
        2. Config files (tsconfig, vite.config, Dockerfile)
        3. Route/handler files (up to 5, by file size — smaller = more focused)
        4. Schema/model files (up to 3)
        5. Test config files (1-2)

        Total budget: ~12k tokens (48k characters)
        """
        parts: list[str] = []
        char_budget = _CHAR_BUDGET

        # Priority 1: Manifest
        if profile.manifest_file and profile.manifest_file.exists():
            try:
                content = profile.manifest_file.read_text()
                parts.append(f"# {profile.manifest_file.name}\n```\n{content}\n```")
                char_budget -= len(content)
            except OSError:
                pass

        # Priority 2: Config files
        for config_file in profile.config_files[:5]:
            if char_budget <= 0:
                break
            try:
                content = config_file.read_text()
                if len(content) > 5000:
                    content = content[:5000] + "\n... (truncated)"
                parts.append(f"# {config_file.name}\n```\n{content}\n```")
                char_budget -= len(content)
            except OSError:
                continue

        # Priority 3-5: Source file sampling
        source_files = self._rank_source_files(profile)
        for path in source_files:
            if char_budget <= 0:
                break
            try:
                content = path.read_text()
                if len(content) > char_budget:
                    content = content[:char_budget] + "\n... (truncated)"
                rel_path = path.relative_to(profile.root)
                parts.append(f"# {rel_path}\n```\n{content}\n```")
                char_budget -= len(content)
            except (OSError, ValueError):
                continue

        return parts

    def _rank_source_files(self, profile: ProjectProfile) -> list[Path]:
        """Rank source files by relevance for API submission.

        Heuristics:
        - Route/handler files: high priority (they define the API surface)
        - Schema/model files: high priority (they define the data model)
        - Config files: medium priority
        - Tests: low priority (we infer test strategy, not specific tests)
        - Generated files: excluded entirely
        """
        scored: list[tuple[int, int, Path]] = []  # (priority, size, path)

        for source_dir in profile.source_dirs:
            if not source_dir.exists():
                continue

            for path in source_dir.rglob("*"):
                if not path.is_file():
                    continue

                # Skip excluded patterns
                path_str = str(path)
                if any(p.search(path_str) for p in _EXCLUDED_PATTERNS):
                    continue

                # Skip non-text files and very large files
                if path.suffix not in {
                    ".py",
                    ".ts",
                    ".tsx",
                    ".js",
                    ".jsx",
                    ".go",
                    ".rs",
                    ".java",
                    ".rb",
                    ".sql",
                    ".graphql",
                    ".prisma",
                }:
                    continue

                try:
                    size = path.stat().st_size
                except OSError:
                    continue

                if size > 50_000:  # Skip files > 50KB
                    continue

                # Score by filename patterns
                name_str = path.name
                priority = 3  # default: low

                if any(p.search(name_str) for p in _HIGH_PRIORITY_PATTERNS):
                    priority = 1
                elif any(p.search(name_str) for p in _MEDIUM_PRIORITY_PATTERNS):
                    priority = 2

                scored.append((priority, size, path))

        # Sort by priority (ascending), then by size (ascending — smaller = more focused)
        scored.sort(key=lambda x: (x[0], x[1]))

        # Return top 15 files
        return [path for _, _, path in scored[:15]]

    def _load_system_instruction(self) -> str:
        """Load the context_prompt.md system instruction."""
        from importlib.resources import files

        try:
            context_pkg = files("gemstack.data.context")
            resource = context_pkg / "context_prompt.md"
            if hasattr(resource, "read_text"):
                return resource.read_text()
        except (FileNotFoundError, ModuleNotFoundError, TypeError):
            pass

        # Fallback: try source repo
        try:
            import gemstack

            pkg_root = Path(gemstack.__file__).parent.parent.parent
            path = pkg_root / "context" / "context_prompt.md"
            if path.exists():
                return path.read_text()
        except (AttributeError, OSError):
            pass

        logger.warning("Could not load context_prompt.md system instruction")
        return "Analyze this codebase and generate .agent/ context files."

    def _parse_response(self, response: object) -> BootstrapResult:
        """Parse the Gemini API response into individual .agent/ file contents.

        The response text is expected to contain sections delimited by
        markdown headers matching the .agent/ file names.
        """
        # Extract response text
        text = ""
        if hasattr(response, "text"):
            text = response.text
        elif hasattr(response, "candidates"):
            candidates = response.candidates
            if candidates and hasattr(candidates[0], "content"):
                parts = candidates[0].content.parts
                text = "".join(p.text for p in parts if hasattr(p, "text"))

        if not text:
            return BootstrapResult(
                ai_powered=True,
                error="Empty response from Gemini API",
            )

        result = BootstrapResult(ai_powered=True)

        # Parse sections by looking for file markers
        file_markers = {
            "ARCHITECTURE": "architecture",
            "STYLE": "style",
            "TESTING": "testing",
            "PHILOSOPHY": "philosophy",
            "STATUS": "status",
        }

        for marker, attr in file_markers.items():
            pattern = (
                rf"(?:^|\n)#\s*(?:\.agent/)?\s*{marker}\.md\s*\n"
                rf"(.*?)(?=\n#\s*(?:\.agent/)?\s*\w+\.md|\Z)"
            )
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                setattr(result, attr, match.group(1).strip())

        # If no sections were parsed, treat the whole response as architecture
        if not any([result.architecture, result.style, result.testing]):
            result.architecture = text
            result.error = "Response was not structured into sections"

        return result
