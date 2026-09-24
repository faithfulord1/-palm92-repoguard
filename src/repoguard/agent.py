from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Protocol, Any

from .audit import AuditLedger
from .risk import assess_path_risk
from .tools import RepoTools
from .review import ApprovalQueue


class ModelAdapter(Protocol):
    def generate(self, *, system: str, prompt: str) -> str: ...


@dataclass
class AgentResult:
    issue: str
    files_considered: list[str]
    model_response: str
    approval_required: bool
    audit: dict[str, Any]


@dataclass
class RepairResult:
    issue: str
    status: str
    summary: str
    touched_files: list[str]
    tests: dict[str, object] | None
    approval_required: bool
    steps: int
    audit: dict[str, Any]


class RepoGuardAgent:
    def __init__(self, repo_root: str, model: ModelAdapter) -> None:
        self.tools = RepoTools(repo_root)
        self.model = model
        self.audit = AuditLedger()
        self.approvals = ApprovalQueue(self.tools)

    def investigate(self, issue: str) -> AgentResult:
        self.audit.record("issue_received", issue=issue)
        files = self.tools.list_files()
        self.audit.record("repository_scanned", file_count=len(files))

        prompt = f"""You are RepoGuard, a cautious software engineering agent.

Issue:
{issue}

Repository files:
{chr(10).join(files[:300])}

Return a concise structured response with:
1. likely relevant files
2. investigation plan
3. risks
4. next tool actions

Do not claim to have read files that have not been supplied.
"""
        response = self.model.generate(
            system="You are an evidence-driven repository debugging agent.",
            prompt=prompt,
        )
        self.audit.record("model_plan_generated", response=response)

        approval_required = any(
            assess_path_risk(path)["level"] == "high" for path in files
        )
        if approval_required:
            self.audit.record("human_gate_enabled", reason="Sensitive repository paths detected")

        return AgentResult(
            issue=issue,
            files_considered=files,
            model_response=response,
            approval_required=approval_required,
            audit=self.audit.to_dict(),
        )

    def repair(self, issue: str, *, max_steps: int = 12) -> RepairResult:
        files = self.tools.list_files()
        self.audit.record("repair_started", issue=issue, file_count=len(files))
        observations: list[dict[str, Any]] = []
        touched_files: list[str] = []
        last_tests: dict[str, object] | None = None
        approval_required = False

        system = """You are RepoGuard, an evidence-driven software repair agent.
Output exactly one JSON action per turn.

Allowed actions:
{"action":"list"}
{"action":"read","path":"relative/path.py"}
{"action":"search","query":"text"}
{"action":"test"}
{"action":"write","path":"relative/path.py","content":"COMPLETE replacement file content","reason":"why"}
{"action":"final","status":"fixed|blocked|not_fixed","summary":"concise summary"}

Rules:
- Read before editing.
- Prefer the smallest relevant change.
- Use test feedback before declaring success.
- Never invent tool output.
"""

        for step in range(1, max_steps + 1):
            prompt = json.dumps(
                {
                    "issue": issue,
                    "repository_files": files[:300],
                    "recent_observations": observations[-8:],
                    "touched_files": touched_files,
                },
                indent=2,
            )
            raw = self.model.generate(system=system, prompt=prompt)
            self.audit.record("model_action", step=step, raw=raw)

            try:
                action = json.loads(raw)
            except json.JSONDecodeError:
                observations.append({"type": "error", "message": "Invalid JSON action."})
                continue

            kind = action.get("action")
            if kind == "list":
                observation = {"type": "list", "files": files[:300]}
            elif kind == "read":
                path = str(action["path"])
                observation = {"type": "read", "path": path, "content": self.tools.read_file(path)}
            elif kind == "search":
                query = str(action["query"])
                observation = {"type": "search", "query": query, "hits": self.tools.search_text(query)}
            elif kind == "test":
                last_tests = self.tools.run_tests()
                observation = {"type": "test", **last_tests}
            elif kind == "write":
                path = str(action["path"])
                proposal = self.approvals.propose(
                    path,
                    str(action["content"]),
                    str(action.get("reason", "")),
                )
                approval_required = True
                observation = {
                    "type": "change_proposed",
                    "proposal_id": proposal.proposal_id,
                    "path": proposal.path,
                    "risk": proposal.risk,
                    "diff": proposal.diff,
                    "message": "Change staged. Human approval is required before applying it.",
                }
                self.audit.record(
                    "change_proposed",
                    proposal_id=proposal.proposal_id,
                    path=proposal.path,
                    risk=proposal.risk,
                )
            elif kind == "final":
                status = str(action.get("status", "not_fixed"))
                summary = str(action.get("summary", ""))
                self.audit.record("repair_finished", status=status, summary=summary, steps=step)
                return RepairResult(
                    issue=issue,
                    status=status,
                    summary=summary,
                    touched_files=touched_files,
                    tests=last_tests,
                    approval_required=approval_required,
                    steps=step,
                    audit=self.audit.to_dict(),
                )
            else:
                observation = {"type": "error", "message": f"Unknown action: {kind}"}

            observations.append(observation)
            self.audit.record("tool_observation", step=step, observation=observation)

        return RepairResult(
            issue=issue,
            status="max_steps_reached",
            summary="Agent stopped at the configured step limit.",
            touched_files=touched_files,
            tests=last_tests,
            approval_required=approval_required,
            steps=max_steps,
            audit=self.audit.to_dict(),
        )


    def approve_change(self, proposal_id: int) -> dict[str, Any]:
        proposal = self.approvals.approve(proposal_id)
        self.audit.record(
            "change_approved",
            proposal_id=proposal.proposal_id,
            path=proposal.path,
        )
        return proposal.to_dict()

    def reject_change(self, proposal_id: int) -> dict[str, Any]:
        proposal = self.approvals.reject(proposal_id)
        self.audit.record(
            "change_rejected",
            proposal_id=proposal.proposal_id,
            path=proposal.path,
        )
        return proposal.to_dict()

    def pending_changes(self) -> list[dict[str, Any]]:
        return [proposal.to_dict() for proposal in self.approvals.pending()]
