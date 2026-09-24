from repoguard.benchmark import BenchmarkTask, summarize_records
from repoguard.experiments import ExperimentRecord


def test_summary_metrics():
    records = [
        ExperimentRecord.create(
            experiment_id="x",
            task_id="1",
            model_id="m",
            model_variant="base",
            prompt_version="v0.5",
            status="fixed",
            tests_passed=True,
            steps=4,
            files_touched=["a.py"],
            proposals_created=1,
            proposals_approved=1,
            proposals_rejected=0,
            human_intervention_required=True,
            latency_seconds=2.0,
        ),
        ExperimentRecord.create(
            experiment_id="x",
            task_id="2",
            model_id="m",
            model_variant="base",
            prompt_version="v0.5",
            status="not_fixed",
            tests_passed=False,
            steps=6,
            files_touched=[],
            proposals_created=0,
            proposals_approved=0,
            proposals_rejected=0,
            human_intervention_required=False,
            latency_seconds=4.0,
        ),
    ]

    summary = summarize_records(records)
    assert summary["tasks"] == 2
    assert summary["fix_rate"] == 0.5
    assert summary["test_pass_rate"] == 0.5
    assert summary["avg_steps"] == 5
    assert summary["avg_latency_seconds"] == 3.0
    assert summary["human_intervention_rate"] == 0.5
