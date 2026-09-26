"""Confirm each v0.9 benchmark starts with a reproducible failing test.

This is a negative-control check: every fixture MUST fail before repair.
It does not claim that an agent can repair the tasks.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ("v0_9_invoice", "v0_9_pagination", "v0_9_permissions")


def main() -> int:
    problems = []
    for fixture in FIXTURES:
        folder = ROOT / "benchmarks" / "repos" / fixture
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=folder, capture_output=True, text=True, timeout=90, check=False,
        )
        print(f"{fixture}: exit={result.returncode}")
        print((result.stdout + result.stderr)[-2500:])
        # Exit 1 means at least one assertion failed; other exit codes can mean collection errors.
        if result.returncode != 1 or "failed" not in result.stdout:
            problems.append(fixture)
    if problems:
        print("Fixture validation failed:", ", ".join(problems))
        return 1
    print("Fixture baseline validated: all three tasks begin with failing tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
