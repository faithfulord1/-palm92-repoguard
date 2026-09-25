"""One-task diagnostic for the unsuccessful v0.9 medium-v001 run.

Writes the full agent audit event stream to a NEW, separate folder. Use the
Gemma T4 notebook and inspect outputs before making architecture changes.
No production repository is modified; the fixture is copied to a temp dir.
The full audit may contain model text and source contents: review before sharing.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import tempfile

from repoguard.agent import RepoGuardAgent
from repoguard.models import TransformersGemmaAdapter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmarks" / "repos" / "v0_9_invoice"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-id", default="diagnostic-v001")
    parser.add_argument("--max-steps", type=int, default=6)
    args = parser.parse_args()
    if (
        not args.experiment_id
        or not args.experiment_id.replace("_", "").replace("-", "").isalnum()
    ):
        parser.error("Use a simple, non-empty experiment ID containing letters, digits, - or _")
    if args.max_steps < 1 or args.max_steps > 12:
        parser.error("max-steps must be from 1 to 12")

    output = ROOT / "artifacts" / "v0.9" / args.experiment_id
    if output.exists():
        parser.error(f"Evidence path already exists: {output}; choose a NEW ID")
    output.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="repoguard-v0.9-diagnostic-") as temp:
        worktree = Path(temp) / "repo"
        shutil.copytree(SOURCE, worktree)
        agent = RepoGuardAgent(
            str(worktree),
            TransformersGemmaAdapter(
                model_id="google/gemma-4-E4B-it",
                load_in_4bit=True,
            ),
        )
        try:
            result = agent.repair(
                "Invoice totals are incorrect when a line has quantity greater "
                "than one and a percentage discount. Follow tests/test_invoice.py: "
                "compute each discounted line subtotal from unit price, quantity, "
                "and discount, round once per line with Decimal ROUND_HALF_UP, "
                "then sum the lines. Preserve the public invoice_total API.",
                max_steps=args.max_steps,
                approval_policy="auto_low_risk",
            )
        finally:
            audit = agent.audit.to_dict()
            (output / "audit.json").write_text(
                json.dumps(audit, indent=2, default=str),
                encoding="utf-8",
            )
        (output / "result.json").write_text(
            json.dumps(asdict(result), indent=2, default=str),
            encoding="utf-8",
        )

    events = audit.get("events", [])
    counts = dict(Counter(event.get("event_type") for event in events))
    (output / "event-counts.json").write_text(
        json.dumps(counts, indent=2),
        encoding="utf-8",
    )
    print("Diagnostic result:", result.status, flush=True)
    print("Events:", json.dumps(counts, indent=2), flush=True)
    print("Audit saved:", output / "audit.json", flush=True)
    print("Read the agent model_action entries in audit.json. A failed task is "
          "a valid diagnostic outcome; do not overwrite evidence.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
