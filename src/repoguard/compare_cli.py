from __future__ import annotations

import argparse
import json

from .reports import generate_comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repoguard-compare",
        description="Compare RepoGuard benchmark experiment logs.",
    )
    parser.add_argument("logs", nargs="+", help="One or more benchmark JSONL files")
    parser.add_argument("--csv-out", default="artifacts/comparison.csv")
    parser.add_argument("--markdown-out", default="artifacts/comparison.md")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rows = generate_comparison(
        args.logs,
        csv_path=args.csv_out,
        markdown_path=args.markdown_out,
    )
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
