from __future__ import annotations

import platform
import shutil
import sys


def main() -> int:
    print("Palm92 RepoGuard v0.7 preflight")
    print("=" * 40)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Git: {shutil.which('git') or 'not found'}")

    try:
        import torch
    except ImportError:
        print("Torch: not installed")
        print("Install project Gemma dependencies before running the baseline.")
        return 1

    print(f"Torch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if not torch.cuda.is_available():
        print("No CUDA GPU detected. Use a Kaggle or Colab GPU runtime for Gemma 4 12B.")
        return 2

    count = torch.cuda.device_count()
    print(f"GPU count: {count}")
    total_gb = 0.0
    for index in range(count):
        props = torch.cuda.get_device_properties(index)
        gb = props.total_memory / (1024 ** 3)
        total_gb += gb
        print(f"GPU {index}: {props.name}, {gb:.1f} GB")

    print(f"Combined visible GPU memory: {total_gb:.1f} GB")
    if total_gb < 24:
        print(
            "Warning: the official Gemma 4 12B weights are about 24 GB. "
            "device_map='auto' may need CPU offload or a larger/multi-GPU runtime."
        )
    else:
        print("GPU memory looks suitable for attempting the baseline.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
