from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True)


def main() -> int:
    artifacts = Path("artifacts/v0.7")
    artifacts.mkdir(parents=True, exist_ok=True)

    run([sys.executable, "scripts/v0_7_preflight.py"])

    run([
        "repoguard-benchmark",
        "benchmarks/v0.6_tasks.json",
        "--backend", "gemma",
        "--model-id", "google/gemma-4-12B-it",
        "--variant", "base",
        "--experiment-id", "baseline-v001",
        "--prompt-version", "v0.7",
        "--approval-policy", "auto_low_risk",
        "--log-out", str(artifacts / "baseline-v001.jsonl"),
        "--summary-out", str(artifacts / "baseline-v001-summary.json"),
    ])

    summary = json.loads(
        (artifacts / "baseline-v001-summary.json").read_text(encoding="utf-8")
    )
    print("\nBaseline complete")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
