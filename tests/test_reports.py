from repoguard.reports import build_comparison


def test_build_comparison_groups_experiments():
    records = [
        {
            "experiment_id": "baseline",
            "model_id": "m1",
            "model_variant": "base",
            "prompt_version": "v0.6",
            "status": "fixed",
            "tests_passed": True,
            "steps": 4,
            "latency_seconds": 2.0,
            "human_intervention_required": False,
            "proposals_created": 0,
            "proposals_approved": 0,
            "proposals_rejected": 0,
        },
        {
            "experiment_id": "baseline",
            "model_id": "m1",
            "model_variant": "base",
            "prompt_version": "v0.6",
            "status": "not_fixed",
            "tests_passed": False,
            "steps": 6,
            "latency_seconds": 4.0,
            "human_intervention_required": True,
            "proposals_created": 1,
            "proposals_approved": 0,
            "proposals_rejected": 0,
        },
    ]
    rows = build_comparison(records)

    assert len(rows) == 1
    assert rows[0]["experiment_id"] == "baseline"
    assert rows[0]["fix_rate"] == 0.5
    assert rows[0]["avg_steps"] == 5.0
    assert rows[0]["human_intervention_rate"] == 0.5
