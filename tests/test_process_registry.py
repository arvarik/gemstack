"""Tests for the process registry module."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from gemstack.platform.process_registry import ProcessRecord, ProcessRegistry


class TestProcessRecord:
    """Tests for the ProcessRecord dataclass."""

    def test_roundtrip_serialization(self) -> None:
        record = ProcessRecord(
            pid=12345,
            step="step1-spec",
            feature="test",
            started_at=1234567890.0,
        )
        d = record.to_dict()
        restored = ProcessRecord.from_dict(d)
        assert restored.pid == record.pid
        assert restored.step == record.step


class TestProcessRegistry:
    """Tests for the ProcessRegistry class."""

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        (tmp_path / ".agent").mkdir()
        return tmp_path

    def test_register_creates_file(self, project: Path) -> None:
        registry = ProcessRegistry(project)
        registry.register(pid=99999, step="step1-spec", feature="test")
        assert (project / ".agent" / ".processes.json").exists()

    def test_register_and_retrieve(self, project: Path) -> None:
        registry = ProcessRegistry(project)
        registry.register(pid=os.getpid(), step="step1-spec", feature="test")
        active = registry.get_active()
        # Current process is alive
        assert len(active) == 1
        assert active[0].pid == os.getpid()

    def test_stale_process_detected(self, project: Path) -> None:
        registry = ProcessRegistry(project)
        # Use a PID that almost certainly doesn't exist
        registry.register(pid=2147483647, step="step1-spec", feature="test")
        active = registry.get_active()
        assert len(active) == 0

    def test_cleanup_stale(self, project: Path) -> None:
        registry = ProcessRegistry(project)
        registry.register(pid=2147483647, step="step1-spec", feature="test")
        # get_active updates statuses
        registry.get_active()
        cleaned = registry.cleanup_stale()
        # Even if no records removed (kept for history), no crash
        assert isinstance(cleaned, int)

    def test_terminate_all_nonexistent(self, project: Path) -> None:
        registry = ProcessRegistry(project)
        registry.register(pid=2147483647, step="step1-spec", feature="test")
        count = registry.terminate_all()
        # Process doesn't exist, so it gets marked completed not terminated
        assert count == 0

    def test_persistence_between_instances(self, project: Path) -> None:
        registry1 = ProcessRegistry(project)
        registry1.register(pid=os.getpid(), step="step1-spec", feature="test")

        registry2 = ProcessRegistry(project)
        active = registry2.get_active()
        assert len(active) == 1

    def test_corrupted_file_graceful(self, project: Path) -> None:
        (project / ".agent" / ".processes.json").write_text("bad json")
        registry = ProcessRegistry(project)
        assert registry.get_active() == []

    def test_signal_handlers_install_restore(self, project: Path) -> None:
        import signal

        registry = ProcessRegistry(project)
        original = signal.getsignal(signal.SIGINT)
        registry.install_signal_handlers()
        # Handler should be changed
        assert signal.getsignal(signal.SIGINT) != original
        registry.restore_signal_handlers()
        # Should be restored
        assert signal.getsignal(signal.SIGINT) == original
