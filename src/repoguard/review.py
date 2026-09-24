from __future__ import annotations

from dataclasses import asdict, dataclass
import difflib
from pathlib import Path
from typing import Any

from .risk import assess_path_risk
from .tools import RepoTools


@dataclass
class ChangeProposal:
    proposal_id: int
    path: str
    reason: str
    original_content: str
    proposed_content: str
    diff: str
    risk: dict[str, str]
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ApprovalQueue:
    """Stages proposed file replacements and requires an explicit decision."""

    def __init__(self, tools: RepoTools) -> None:
        self.tools = tools
        self._proposals: dict[int, ChangeProposal] = {}
        self._next_id = 1

    def propose(self, path: str, proposed_content: str, reason: str = "") -> ChangeProposal:
        try:
            original = self.tools.read_file(path, max_chars=1_000_000)
        except FileNotFoundError:
            original = ""

        diff = "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                proposed_content.splitlines(keepends=True),
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
            )
        )
        proposal = ChangeProposal(
            proposal_id=self._next_id,
            path=path,
            reason=reason,
            original_content=original,
            proposed_content=proposed_content,
            diff=diff,
            risk=assess_path_risk(path),
        )
        self._proposals[proposal.proposal_id] = proposal
        self._next_id += 1
        return proposal

    def get(self, proposal_id: int) -> ChangeProposal:
        return self._proposals[proposal_id]

    def pending(self) -> list[ChangeProposal]:
        return [p for p in self._proposals.values() if p.status == "pending"]

    def approve(self, proposal_id: int) -> ChangeProposal:
        proposal = self.get(proposal_id)
        if proposal.status != "pending":
            raise ValueError(f"Proposal {proposal_id} is already {proposal.status}")
        self.tools.write_file(proposal.path, proposal.proposed_content)
        proposal.status = "approved"
        return proposal

    def reject(self, proposal_id: int) -> ChangeProposal:
        proposal = self.get(proposal_id)
        if proposal.status != "pending":
            raise ValueError(f"Proposal {proposal_id} is already {proposal.status}")
        proposal.status = "rejected"
        return proposal
