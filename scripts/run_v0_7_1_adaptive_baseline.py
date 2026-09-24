from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


def gpu_memory_gb() -> float:
    try:
        import torch
    except ImportError:
        return 0.0
    if not torch.cuda.is_available():
        return 0.0
    return sum(
        torch.cuda.get_device_properties(i).total_memory
        for i in range(torch.cuda.device_count())
    ) / (1024 ** 3)


def choose_model(requested: str) -> str:
    if requested != "auto":
        return requested

    memory = gpu_memory_gb()
    if memory >= 18:
        return "google/gemma-4-E4B-it"
    if memory >= 11:
        return "google/gemma-4-E2B-it"
    raise SystemExit(
        "No suitable CUDA GPU detected. "
        "Reconnect with a GPU or use the Kaggle GPU route."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="auto",
        choices=("auto", "google/gemma-4-E4B-it", "google/gemma-4-E2B-it"),
    )
    args = parser.parse_args()

    model_id = choose_model(args.model)
    model_slug = "e4b" if "E4B" in model_id else "e2b"

    artifacts = Path("artifacts/v0.7.1")
    artifacts.mkdir(parents=True, exist_ok=True)

    command = [
        "repoguard-benchmark",
        "benchmarks/v0.6_tasks.json",
        "--backend", "gemma",
        "--model-id", model_id,
        "--variant", "base",
        "--experiment-id", f"baseline-{model_slug}-v001",
        "--prompt-version", "v0.7.1",
        "--approval-policy", "auto_low_risk",
        "--log-out", str(artifacts / f"baseline-{model_slug}-v001.jsonl"),
        "--summary-out", str(artifacts / f"baseline-{model_slug}-v001-summary.json"),
    ]

    print("Selected model:", model_id)
    print("$", " ".join(command))
    subprocess.run(command, check=True)

    summary_path = artifacts / f"baseline-{model_slug}-v001-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    print("\nBaseline complete")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
