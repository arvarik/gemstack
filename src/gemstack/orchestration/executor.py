"""Autonomous step executor — the heart of Gemstack v1.0.

Compiles context via ``ContextCompiler``, sends it to Gemini,
parses structured responses, and writes results to project files.
Integrates with cost tracking, plugin hooks, and the phase router.

Requires the ``gemstack[ai]`` optional dependency (google-genai).
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gemstack.utils.fileutil import write_atomic

logger = logging.getLogger(__name__)

# Step-specific output expectations
_STEP_OUTPUTS: dict[str, dict[str, Any]] = {
    "step1-spec": {
        "description": "Define feature spec and lock in contracts",
        "output_files": ["ARCHITECTURE.md"],
        "output_dirs": ["docs/explorations"],
        "max_output_tokens": 8192,
    },
    "step2-trap": {
        "description": "Write task plan and failing test suite",
        "output_files": [],
        "output_dirs": ["docs/plans"],
        "max_output_tokens": 12288,
    },
    "step3-build": {
        "description": "Implement until all tests pass",
        "output_files": [],
        "output_dirs": [],
        "max_output_tokens": 16384,
    },
    "step4-audit": {
        "description": "Security and logic review",
        "output_files": ["AUDIT_FINDINGS.md"],
        "output_dirs": [],
        "max_output_tokens": 8192,
    },
    "step5-ship": {
        "description": "Integrate, merge, deploy",
        "output_files": [],
        "output_dirs": ["docs/archive"],
        "max_output_tokens": 4096,
    },
}


@dataclass
class ExecutionResult:
    """Result of autonomous step execution."""

    step: str
    feature: str
    success: bool
    dry_run: bool = False
    files_written: list[str] = field(default_factory=list)
    compiled_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    error: str | None = None
    next_step: str = ""

    def summary(self) -> str:
        """Human-readable summary of the execution."""
        if self.dry_run:
            return (
                f"🔍 DRY RUN: {self.step} for '{self.feature}'\n"
                f"   Context: ~{self.compiled_tokens:,} tokens\n"
                f"   Would write to: {', '.join(self.files_written) or '(none)'}\n"
                f"   Next step: {self.next_step or '(router will decide)'}"
            )
        if self.success:
            return (
                f"✅ {self.step} completed for '{self.feature}'\n"
                f"   Files: {', '.join(self.files_written)}\n"
                f"   Tokens: {self.compiled_tokens:,} in / "
                f"{self.output_tokens:,} out\n"
                f"   Cost: ${self.cost_usd:.4f}\n"
                f"   Duration: {self.duration_seconds:.1f}s\n"
                f"   Next: {self.next_step}"
            )
        return f"❌ {self.step} failed: {self.error}"


class StepExecutor:
    """Autonomous executor for Gemstack workflow steps.

    Orchestrates the full execution pipeline:
    1. Validate step transition via PhaseRouter
    2. Compile context via ContextCompiler
    3. Check cost budget (if tracking enabled)
    4. Fire plugin pre_run hook
    5. Call Gemini API via asyncio.to_thread()
    6. Parse structured response into file operations
    7. Write results via write_atomic()
    8. Record costs
    9. Fire plugin post_run hook
    10. Return ExecutionResult with next-step guidance
    """

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        max_cost: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self.model = model
        self.max_cost = max_cost
        self.max_tokens = max_tokens

    async def execute(
        self,
        step: str,
        feature: str,
        project_root: Path,
        *,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Execute a workflow step autonomously.

        Acquires a per-project lockfile (``.agent/.gemstack.lock``) to
        prevent concurrent executions from corrupting state.

        Args:
            step: Workflow step (e.g., "step1-spec").
            feature: Feature description (e.g., "Add user notifications").
            project_root: Path to the project root.
            dry_run: If True, compile context but skip the API call.

        Returns:
            ExecutionResult with details of the execution.
        """
        lock_path = self._acquire_lock(project_root)
        try:
            return await self._execute_locked(step, feature, project_root, dry_run=dry_run)
        finally:
            self._release_lock(lock_path)

    async def _execute_locked(
        self,
        step: str,
        feature: str,
        project_root: Path,
        *,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Inner execution logic, called under lock."""
        start_time = time.monotonic()

        # Validate step name
        step_meta = _STEP_OUTPUTS.get(step)
        if step_meta is None:
            return ExecutionResult(
                step=step,
                feature=feature,
                success=False,
                error=(f"Unknown step '{step}'. Valid steps: {', '.join(_STEP_OUTPUTS)}"),
            )

        # 1. Compile context
        from gemstack.orchestration.compiler import ContextCompiler

        compiler = ContextCompiler()
        try:
            compiled = compiler.compile(
                step=step,
                project_root=project_root,
                include_source=True,
            )
        except FileNotFoundError as e:
            return ExecutionResult(
                step=step,
                feature=feature,
                success=False,
                error=f"Context compilation failed: {e}",
            )

        # Inject the feature description into the context
        feature_section = (
            f"## Feature Request\n\n"
            f"The user wants to: **{feature}**\n\n"
            f"Execute {step_meta['description']} for this feature.\n"
        )
        full_prompt = compiled.total_content + "\n\n" + feature_section

        # 2. Determine next step from router
        from gemstack.orchestration.router import PhaseRouter

        router = PhaseRouter()
        decision = router.route(project_root)
        next_step = decision.next_command

        # 3. Dry-run mode: return compilation results without API call
        if dry_run:
            expected_files = list(step_meta.get("output_files", []))
            return ExecutionResult(
                step=step,
                feature=feature,
                success=True,
                dry_run=True,
                compiled_tokens=compiled.token_estimate,
                files_written=expected_files,
                next_step=next_step,
                duration_seconds=time.monotonic() - start_time,
            )

        # 4. Check cost budget
        cost_tracker = self._get_cost_tracker(project_root)
        if cost_tracker:
            try:
                cost_tracker.check_budget(step, feature)
            except Exception as e:
                return ExecutionResult(
                    step=step,
                    feature=feature,
                    success=False,
                    error=str(e),
                )

        # 5. Fire plugin pre_run hook
        from gemstack.plugins import fire_pre_run

        fire_pre_run(step, feature)

        # 6. Call Gemini API
        try:
            response_text, usage = await self._call_gemini(
                full_prompt,
                max_output_tokens=step_meta["max_output_tokens"],
            )
        except ImportError:
            return ExecutionResult(
                step=step,
                feature=feature,
                success=False,
                error=(
                    "The 'ai' extra is required for autonomous execution. "
                    "Install with: pip install gemstack[ai]"
                ),
            )
        except Exception as e:
            return ExecutionResult(
                step=step,
                feature=feature,
                success=False,
                error=f"Gemini API call failed: {e}",
            )

        # 7. Parse response and write files
        files_written = self._write_results(step, response_text, project_root)

        # 8. Record costs
        input_tokens = usage.get("input_tokens", compiled.token_estimate)
        output_tokens = usage.get("output_tokens", len(response_text) // 4)
        cost_usd = 0.0
        if cost_tracker:
            record = cost_tracker.record(
                step=step,
                feature=feature,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            cost_usd = record.cost_usd

        # 9. Fire plugin post_run hook
        from gemstack.plugins import fire_post_run

        result = ExecutionResult(
            step=step,
            feature=feature,
            success=True,
            compiled_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            files_written=files_written,
            next_step=next_step,
            duration_seconds=time.monotonic() - start_time,
        )
        fire_post_run(step, result)

        return result

    async def _call_gemini(
        self,
        prompt: str,
        max_output_tokens: int = 8192,
    ) -> tuple[str, dict[str, int]]:
        """Call the Gemini API via asyncio.to_thread().

        Returns:
            Tuple of (response_text, usage_dict).
        """
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "The 'ai' extra is required. Install with: pip install gemstack[ai]"
            ) from None

        client = genai.Client()
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=self.model,
            contents=[prompt],
            config={
                "temperature": 0.3,
                "max_output_tokens": max_output_tokens,
            },
        )

        # Extract text
        text = ""
        if hasattr(response, "text"):
            text = response.text or ""
        elif hasattr(response, "candidates"):
            candidates = response.candidates
            if candidates and hasattr(candidates[0], "content"):
                content = candidates[0].content
                if content is not None and content.parts is not None:
                    text = "".join(str(p.text) for p in content.parts if hasattr(p, "text"))

        # Extract usage metadata
        usage: dict[str, int] = {}
        if hasattr(response, "usage_metadata"):
            meta = response.usage_metadata
            if meta is not None and hasattr(meta, "prompt_token_count"):
                usage["input_tokens"] = int(meta.prompt_token_count or 0)
            if meta is not None and hasattr(meta, "candidates_token_count"):
                usage["output_tokens"] = int(meta.candidates_token_count or 0)

        return text, usage

    @staticmethod
    def _validate_write_path(filepath: str, project_root: Path) -> Path | None:
        """Validate and resolve a write target path.

        Returns the resolved Path if safe, or None if the path
        is rejected (traversal, absolute, empty, or contains
        dangerous characters).
        """
        # Reject empty or whitespace-only paths
        if not filepath or not filepath.strip():
            logger.warning("Rejected empty filepath from AI response")
            return None

        # Reject null bytes
        if "\x00" in filepath:
            logger.warning("Rejected filepath with null bytes")
            return None

        # Normalize to forward slashes and strip
        filepath = filepath.strip().replace("\\", "/")

        # Reject absolute paths
        if filepath.startswith("/") or (len(filepath) >= 2 and filepath[1] == ":"):
            logger.warning(f"Rejected absolute filepath: {filepath}")
            return None

        # Block dangerous internal directories
        filepath_lower = filepath.lower()
        if (
            filepath_lower.startswith(".git/")
            or "/.git/" in filepath_lower
            or filepath_lower == ".git"
        ):
            logger.warning(f"Rejected attempt to write to .git directory: {filepath}")
            return None
        if (
            filepath_lower.startswith(".agent/")
            or "/.agent/" in filepath_lower
            or filepath_lower == ".agent"
        ):
            logger.warning(f"Rejected attempt to write to .agent directory: {filepath}")
            return None

        full_path = (project_root / filepath).resolve()
        root_resolved = project_root.resolve()

        # Reject paths that escape the project root
        if not full_path.is_relative_to(root_resolved):
            logger.warning(
                f"Rejected path traversal attempt: {filepath} "
                f"resolves to {full_path} (outside {root_resolved})"
            )
            return None

        return full_path

    def _write_results(
        self,
        step: str,
        response_text: str,
        project_root: Path,
    ) -> list[str]:
        """Parse the structured response and write files.

        The response is expected to contain file blocks delimited by:
        ```file:path/to/file.md
        content
        ```

        All write targets are validated against the project root to
        prevent path traversal attacks from AI-generated responses.

        Falls back to step-specific heuristics if no file blocks found.
        """
        files_written: list[str] = []

        # Try to parse explicit file blocks
        file_pattern = re.compile(
            r"```file:([^\n]+)\n(.*?)```",
            re.DOTALL,
        )
        matches = list(file_pattern.finditer(response_text))

        if matches:
            for match in matches:
                filepath = match.group(1).strip()
                content = match.group(2)

                # Validate path stays within project root
                full_path = self._validate_write_path(filepath, project_root)
                if full_path is None:
                    logger.warning(f"Skipping unsafe path: {filepath}")
                    continue

                if full_path.is_dir():
                    logger.error(f"Cannot overwrite directory with file: {filepath}")
                    continue
                full_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    write_atomic(full_path, content)
                    files_written.append(filepath)
                    logger.info(f"Wrote: {filepath}")
                except IsADirectoryError:
                    logger.error(f"Cannot overwrite directory with file: {filepath}")
                except OSError as e:
                    logger.error(f"Failed to write {filepath}: {e}")
        else:
            # Fallback: step-specific heuristic writing
            files_written = self._write_heuristic(step, response_text, project_root)

        return files_written

    def _write_heuristic(
        self,
        step: str,
        response_text: str,
        project_root: Path,
    ) -> list[str]:
        """Step-specific heuristic for writing response content.

        All paths are hardcoded and validated, so path traversal
        is not possible in this method.
        """
        files_written: list[str] = []
        agent_dir = project_root / ".agent"
        agent_dir.mkdir(parents=True, exist_ok=True)

        if step == "step1-spec":
            # Write the spec output to an exploration doc
            docs_dir = project_root / "docs" / "explorations"
            docs_dir.mkdir(parents=True, exist_ok=True)
            spec_path = docs_dir / "spec-output.md"
            write_atomic(spec_path, response_text)
            files_written.append("docs/explorations/spec-output.md")

        elif step == "step4-audit":
            # Write audit findings
            findings_path = agent_dir / "AUDIT_FINDINGS.md"
            write_atomic(findings_path, response_text)
            files_written.append(".agent/AUDIT_FINDINGS.md")

        elif step == "step5-ship":
            # Write ship summary to archive
            archive_dir = project_root / "docs" / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            ship_path = archive_dir / "ship-summary.md"
            write_atomic(ship_path, response_text)
            files_written.append("docs/archive/ship-summary.md")

        else:
            # Generic: write to a step-specific output file
            output_path = agent_dir / f"{step}-output.md"
            write_atomic(output_path, response_text)
            files_written.append(f".agent/{step}-output.md")

        return files_written

    @staticmethod
    def _acquire_lock(project_root: Path) -> Path | None:
        """Acquire a per-project lockfile to prevent concurrent execution.

        Uses exclusively created file lock, making it safe across
        all platforms including Windows.

        Returns:
            Path of the lock file, or None if locking fails implicitly.
        """
        agent_dir = project_root / ".agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
        lock_path = agent_dir / ".gemstack.lock"

        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            logger.debug(f"Acquired lock: {lock_path}")
            return lock_path
        except FileExistsError:
            raise RuntimeError(
                "Another `gemstack run` is already executing in this project. "
                f"If this is incorrect, remove {lock_path}"
            ) from None
        except OSError as e:
            logger.warning(f"Failed to acquire lockfile: {e}")
            return None

    @staticmethod
    def _release_lock(lock_path: Path | None) -> None:
        """Release the lockfile."""
        if lock_path is None:
            return
        with contextlib.suppress(OSError):
            lock_path.unlink()

    def _get_cost_tracker(self, project_root: Path) -> Any:
        """Get a CostTracker if cost limits are configured."""
        if self.max_cost is None and self.max_tokens is None:
            # Still create a tracker for recording, just without limits
            from gemstack.orchestration.cost_tracker import CostTracker

            return CostTracker(project_root)

        from gemstack.orchestration.cost_tracker import CostTracker

        return CostTracker(
            project_root,
            max_cost_per_feature=self.max_cost,
            max_tokens_per_step=self.max_tokens,
        )
