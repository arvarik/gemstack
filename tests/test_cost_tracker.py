"""Tests for the cost tracker module."""

from __future__ import annotations

from pathlib import Path

import pytest

from gemstack.core.cost_tracker import (
    CostLimitExceeded,
    CostTracker,
    UsageRecord,
)


class TestUsageRecord:
    """Tests for the UsageRecord dataclass."""

    def test_roundtrip_serialization(self) -> None:
        record = UsageRecord(
            step="step1-spec",
            feature="notifications",
            model="gemini-2.5-flash",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.0005,
            timestamp=1234567890.0,
        )
        d = record.to_dict()
        restored = UsageRecord.from_dict(d)
        assert restored.step == record.step
        assert restored.cost_usd == record.cost_usd
        assert restored.timestamp == record.timestamp


class TestCostTracker:
    """Tests for the CostTracker class."""

    @pytest.fixture
    def project(self, tmp_path: Path) -> Path:
        (tmp_path / ".agent").mkdir()
        return tmp_path

    def test_record_creates_costs_file(self, project: Path) -> None:
        tracker = CostTracker(project)
        tracker.record(
            step="step1-spec",
            feature="test",
            model="gemini-2.5-flash",
            input_tokens=1000,
            output_tokens=500,
        )
        assert (project / ".agent" / "costs.json").exists()

    def test_record_persists_between_instances(self, project: Path) -> None:
        tracker1 = CostTracker(project)
        tracker1.record(
            step="step1-spec",
            feature="test",
            model="gemini-2.5-flash",
            input_tokens=1000,
            output_tokens=500,
        )

        tracker2 = CostTracker(project)
        summary = tracker2.get_summary()
        assert summary.record_count == 1
        assert summary.total_input_tokens == 1000

    def test_cost_calculation(self, project: Path) -> None:
        tracker = CostTracker(project)
        record = tracker.record(
            step="step1-spec",
            feature="test",
            model="gemini-2.5-flash",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
        )
        # Default: $0.15/M input + $0.60/M output = $0.75
        assert record.cost_usd == pytest.approx(0.75, abs=0.01)

    def test_summary_by_step(self, project: Path) -> None:
        tracker = CostTracker(project)
        tracker.record("step1-spec", "f1", "flash", 100, 50)
        tracker.record("step3-build", "f1", "flash", 200, 100)
        summary = tracker.get_summary()
        assert "step1-spec" in summary.by_step
        assert "step3-build" in summary.by_step

    def test_summary_filtered_by_feature(self, project: Path) -> None:
        tracker = CostTracker(project)
        tracker.record("step1-spec", "feature-a", "flash", 100, 50)
        tracker.record("step1-spec", "feature-b", "flash", 200, 100)
        summary = tracker.get_summary(feature="feature-a")
        assert summary.record_count == 1
        assert summary.total_input_tokens == 100

    def test_budget_enforcement_per_feature(self, project: Path) -> None:
        tracker = CostTracker(project, max_cost_per_feature=0.01)
        tracker.record("step1-spec", "expensive", "flash", 1_000_000, 500_000)
        with pytest.raises(CostLimitExceeded, match="limit"):
            tracker.check_budget("step2-trap", "expensive")

    def test_budget_enforcement_per_step_tokens(
        self, project: Path
    ) -> None:
        tracker = CostTracker(project, max_tokens_per_step=1000)
        tracker.record("step1-spec", "test", "flash", 800, 300)
        with pytest.raises(CostLimitExceeded, match="tokens"):
            tracker.check_budget("step1-spec", "test")

    def test_budget_passes_when_under_limit(self, project: Path) -> None:
        tracker = CostTracker(project, max_cost_per_feature=100.0)
        tracker.record("step1-spec", "test", "flash", 100, 50)
        tracker.check_budget("step2-trap", "test")  # Should not raise

    def test_reset_all(self, project: Path) -> None:
        tracker = CostTracker(project)
        tracker.record("step1-spec", "test", "flash", 100, 50)
        tracker.record("step2-trap", "test", "flash", 200, 100)
        removed = tracker.reset()
        assert removed == 2
        assert tracker.get_summary().record_count == 0

    def test_reset_by_feature(self, project: Path) -> None:
        tracker = CostTracker(project)
        tracker.record("step1-spec", "keep", "flash", 100, 50)
        tracker.record("step1-spec", "remove", "flash", 200, 100)
        removed = tracker.reset(feature="remove")
        assert removed == 1
        assert tracker.get_summary().record_count == 1

    def test_corrupted_file_graceful_fallback(self, project: Path) -> None:
        costs_file = project / ".agent" / "costs.json"
        costs_file.write_text("not json {{")
        tracker = CostTracker(project)
        assert tracker.get_summary().record_count == 0
