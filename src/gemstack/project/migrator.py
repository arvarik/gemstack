"""Topology migration — upgrades existing projects with topology-specific sections.

Adds topology declarations, testing matrices, and tracking sections
to existing .agent/ files without overwriting user content.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from gemstack.utils.fileutil import write_atomic

logger = logging.getLogger(__name__)

# Topology-specific testing matrices
_TESTING_MATRICES: dict[str, str] = {
    "backend": """### Backend Route Coverage

| Route | Method | Auth | Contract Test | Integration Test |
|-------|--------|------|---------------|------------------|
| _Fill in your routes_ | | | | |
""",
    "frontend": """### Frontend Component State Matrix

| Component | Loading | Empty | Error | Populated | Offline |
|-----------|---------|-------|-------|-----------|---------|
| _Fill in your components_ | | | | | |
""",
    "ml-ai": """### ML/AI Evaluation Thresholds

| Metric | Baseline | Target | Current | Status |
|--------|----------|--------|---------|--------|
| _Fill in your metrics_ | | | | |
""",
    "infrastructure": """### Infrastructure Validation Matrix

| Service | Health Check | Failover | Backup | Monitoring |
|---------|-------------|----------|--------|------------|
| _Fill in your services_ | | | | | |
""",
    "library-sdk": """### API Surface Coverage

| Export | Unit Test | Type Test | Doc Example | Breaking Change Guard |
|-------|-----------|-----------|-------------|----------------------|
| _Fill in your exports_ | | | | |
""",
}

_STATUS_TRACKERS: dict[str, str] = {
    "backend": """## Stub Audit Tracker

| Stub Location | Description | Blocked By | Target Removal |
|---------------|-------------|------------|----------------|
| _Scan codebase for TODO/FIXME stubs_ | | | |
""",
    "ml-ai": """## Prompt Versioning Changelog

| Prompt | Version | Date | Change | Eval Score |
|--------|---------|------|--------|------------|
| _Track prompt iterations here_ | | | | |
""",
}


@dataclass
class MigrationResult:
    """Result of a topology migration."""

    files_modified: list[str] = field(default_factory=list)
    sections_added: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class TopologyMigrator:
    """Upgrades existing projects to include topology-specific sections.

    Adds:
    1. Topology declaration to ARCHITECTURE.md
    2. Topology-specific testing matrices to TESTING.md
    3. Tracking sections to STATUS.md
    """

    def migrate(
        self,
        project_root: Path,
        topologies: list[str],
    ) -> MigrationResult:
        """Apply topology migration to an existing .agent/ directory.

        Args:
            project_root: Path to the project root.
            topologies: List of topology names to add.

        Returns:
            MigrationResult with details of changes made.
        """
        result = MigrationResult()
        agent_dir = project_root / ".agent"

        if not agent_dir.exists():
            result.warnings.append("No .agent/ directory found")
            return result

        self._update_architecture(agent_dir, topologies, result)
        self._update_testing(agent_dir, topologies, result)
        self._update_status(agent_dir, topologies, result)

        return result

    def _update_architecture(
        self, agent_dir: Path, topologies: list[str], result: MigrationResult
    ) -> None:
        """Insert topology declaration into ARCHITECTURE.md."""
        arch_path = agent_dir / "ARCHITECTURE.md"
        if not arch_path.exists():
            result.warnings.append("ARCHITECTURE.md not found — skipping")
            return

        content = arch_path.read_text()

        # Check if topology declaration already exists
        if re.search(r"\*\*Topology:\*\*", content):
            result.warnings.append("ARCHITECTURE.md already has a topology declaration")
            return

        # Insert after the first heading
        topo_str = ", ".join(topologies)
        declaration = f"\n**Topology:** [{topo_str}]\n"

        # Insert after the first # heading line
        match = re.search(r"^# .+\n", content, re.MULTILINE)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + declaration + content[insert_pos:]
        else:
            content = declaration + "\n" + content

        write_atomic(arch_path, content)
        result.files_modified.append("ARCHITECTURE.md")
        result.sections_added.append(f"Topology declaration: [{topo_str}]")

    def _update_testing(
        self, agent_dir: Path, topologies: list[str], result: MigrationResult
    ) -> None:
        """Insert topology-specific testing matrices into TESTING.md."""
        testing_path = agent_dir / "TESTING.md"
        if not testing_path.exists():
            result.warnings.append("TESTING.md not found — skipping")
            return

        content = testing_path.read_text()
        additions: list[str] = []

        for topo in topologies:
            matrix = _TESTING_MATRICES.get(topo)
            if matrix and matrix.strip().split("\n")[0] not in content:
                additions.append(matrix)

        if not additions:
            return

        # Append before the last section or at the end
        insert_content = "\n" + "\n".join(additions)
        content = content.rstrip() + "\n" + insert_content + "\n"

        write_atomic(testing_path, content)
        result.files_modified.append("TESTING.md")
        result.sections_added.append(f"Testing matrices for: {', '.join(topologies)}")

    def _update_status(
        self, agent_dir: Path, topologies: list[str], result: MigrationResult
    ) -> None:
        """Append tracking sections to STATUS.md."""
        status_path = agent_dir / "STATUS.md"
        if not status_path.exists():
            result.warnings.append("STATUS.md not found — skipping")
            return

        content = status_path.read_text()
        additions: list[str] = []

        for topo in topologies:
            tracker = _STATUS_TRACKERS.get(topo)
            if tracker and tracker.strip().split("\n")[0] not in content:
                additions.append(tracker)

        # Always add stub tracker if not present and any topology is set
        if "## Stub Audit Tracker" not in content and "backend" not in topologies:
            stub_tracker = _STATUS_TRACKERS.get("backend", "")
            if stub_tracker:
                additions.append(stub_tracker)

        if not additions:
            return

        insert_content = "\n" + "\n".join(additions)
        content = content.rstrip() + "\n" + insert_content + "\n"

        write_atomic(status_path, content)
        result.files_modified.append("STATUS.md")
        result.sections_added.append(f"Tracking sections for: {', '.join(topologies)}")
