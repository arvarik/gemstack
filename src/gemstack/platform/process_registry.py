"""Process registry for tracking background subprocesses.

Tracks PIDs of background commands started by ``gemstack run``,
supports clean shutdown via signal handlers, and persists state
to ``.agent/.processes.json``.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from gemstack.utils.fileutil import write_atomic

logger = logging.getLogger(__name__)


@dataclass
class ProcessRecord:
    """A tracked background process."""

    pid: int
    step: str
    feature: str
    started_at: float = field(default_factory=time.time)
    status: str = "running"  # running | completed | terminated

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-safe dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProcessRecord:
        """Deserialize from dict."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ProcessRegistry:
    """Tracks background processes started by gemstack run.

    Provides registration, status checking, and clean shutdown.
    State is persisted to ``.agent/.processes.json``.
    """

    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root
        self._registry_file = project_root / ".agent" / ".processes.json"
        self._records: list[ProcessRecord] = self._load()
        self._original_sigint: signal.Handlers = signal.SIG_DFL
        self._original_sigterm: signal.Handlers = signal.SIG_DFL

    def register(self, pid: int, step: str, feature: str) -> ProcessRecord:
        """Register a new background process."""
        record = ProcessRecord(pid=pid, step=step, feature=feature)
        self._records.append(record)
        self._persist()
        logger.info(f"Registered process {pid} for {step}/{feature}")
        return record

    def get_active(self) -> list[ProcessRecord]:
        """Return all records whose processes are still running."""
        active: list[ProcessRecord] = []
        for record in self._records:
            if record.status != "running":
                continue
            if self._is_alive(record.pid):
                active.append(record)
            else:
                record.status = "completed"
        self._persist()
        return active

    def terminate_all(self) -> int:
        """Send SIGTERM to all tracked running processes.

        Returns the number of processes signalled.
        """
        count = 0
        for record in self._records:
            if record.status != "running":
                continue
            if self._is_alive(record.pid):
                try:
                    os.kill(record.pid, signal.SIGTERM)
                    record.status = "terminated"
                    count += 1
                    logger.info(f"Terminated process {record.pid}")
                except OSError as e:
                    logger.warning(f"Failed to terminate PID {record.pid}: {e}")
            else:
                record.status = "completed"
        self._persist()
        return count

    def cleanup_stale(self) -> int:
        """Remove records for processes that are no longer running.

        Returns the number of stale records cleaned up.
        """
        before = len(self._records)
        alive: list[ProcessRecord] = []
        for record in self._records:
            if record.status == "running" and not self._is_alive(record.pid):
                record.status = "completed"
            alive.append(record)
        # Keep only the last 50 records to avoid unbounded growth
        self._records = alive[-50:]
        self._persist()
        return before - len(self._records)

    def install_signal_handlers(self) -> None:
        """Install signal handlers that terminate all tracked processes on exit."""

        def _handler(signum: int, frame: object) -> None:
            logger.info(f"Received signal {signum}, terminating tracked processes")
            self.terminate_all()
            # Re-raise with original handler
            if (
                signum == signal.SIGINT
                and self._original_sigint
                and callable(self._original_sigint)
            ):
                self._original_sigint(signum, frame)
            raise SystemExit(128 + signum)

        self._original_sigint = signal.getsignal(signal.SIGINT)  # type: ignore[assignment]
        self._original_sigterm = signal.getsignal(signal.SIGTERM)  # type: ignore[assignment]
        signal.signal(signal.SIGINT, _handler)
        signal.signal(signal.SIGTERM, _handler)

    def restore_signal_handlers(self) -> None:
        """Restore the original signal handlers."""
        if self._original_sigint is not None:
            signal.signal(signal.SIGINT, self._original_sigint)
        if self._original_sigterm is not None:
            signal.signal(signal.SIGTERM, self._original_sigterm)

    @staticmethod
    def _is_alive(pid: int) -> bool:
        """Check if a process is still running."""
        try:
            os.kill(pid, 0)  # Signal 0 = existence check
            return True
        except OSError:
            return False

    def _load(self) -> list[ProcessRecord]:
        """Load existing process records from disk."""
        if not self._registry_file.exists():
            return []
        try:
            data = json.loads(self._registry_file.read_text())
            return [ProcessRecord.from_dict(r) for r in data.get("processes", [])]
        except (json.JSONDecodeError, OSError, TypeError) as e:
            logger.warning(f"Failed to load process registry: {e}")
            return []

    def _persist(self) -> None:
        """Write process records to disk atomically."""
        data = {
            "version": 1,
            "processes": [r.to_dict() for r in self._records],
        }
        write_atomic(self._registry_file, json.dumps(data, indent=2))
