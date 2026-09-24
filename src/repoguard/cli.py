from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import RepoGuardAgent
from .models import MockModelAdapter, TransformersGemmaAdapter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repoguard",
        description="Investigate a software issue with the Palm92 RepoGuard agent.",
    )
    parser.add_argument("repo", help="Path to the repository to investigate")
    parser.add_argument("issue", help="Natural-language software issue")
    parser.add_argument(
        "--backend",
        choices=("mock", "gemma"),
        default="mock",
        help="Model backend. Use mock for a zero-download smoke test.",
    )
    parser.add_argument(
        "--model-id",
        default="google/gemma-4-E4B-it",
        help="Hugging Face Gemma model id when --backend gemma is selected.",
    )
    parser.add_argument(
        "--audit-out",
        default="repoguard-audit.json",
        help="Path for the generated audit JSON.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo = Path(args.repo).resolve()

    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repository path does not exist: {repo}")

    if args.backend == "gemma":
        model = TransformersGemmaAdapter(model_id=args.model_id)
    else:
        model = MockModelAdapter()

    agent = RepoGuardAgent(str(repo), model)
    result = agent.investigate(args.issue)

    print("\n=== RepoGuard Investigation ===\n")
    print(result.model_response)
    print("\n=== Governance ===")
    print(f"Human approval required: {result.approval_required}")

    Path(args.audit_out).write_text(
        json.dumps(result.audit, indent=2),
        encoding="utf-8",
    )
    print(f"Audit written to: {args.audit_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
