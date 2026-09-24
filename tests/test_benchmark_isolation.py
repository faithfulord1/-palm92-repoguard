from pathlib import Path
import json

from repoguard.benchmark import BenchmarkConfig, BenchmarkRunner, BenchmarkTask


class FinalOnlyModel:
    def generate(self, *, system: str, prompt: str) -> str:
        return json.dumps({
            "action": "final",
            "status": "not_fixed",
            "summary": "No change made."
        })


def test_benchmark_isolation_preserves_source(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("value = 1\n", encoding="utf-8")

    runner = BenchmarkRunner(
        config=BenchmarkConfig(
            experiment_id="test",
            model_id="mock",
            model_variant="base",
            prompt_version="v0.6",
            isolate_repositories=True,
        ),
        model_factory=FinalOnlyModel,
        log_path=tmp_path / "runs.jsonl",
    )
    task = BenchmarkTask(
        task_id="t1",
        repo_path=str(repo),
        issue="Do nothing",
        metadata={},
    )
    runner.run_task(task)

    assert target.read_text(encoding="utf-8") == "value = 1\n"
