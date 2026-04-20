"""Cost tracking and circuit breaker for autonomous execution.

Tracks API token usage per step and per feature, enforces configurable
budget limits, and persists cost data to ``.agent/costs.json``.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from gemstack.utils.fileutil import write_atomic

logger = logging.getLogger(__name__)

# Gemini pricing (USD per 1M tokens) — gemini-2.5-flash defaults
_DEFAULT_INPUT_PRICE_PER_M = 0.15
_DEFAULT_OUTPUT_PRICE_PER_M = 0.60

# Default budget limits (opt-in — only enforced when set)
DEFAULT_MAX_COST_PER_FEATURE = 5.00  # USD
DEFAULT_MAX_TOKENS_PER_STEP = 500_000


class CostLimitExceeded(Exception):
    """Raised when a cost budget threshold is exceeded."""


@dataclass
class UsageRecord:
    """A single API call usage record."""

    step: str
    feature: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-safe dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UsageRecord:
        """Deserialize from dict."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CostSummary:
    """Aggregate cost summary."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    record_count: int = 0
    by_step: dict[str, float] = field(default_factory=dict)
    by_feature: dict[str, float] = field(default_factory=dict)


class CostTracker:
    """Tracks API costs and enforces budget limits.

    Usage records are persisted to ``.agent/costs.json`` so they
    survive across runs. The circuit breaker is opt-in: it only
    triggers when explicit limits are configured.
    """

    def __init__(
        self,
        project_root: Path,
        *,
        max_cost_per_feature: float | None = None,
        max_tokens_per_step: int | None = None,
        input_price_per_m: float = _DEFAULT_INPUT_PRICE_PER_M,
        output_price_per_m: float = _DEFAULT_OUTPUT_PRICE_PER_M,
    ) -> None:
        self._project_root = project_root
        self._costs_file = project_root / ".agent" / "costs.json"
        self._max_cost_per_feature = max_cost_per_feature
        self._max_tokens_per_step = max_tokens_per_step
        self._input_price_per_m = input_price_per_m
        self._output_price_per_m = output_price_per_m
        self._records: list[UsageRecord] = self._load()

    def record(
        self,
        step: str,
        feature: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> UsageRecord:
        """Record a single API call and persist to disk.

        Args:
            step: Workflow step (e.g., "step1-spec").
            feature: Feature being worked on.
            model: Model name used.
            input_tokens: Number of input tokens consumed.
            output_tokens: Number of output tokens consumed.

        Returns:
            The created UsageRecord.
        """
        cost = self._calculate_cost(input_tokens, output_tokens)
        record = UsageRecord(
            step=step,
            feature=feature,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
        self._records.append(record)
        self._persist()
        return record

    def check_budget(self, step: str, feature: str) -> None:
        """Check if executing a step would violate budget constraints.

        Raises:
            CostLimitExceeded: If a budget threshold has been exceeded.
        """
        if self._max_cost_per_feature is not None:
            feature_cost = sum(r.cost_usd for r in self._records if r.feature == feature)
            if feature_cost >= self._max_cost_per_feature:
                raise CostLimitExceeded(
                    f"Feature '{feature}' has spent ${feature_cost:.2f} "
                    f"(limit: ${self._max_cost_per_feature:.2f}). "
                    f"Increase --max-cost or reset costs."
                )

        if self._max_tokens_per_step is not None:
            step_tokens = sum(
                r.input_tokens + r.output_tokens
                for r in self._records
                if r.step == step and r.feature == feature
            )
            if step_tokens >= self._max_tokens_per_step:
                raise CostLimitExceeded(
                    f"Step '{step}' for '{feature}' has used {step_tokens:,} "
                    f"tokens (limit: {self._max_tokens_per_step:,}). "
                    f"Reset costs or raise the limit."
                )

    def get_summary(self, feature: str | None = None) -> CostSummary:
        """Get an aggregate cost summary, optionally filtered by feature."""
        records = self._records
        if feature:
            records = [r for r in records if r.feature == feature]

        summary = CostSummary(record_count=len(records))
        for r in records:
            summary.total_input_tokens += r.input_tokens
            summary.total_output_tokens += r.output_tokens
            summary.total_cost_usd += r.cost_usd
            summary.by_step[r.step] = summary.by_step.get(r.step, 0.0) + r.cost_usd
            summary.by_feature[r.feature] = summary.by_feature.get(r.feature, 0.0) + r.cost_usd
        return summary

    def reset(self, feature: str | None = None) -> int:
        """Clear cost records, optionally only for a specific feature.

        Returns the number of records removed.
        """
        if feature:
            before = len(self._records)
            self._records = [r for r in self._records if r.feature != feature]
            removed = before - len(self._records)
        else:
            removed = len(self._records)
            self._records = []
        self._persist()
        return removed

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate USD cost from token counts."""
        input_cost = (input_tokens / 1_000_000) * self._input_price_per_m
        output_cost = (output_tokens / 1_000_000) * self._output_price_per_m
        return round(input_cost + output_cost, 6)

    def _load(self) -> list[UsageRecord]:
        """Load existing cost records from disk."""
        if not self._costs_file.exists():
            return []
        try:
            data = json.loads(self._costs_file.read_text())
            return [UsageRecord.from_dict(r) for r in data.get("records", [])]
        except (json.JSONDecodeError, OSError, TypeError, KeyError) as e:
            logger.warning(f"Failed to load costs.json: {e}")
            return []

    def _persist(self) -> None:
        """Write cost records to disk atomically."""
        data = {
            "version": 1,
            "records": [r.to_dict() for r in self._records],
        }
        write_atomic(self._costs_file, json.dumps(data, indent=2))
