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
    1. If AUDIT_FINDINGS.md has active findings → REROUTE_TO_BUILD
    2. If AUDIT_FINDINGS.md has "ALL ISSUES RESOLVED" → REROUTE_TO_AUDIT
    3. If lifecycle is fully complete and audit is PASS → READY_TO_SHIP
    4. Otherwise, infer next sequential step from Lifecycle checkboxes.
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

        lifecycle = self._parse_lifecycle(status_path)
        audit_state = self._parse_audit_state(audit_path)

        logger.debug(f"Router audit_state={audit_state}, lifecycle={lifecycle}")

        # Rule 1: Active audit findings → reroute to build to fix them
        if audit_state == "FINDINGS":
            return RoutingDecision(
                action=RoutingAction.REROUTE_TO_BUILD,
                next_command="/step3-build",
                reason=(
                    "Audit findings exist. Rerouting to build to address them. "
                    "The findings have been attached as context."
                ),
                context_files=[str(audit_path)],
            )

        # Rule 2: Builder fixed findings → reroute to audit to verify
        if audit_state == "RESOLVED":
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step4-audit",
                reason=(
                    "Builder has marked issues as resolved. "
                    "Proceeding to Step 4: Audit for re-verification."
                ),
                context_files=[str(audit_path)],
            )

        # Rule 3: Sequential step routing
        next_cmd, phase_name = self._infer_current_step(lifecycle)

        if next_cmd == "/step1-spec":
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step1-spec",
                reason="Begin with Step 1: Spec to define the feature and architecture contracts.",
                context_files=[str(status_path)],
            )

        if next_cmd == "/step2-trap":
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step2-trap",
                reason="Spec is complete. Proceed to Step 2: Trap to write the plan and failing tests.",
                context_files=[str(status_path)],
            )

        if next_cmd == "/step3-build":
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step3-build",
                reason="Trap is set. Proceed to Step 3: Build to implement the code.",
                context_files=[str(status_path)],
            )

        if next_cmd == "/step4-audit":
            # Edge case: If Audit checkbox is missed but Audit explicitly passed
            if audit_state == "PASS":
                return RoutingDecision(
                    action=RoutingAction.READY_TO_SHIP,
                    next_command="/step5-ship",
                    reason="Audit passed with no active findings. Proceed to Step 5: Ship.",
                    context_files=[str(status_path)],
                )

            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step4-audit",
                reason="Build complete. Proceed to Step 4: Audit for security and logic review.",
                context_files=[str(status_path)],
            )

        if next_cmd == "/step5-ship":
            if audit_state == "PASS" or audit_state == "EMPTY":
                return RoutingDecision(
                    action=RoutingAction.READY_TO_SHIP,
                    next_command="/step5-ship",
                    reason="Audit passed. Proceeding to Step 5: Ship — integrate, merge, and deploy.",
                    context_files=[str(status_path)],
                )
            # Should not reach here if FINDINGS/RESOLVED due to earlier rules
            return RoutingDecision(
                action=RoutingAction.CONTINUE,
                next_command="/step4-audit",
                reason="Audit has not explicitly passed. Proceed to Step 4: Audit.",
                context_files=[str(status_path)],
            )

        if next_cmd == "DONE":
            return RoutingDecision(
                action=RoutingAction.BLOCKED,
                next_command="gemstack start",
                reason=(
                    "Current feature lifecycle is fully complete. "
                    "Run `gemstack start <feature>` to begin a new feature."
                ),
                blockers=["Feature already shipped"],
            )

        return RoutingDecision(
            action=RoutingAction.BLOCKED,
            reason="Unable to determine next action from lifecycle state.",
            blockers=["Unrecognized lifecycle state"],
        )

    def _parse_audit_state(self, audit_path: Path) -> str:
        """Parse the state of AUDIT_FINDINGS.md.
        
        Returns:
            "EMPTY" if file doesn't exist or is empty
            "PASS" if auditor passed it
            "RESOLVED" if builder fixed issues but pending audit
            "FINDINGS" if issues exist
        """
        if not audit_path.exists() or audit_path.stat().st_size == 0:
            return "EMPTY"
            
        try:
            content = audit_path.read_text(encoding="utf-8").upper()
        except (OSError, UnicodeDecodeError):
            return "EMPTY"
            
        if "PASS" in content and "BLOCKS_RELEASE" not in content and "DEGRADED" not in content:
            return "PASS"
            
        if "ALL ISSUES RESOLVED" in content:
            return "RESOLVED"
            
        return "FINDINGS"

    def _parse_lifecycle(self, status_path: Path) -> dict[str, bool]:
        """Extract feature lifecycle checkbox state from STATUS.md.

        Returns a dict mapping phase names to completion status.
        """
        try:
            content = status_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return {}

        lifecycle: dict[str, bool] = {}
        # Match lines like: - [x] Step 1: Spec, - [ ] Step 3: Build
        for match in re.finditer(r"-\s*\[([ xX])\]\s*(?:Step\s*\d+:\s*)?(\w+)", content):
            completed = match.group(1).lower() == "x"
            phase_name = match.group(2)
            lifecycle[phase_name] = completed

        return lifecycle

    def _infer_current_step(self, lifecycle: dict[str, bool]) -> tuple[str, str]:
        """Infer the current step from lifecycle checkboxes.

        Returns (next_command, phase_name).
        """
        step_mapping = [
            ("Spec", "/step1-spec"),
            ("Trap", "/step2-trap"),
            ("Build", "/step3-build"),
            ("Audit", "/step4-audit"),
            ("Ship", "/step5-ship"),
        ]

        if not lifecycle:
            return "/step1-spec", "Spec"

        for phase_name, command in step_mapping:
            if not lifecycle.get(phase_name, False):
                return command, phase_name

        # All phases complete → ready to ship
        return "DONE", "Done"
