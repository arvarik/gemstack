"""Tests for the eval runner."""

import json
from pathlib import Path

from gemstack.cli.eval_cmd import _discover_eval_sets, _run_eval_set


class TestEvalDiscovery:
    def test_discovers_eval_sets(self, tmp_path: Path) -> None:
        (tmp_path / "accuracy.json").write_text("{}")
        (tmp_path / "rouge.json").write_text("{}")

        sets = _discover_eval_sets(tmp_path)
        assert len(sets) == 2

    def test_excludes_holdout(self, tmp_path: Path) -> None:
        (tmp_path / "accuracy.json").write_text("{}")
        holdout = tmp_path / "holdout"
        holdout.mkdir()
        (holdout / "secret.json").write_text("{}")

        sets = _discover_eval_sets(tmp_path, exclude_holdout=True)
        assert len(sets) == 1
        assert all("holdout" not in s.parts for s in sets)

    def test_includes_holdout_when_allowed(self, tmp_path: Path) -> None:
        (tmp_path / "accuracy.json").write_text("{}")
        holdout = tmp_path / "holdout"
        holdout.mkdir()
        (holdout / "secret.json").write_text("{}")

        sets = _discover_eval_sets(tmp_path, exclude_holdout=False)
        assert len(sets) == 2


class TestEvalRunner:
    def test_perfect_accuracy(self, tmp_path: Path) -> None:
        eval_file = tmp_path / "test.json"
        eval_file.write_text(
            json.dumps(
                {
                    "name": "test-eval",
                    "metric": "accuracy",
                    "target": 0.9,
                    "cases": [
                        {"input": "a", "expected": "yes", "actual": "yes"},
                        {"input": "b", "expected": "no", "actual": "no"},
                    ],
                }
            )
        )

        result = _run_eval_set(eval_file)
        assert result["score"] == 1.0
        assert result["passed"]

    def test_partial_accuracy(self, tmp_path: Path) -> None:
        eval_file = tmp_path / "test.json"
        eval_file.write_text(
            json.dumps(
                {
                    "name": "test-eval",
                    "metric": "accuracy",
                    "target": 0.9,
                    "cases": [
                        {"input": "a", "expected": "yes", "actual": "yes"},
                        {"input": "b", "expected": "no", "actual": "yes"},
                    ],
                }
            )
        )

        result = _run_eval_set(eval_file)
        assert result["score"] == 0.5
        assert not result["passed"]

    def test_empty_cases(self, tmp_path: Path) -> None:
        eval_file = tmp_path / "test.json"
        eval_file.write_text(
            json.dumps(
                {
                    "name": "empty",
                    "metric": "accuracy",
                    "target": 0.9,
                    "cases": [],
                }
            )
        )

        result = _run_eval_set(eval_file)
        assert result["score"] == 0.0

    def test_metric_filter(self, tmp_path: Path) -> None:
        eval_file = tmp_path / "test.json"
        eval_file.write_text(
            json.dumps(
                {
                    "name": "test",
                    "metric": "rouge-l",
                    "target": 0.8,
                    "cases": [],
                }
            )
        )

        result = _run_eval_set(eval_file, metric_filter="accuracy")
        assert result.get("skipped")

    def test_invalid_json(self, tmp_path: Path) -> None:
        eval_file = tmp_path / "bad.json"
        eval_file.write_text("not json")

        result = _run_eval_set(eval_file)
        assert not result["passed"]
        assert "error" in result
