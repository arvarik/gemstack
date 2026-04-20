"""Deterministic phase router — DAG routing engine.

Reads filesystem state (STATUS.md, AUDIT_FINDINGS.md) and outputs
deterministic routing decisions for the next workflow step.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class RoutingAction(str, Enum):
    """Possible routing actions."""

    CONTINUE = "continue"
    REROUTE_TO_BUILD = "reroute_to_build"
    REROUTE_TO_SPEC = "reroute_to_spec"
    READY_TO_SHIP = "ready_to_ship"
    BLOCKED = "blocked"


@dataclass
class RoutingDecision:
    """A routing decision with context."""

    action: RoutingAction
    next_command: str = ""
    reason: str = ""
    context_files: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


# Map of STATUS.md state values to their human-readable descriptions
_STATE_DESCRIPTIONS = {
    "INITIALIZED": "Project initialized, no feature started",
    "IN_PROGRESS": "Feature in progress",
    "READY_FOR_BUILD": "Spec and plan complete, ready to build",
    "READY_FOR_AUDIT": "Build complete, ready for audit",
    "READY_FOR_SHIP": "Audit passed, ready to ship",
    "SHIPPED": "Feature shipped",
    "BLOCKED": "Blocked — manual intervention required",
}


class PhaseRouter:
    """Deterministic state machine for workflow routing.

    Rules (evaluated in order):
    1. If AUDIT_FINDINGS.md exists and has content → REROUTE_TO_BUILD
    2. If state is INITIALIZED → CONTINUE to /step1-spec
    3. If state is IN_PROGRESS → CONTINUE to current step
    4. If state is READY_FOR_BUILD → CONTINUE to /step3-build
    5. If state is READY_FOR_AUDIT → CONTINUE to /step4-audit
    6. If state is READY_FOR_SHIP and no findings → READY_TO_SHIP
    7. If state is SHIPPED → BLOCKED (start a new feature)
    8. Default → BLOCKED with "unable to determine state"
    """

    def route(self, project_root: Path) -> RoutingDecision:
        """Read STATUS.md and AUDIT_FINDINGS.md to determine next action."""
        status_path = project_root / ".agent" / "STATUS.md"
        audit_path = project_root / ".agent" / "AUDIT_FINDINGS.md"

        if not status_path.exists():
            return RoutingDecision(
                action=RoutingAction.BLOCKED,
                next_command="gemstack init",
                reason="No .agent/STATUS.md found. Initialize with `gemstack init`.",
                context_files=[],
                blockers=["Missing .agent/ directory"],
            )

        state = self._parse_state(status_path)
        lifecycle = self._parse_lifecycle(status_path)
        has_findings = audit_path.exists() and audit_path.stat().st_size > 0

        logger.debug(f"Router state: {state}, has_findings={has_findings}, lifecycle={lifecycle}")

        # Rule 1: Audit findings exist → reroute to build
        if has_findings:
            return RoutingDecision(
                action=RoutingAction.REROUTE_TO_BUILD,
                next_command="/step3-build",
                reason=(
                    "Audit findings exist. Rerouting to build to address them. "
                    "The findings have been attached as context."
                ),
                context_files=[str(audit_path)],
            )

        # Rule 2: Initialized → start with spec
        if state == "INITIALIZED":
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step1-spec",
                reason=(
                    "Project is initialized but no feature has been started. "
                    "Begin with Step 1: Spec to define the feature."
                ),
                context_files=[str(status_path)],
            )

        # Rule 3: In progress → determine current step from lifecycle
        if state == "IN_PROGRESS":
            next_cmd = self._infer_current_step(lifecycle)
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command=next_cmd,
                reason=f"Feature is in progress. Continue with {next_cmd}.",
                context_files=[str(status_path)],
            )

        # Rule 4: Ready for build
        if state == "READY_FOR_BUILD":
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step3-build",
                reason=(
                    "Spec and plan are complete. Proceeding to Step 3: Build. "
                    "Read the plan and contracts, then implement."
                ),
                context_files=[str(status_path)],
            )

        # Rule 5: Ready for audit
        if state == "READY_FOR_AUDIT":
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step4-audit",
                reason=(
                    "Build is complete and tests are passing. "
                    "Proceeding to Step 4: Audit for security and logic review."
                ),
                context_files=[str(status_path)],
            )

        # Rule 6: Ready to ship (no findings)
        if state == "READY_FOR_SHIP":
            return RoutingDecision(
                action=RoutingAction.READY_TO_SHIP,
                next_command="/step5-ship",
                reason=(
                    "Audit passed with no findings. "
                    "Proceeding to Step 5: Ship — integrate, merge, and deploy."
                ),
                context_files=[str(status_path)],
            )

        # Rule 7: Already shipped
        if state == "SHIPPED":
            return RoutingDecision(
                action=RoutingAction.BLOCKED,
                next_command="gemstack start",
                reason=(
                    "Current feature has been shipped. "
                    "Run `gemstack start <feature>` to begin a new feature."
                ),
                blockers=["Feature already shipped"],
            )

        # Rule 8: Unknown state
        return RoutingDecision(
            action=RoutingAction.BLOCKED,
            reason=f"Unable to determine next action from state '{state}'.",
            blockers=[f"Unrecognized state: {state}"],
        )

    def _parse_state(self, status_path: Path) -> str:
        """Extract [STATE: ...] enum from STATUS.md."""
        try:
            content = status_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return "UNKNOWN"

        match = re.search(r"\[STATE:\s*(\w+)\]", content)
        return match.group(1) if match else "UNKNOWN"

    def _parse_lifecycle(self, status_path: Path) -> dict[str, bool]:
        """Extract feature lifecycle checkbox state from STATUS.md.

        Returns a dict mapping phase names to completion status.
        """
        try:
            content = status_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return {}

        lifecycle: dict[str, bool] = {}
        # Match lines like: - [x] Spec, - [ ] Build
        for match in re.finditer(r"-\s*\[([ xX])\]\s*(\w+)", content):
            completed = match.group(1).lower() == "x"
            phase_name = match.group(2)
            lifecycle[phase_name] = completed

        return lifecycle

    def _infer_current_step(self, lifecycle: dict[str, bool]) -> str:
        """Infer the current step from lifecycle checkboxes.

        Returns the next uncompleted step command.
        """
        step_mapping = [
            ("Spec", "/step1-spec"),
            ("Trap", "/step2-trap"),
            ("Build", "/step3-build"),
            ("Audit", "/step4-audit"),
            ("Ship", "/step5-ship"),
        ]

        for phase_name, command in step_mapping:
            if not lifecycle.get(phase_name, False):
                return command

        # All phases complete → ready to ship
        return "/step5-ship"
