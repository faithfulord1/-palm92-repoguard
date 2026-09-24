from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any

from .audit import AuditLedger
from .risk import assess_path_risk
from .tools import RepoTools

class ModelAdapter(Protocol):
    def generate(self, *, system: str, prompt: str) -> str: ...

@dataclass
class AgentResult:
    issue: str
    files_considered: list[str]
    model_response: str
    approval_required: bool
    audit: dict[str, Any]

class RepoGuardAgent:
    def __init__(self, repo_root: str, model: ModelAdapter) -> None:
        self.tools = RepoTools(repo_root)
        self.model = model
        self.audit = AuditLedger()

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
