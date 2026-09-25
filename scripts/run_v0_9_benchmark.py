"""Run the RepoGuard v0.9 exploratory multi-file benchmark.

New task pack: do NOT compare headline rates directly to four-task v0.7/v0.8 data.
Refuses to overwrite evidence; one distinct experiment ID per run.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-id", default="medium-v001")
    args = parser.parse_args()
    if not args.experiment_id.replace("-", "").replace("_", "").isalnum():
        parser.error("experiment-id may contain only letters, numbers, hyphens, underscores")
    artifacts = ROOT / "artifacts" / "v0.9" / args.experiment_id
    if artifacts.exists():
        parser.error(f"Evidence destination already exists: {artifacts}. Choose a NEW experiment ID.")
    artifacts.mkdir(parents=True)

    cmd = [
        sys.executable, "-m", "repoguard.benchmark_cli",
        "benchmarks/v0.9_tasks.json",
        "--backend", "gemma",
        "--model-id", "google/gemma-4-E4B-it",
        "--variant", "e4b-4bit",
        "--experiment-id", args.experiment_id,
        "--prompt-version", "v0.9",
        "--approval-policy", "auto_low_risk",
        "--load-in-4bit",
        "--max-steps", "12",
        "--log-out", str(artifacts / "tasks.jsonl"),
        "--summary-out", str(artifacts / "summary.json"),
    ]
    print("Output:", artifacts, flush=True)
    print("Command:", " ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        print("Benchmark incomplete; preserve partial evidence and inspect logs.", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
