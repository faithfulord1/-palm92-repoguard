from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .experiments import ExperimentRecord


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    source = Path(path)
    if not source.exists():
        return records
    for line in source.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def group_by_experiment(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        groups.setdefault(str(record["experiment_id"]), []).append(record)
    return groups


def summarize_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    tested = [r for r in records if r.get("tests_passed") is not None]
    fixed = sum(1 for r in records if r.get("status") == "fixed")
    test_passes = sum(1 for r in tested if r.get("tests_passed") is True)
    interventions = sum(
        1 for r in records if r.get("human_intervention_required") is True
    )
    latencies = [float(r.get("latency_seconds") or 0.0) for r in records]
    steps = [int(r.get("steps") or 0) for r in records]

    return {
        "tasks": total,
        "fixed": fixed,
        "fix_rate": round(fixed / total, 4) if total else 0.0,
        "test_pass_rate": round(test_passes / len(tested), 4) if tested else None,
        "avg_steps": round(sum(steps) / total, 2) if total else None,
        "avg_latency_seconds": round(sum(latencies) / total, 4) if total else None,
        "human_intervention_rate": round(interventions / total, 4) if total else 0.0,
        "proposals_created": sum(int(r.get("proposals_created") or 0) for r in records),
        "proposals_approved": sum(int(r.get("proposals_approved") or 0) for r in records),
        "proposals_rejected": sum(int(r.get("proposals_rejected") or 0) for r in records),
    }


def build_comparison(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for experiment_id, items in sorted(group_by_experiment(records).items()):
        summary = summarize_group(items)
        example = items[0]
        rows.append({
            "experiment_id": experiment_id,
            "model_id": example.get("model_id"),
            "model_variant": example.get("model_variant"),
            "prompt_version": example.get("prompt_version"),
            **summary,
        })
    return rows


def write_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        target.write_text("", encoding="utf-8")
        return
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "Experiment",
        "Model",
        "Variant",
        "Tasks",
        "Fix rate",
        "Test pass",
        "Avg steps",
        "Avg latency (s)",
        "Human intervention",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join([
                str(row["experiment_id"]),
                str(row.get("model_id") or ""),
                str(row.get("model_variant") or ""),
                str(row["tasks"]),
                f'{row["fix_rate"]:.2%}',
                "" if row["test_pass_rate"] is None else f'{row["test_pass_rate"]:.2%}',
                str(row["avg_steps"]),
                str(row["avg_latency_seconds"]),
                f'{row["human_intervention_rate"]:.2%}',
            ])
            + " |"
        )
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_comparison(
    jsonl_paths: list[str | Path],
    *,
    csv_path: str | Path,
    markdown_path: str | Path,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in jsonl_paths:
        records.extend(load_jsonl(path))
    rows = build_comparison(records)
    write_csv(rows, csv_path)
    write_markdown(rows, markdown_path)
    return rows
