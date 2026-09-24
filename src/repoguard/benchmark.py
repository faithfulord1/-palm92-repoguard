from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import statistics
import tempfile
import time
from typing import Callable, Any

from .agent import RepoGuardAgent
from .experiments import ExperimentLogger, ExperimentRecord


@dataclass
class BenchmarkTask:
    task_id: str
    repo_path: str
    issue: str
    metadata: dict[str, Any]


@dataclass
class BenchmarkConfig:
    experiment_id: str
    model_id: str
    model_variant: str
    prompt_version: str
    max_steps: int = 12
    isolate_repositories: bool = True
    approval_policy: str = "auto_low_risk"


class BenchmarkRunner:
    """Run repeatable benchmark tasks with optional repository isolation."""

    def __init__(
        self,
        *,
        config: BenchmarkConfig,
        model_factory: Callable[[], object],
        log_path: str | Path,
    ) -> None:
        self.config = config
        self.model_factory = model_factory
        self.logger = ExperimentLogger(log_path)

    def _run_in_repo(self, task: BenchmarkTask, repo_path: Path) -> ExperimentRecord:
        model = self.model_factory()
        agent = RepoGuardAgent(str(repo_path), model)

        started = time.perf_counter()
        result = agent.repair(
            task.issue,
            max_steps=self.config.max_steps,
            approval_policy=self.config.approval_policy,
        )
        elapsed = time.perf_counter() - started

        pending = agent.pending_changes()
        events = result.audit.get("events", [])

        proposals_created = sum(
            1 for event in events if event.get("event_type") == "change_proposed"
        )
        proposals_approved = sum(
            1 for event in events if event.get("event_type") == "change_approved"
        )
        proposals_rejected = sum(
            1 for event in events if event.get("event_type") == "change_rejected"
        )

        tests_passed = None
        if result.tests is not None:
            tests_passed = result.tests.get("returncode") == 0

        record = ExperimentRecord.create(
            experiment_id=self.config.experiment_id,
            task_id=task.task_id,
            model_id=self.config.model_id,
            model_variant=self.config.model_variant,
            prompt_version=self.config.prompt_version,
            status=result.status,
            tests_passed=tests_passed,
            steps=result.steps,
            files_touched=result.touched_files,
            proposals_created=proposals_created,
            proposals_approved=proposals_approved,
            proposals_rejected=proposals_rejected,
            human_intervention_required=bool(pending) or result.approval_required,
            latency_seconds=round(elapsed, 4),
            metadata={
                **task.metadata,
                "isolation_enabled": self.config.isolate_repositories,
                "approval_policy": self.config.approval_policy,
            },
        )
        self.logger.append(record)
        return record

    def run_task(self, task: BenchmarkTask) -> ExperimentRecord:
        source = Path(task.repo_path).resolve()
        if not source.exists() or not source.is_dir():
            raise FileNotFoundError(f"Benchmark repository not found: {source}")

        if not self.config.isolate_repositories:
            return self._run_in_repo(task, source)

        with tempfile.TemporaryDirectory(prefix=f"repoguard-{task.task_id}-") as temp_dir:
            destination = Path(temp_dir) / "repo"
            shutil.copytree(source, destination)
            return self._run_in_repo(task, destination)

    def run_suite(self, tasks: list[BenchmarkTask]) -> list[ExperimentRecord]:
        return [self.run_task(task) for task in tasks]


def load_tasks(path: str | Path) -> list[BenchmarkTask]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        BenchmarkTask(
            task_id=item["task_id"],
            repo_path=item["repo_path"],
            issue=item["issue"],
            metadata=item.get("metadata", {}),
        )
        for item in data["tasks"]
    ]


def summarize_records(records: list[ExperimentRecord]) -> dict[str, Any]:
    total = len(records)
    if total == 0:
        return {
            "tasks": 0,
            "fixed": 0,
            "fix_rate": 0.0,
            "test_pass_rate": None,
            "avg_steps": None,
            "avg_latency_seconds": None,
            "human_intervention_rate": 0.0,
        }

    fixed = sum(1 for r in records if r.status == "fixed")
    tested = [r for r in records if r.tests_passed is not None]
    test_passes = sum(1 for r in tested if r.tests_passed)

    return {
        "tasks": total,
        "fixed": fixed,
        "fix_rate": round(fixed / total, 4),
        "test_pass_rate": (
            round(test_passes / len(tested), 4) if tested else None
        ),
        "avg_steps": round(statistics.mean(r.steps for r in records), 2),
        "avg_latency_seconds": round(
            statistics.mean(r.latency_seconds or 0.0 for r in records),
            4,
        ),
        "human_intervention_rate": round(
            sum(1 for r in records if r.human_intervention_required) / total,
            4,
        ),
        "proposals_created": sum(r.proposals_created for r in records),
        "proposals_approved": sum(r.proposals_approved for r in records),
        "proposals_rejected": sum(r.proposals_rejected for r in records),
    }


def write_summary(records: list[ExperimentRecord], path: str | Path) -> dict[str, Any]:
    summary = summarize_records(records)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
