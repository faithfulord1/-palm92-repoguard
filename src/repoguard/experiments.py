from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


@dataclass
class ExperimentRecord:
    experiment_id: str
    task_id: str
    model_id: str
    model_variant: str
    prompt_version: str
    status: str
    tests_passed: bool | None
    steps: int
    files_touched: list[str]
    proposals_created: int
    proposals_approved: int
    proposals_rejected: int
    human_intervention_required: bool
    latency_seconds: float | None
    metadata: dict[str, Any]
    timestamp: str

    @classmethod
    def create(
        cls,
        *,
        experiment_id: str,
        task_id: str,
        model_id: str,
        model_variant: str,
        prompt_version: str,
        status: str,
        tests_passed: bool | None,
        steps: int,
        files_touched: list[str],
        proposals_created: int,
        proposals_approved: int,
        proposals_rejected: int,
        human_intervention_required: bool,
        latency_seconds: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "ExperimentRecord":
        return cls(
            experiment_id=experiment_id,
            task_id=task_id,
            model_id=model_id,
            model_variant=model_variant,
            prompt_version=prompt_version,
            status=status,
            tests_passed=tests_passed,
            steps=steps,
            files_touched=files_touched,
            proposals_created=proposals_created,
            proposals_approved=proposals_approved,
            proposals_rejected=proposals_rejected,
            human_intervention_required=human_intervention_required,
            latency_seconds=latency_seconds,
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


class ExperimentLogger:
    """Append-only JSONL logger for competition runs."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, record: ExperimentRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
