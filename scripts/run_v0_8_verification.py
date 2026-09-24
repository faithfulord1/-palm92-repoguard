from __future__ import annotations

import json
from pathlib import Path
import subprocess


MODEL_ID = "google/gemma-4-E4B-it"


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True)


def main() -> int:
    artifacts = Path("artifacts/v0.8")
    artifacts.mkdir(parents=True, exist_ok=True)

    run([
        "repoguard-benchmark",
        "benchmarks/v0.6_tasks.json",
        "--backend", "gemma",
        "--model-id", MODEL_ID,
        "--variant", "e4b-4bit",
        "--experiment-id", "verification-v001",
        "--prompt-version", "v0.8",
        "--approval-policy", "auto_low_risk",
        "--load-in-4bit",
        "--max-steps", "12",
        "--log-out", str(artifacts / "verification-v001.jsonl"),
        "--summary-out", str(artifacts / "verification-v001-summary.json"),
    ])

    run([
        "repoguard-compare",
        "artifacts/v0.7-lite/baseline-lite-v001.jsonl",
        str(artifacts / "verification-v001.jsonl"),
        "--csv-out", str(artifacts / "v0.7-vs-v0.8.csv"),
        "--markdown-out", str(artifacts / "v0.7-vs-v0.8.md"),
    ])

    summary = json.loads(
        (artifacts / "verification-v001-summary.json").read_text(encoding="utf-8")
    )
    print("\nRepoGuard v0.8 verification experiment complete")
    print(json.dumps(summary, indent=2))
    print("\nComparison written to artifacts/v0.8/v0.7-vs-v0.8.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
