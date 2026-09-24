from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


PRIMARY_MODEL = "google/gemma-4-E4B-it"
FALLBACK_MODEL = "google/gemma-4-E2B-it"


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True)


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


def main() -> int:
    artifacts = Path("artifacts/v0.7-lite")
    artifacts.mkdir(parents=True, exist_ok=True)

    visible_gb = gpu_memory_gb()
    if visible_gb <= 0:
        print("No CUDA GPU detected.")
        print("Use a Colab or Kaggle GPU runtime before running this script.")
        return 2

    model_id = PRIMARY_MODEL if visible_gb >= 14 else FALLBACK_MODEL
    variant = "e4b-4bit" if model_id == PRIMARY_MODEL else "e2b-4bit"

    print(f"Visible GPU memory: {visible_gb:.1f} GB")
    print(f"Selected model: {model_id}")

    run([
        "repoguard-benchmark",
        "benchmarks/v0.6_tasks.json",
        "--backend", "gemma",
        "--model-id", model_id,
        "--variant", variant,
        "--experiment-id", "baseline-lite-v001",
        "--prompt-version", "v0.7-lite",
        "--approval-policy", "auto_low_risk",
        "--load-in-4bit",
        "--log-out", str(artifacts / "baseline-lite-v001.jsonl"),
        "--summary-out", str(artifacts / "baseline-lite-v001-summary.json"),
    ])

    summary = json.loads(
        (artifacts / "baseline-lite-v001-summary.json").read_text(encoding="utf-8")
    )
    print("\nLite baseline complete")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
