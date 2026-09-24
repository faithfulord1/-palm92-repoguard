from __future__ import annotations

import json
import platform
import shutil
import sys


def inspect_runtime() -> dict[str, object]:
    info: dict[str, object] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "git": shutil.which("git"),
        "cuda_available": False,
        "gpus": [],
        "recommended_model": "google/gemma-4-E2B-it",
    }

    try:
        import torch
    except ImportError:
        info["torch"] = None
        return info

    info["torch"] = torch.__version__
    info["cuda_available"] = torch.cuda.is_available()

    if torch.cuda.is_available():
        total_gb = 0.0
        gpus = []
        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)
            gb = props.total_memory / (1024 ** 3)
            total_gb += gb
            gpus.append({"index": index, "name": props.name, "memory_gb": round(gb, 1)})
        info["gpus"] = gpus
        info["visible_gpu_memory_gb"] = round(total_gb, 1)

        if total_gb >= 18:
            info["recommended_model"] = "google/gemma-4-E4B-it"
        elif total_gb >= 11:
            info["recommended_model"] = "google/gemma-4-E2B-it"
        else:
            info["recommended_model"] = None

    return info


def main() -> int:
    info = inspect_runtime()
    print("Palm92 RepoGuard v0.7.1 adaptive preflight")
    print("=" * 48)
    print(json.dumps(info, indent=2))

    model = info.get("recommended_model")
    if info.get("cuda_available") and model:
        print(f"\nRecommended real baseline model: {model}")
        return 0

    print(
        "\nNo suitable CUDA GPU is currently available. "
        "Do not start the real model download in this runtime. "
        "Try reconnecting later or use a Kaggle GPU notebook."
    )
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
