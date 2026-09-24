from __future__ import annotations

import argparse
import json

from .benchmark import BenchmarkConfig, BenchmarkRunner, load_tasks, write_summary
from .models import MockModelAdapter, TransformersGemmaAdapter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repoguard-benchmark",
        description="Run a repeatable RepoGuard competition benchmark suite.",
    )
    parser.add_argument("tasks", help="Path to benchmark tasks JSON")
    parser.add_argument("--backend", choices=("mock", "gemma"), default="mock")
    parser.add_argument("--model-id", default="google/gemma-4-12B-it")
    parser.add_argument("--variant", default="base")
    parser.add_argument("--experiment-id", default="baseline-v001")
    parser.add_argument("--prompt-version", default="v0.7")
    parser.add_argument("--max-steps", type=int, default=12)
    parser.add_argument(
        "--approval-policy",
        choices=("manual", "auto_low_risk"),
        default="auto_low_risk",
        help="Auto-approval is intended only for isolated benchmark copies.",
    )
    parser.add_argument("--log-out", default="artifacts/benchmark-runs.jsonl")
    parser.add_argument("--summary-out", default="artifacts/benchmark-summary.json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    tasks = load_tasks(args.tasks)

    if args.backend == "gemma":
        factory = lambda: TransformersGemmaAdapter(model_id=args.model_id)
    else:
        factory = lambda: MockModelAdapter()

    runner = BenchmarkRunner(
        config=BenchmarkConfig(
            experiment_id=args.experiment_id,
            model_id=args.model_id if args.backend == "gemma" else "mock",
            model_variant=args.variant,
            prompt_version=args.prompt_version,
            max_steps=args.max_steps,
            approval_policy=args.approval_policy,
        ),
        model_factory=factory,
        log_path=args.log_out,
    )

    records = runner.run_suite(tasks)
    summary = write_summary(records, args.summary_out)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
