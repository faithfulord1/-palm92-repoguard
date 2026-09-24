import json

from repoguard.experiments import ExperimentLogger, ExperimentRecord


def test_experiment_logger(tmp_path):
    path = tmp_path / "runs.jsonl"
    logger = ExperimentLogger(path)
    record = ExperimentRecord.create(
        experiment_id="tools-v001",
        task_id="demo-001",
        model_id="google/gemma-4-12B-it",
        model_variant="base",
        prompt_version="v0.4",
        status="fixed",
        tests_passed=True,
        steps=6,
        files_touched=["src/app.py"],
        proposals_created=1,
        proposals_approved=1,
        proposals_rejected=0,
        human_intervention_required=True,
        latency_seconds=12.5,
    )
    logger.append(record)

    saved = json.loads(path.read_text(encoding="utf-8").strip())
    assert saved["task_id"] == "demo-001"
    assert saved["tests_passed"] is True
    assert saved["proposals_approved"] == 1
