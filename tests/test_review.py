from pathlib import Path

from repoguard.review import ApprovalQueue
from repoguard.tools import RepoTools


def test_patch_preview_and_approval(tmp_path: Path):
    target = tmp_path / "app.py"
    target.write_text("value = 1\n", encoding="utf-8")

    queue = ApprovalQueue(RepoTools(tmp_path))
    proposal = queue.propose("app.py", "value = 2\n", "Update value")

    assert "-value = 1" in proposal.diff
    assert "+value = 2" in proposal.diff
    assert target.read_text(encoding="utf-8") == "value = 1\n"

    queue.approve(proposal.proposal_id)
    assert target.read_text(encoding="utf-8") == "value = 2\n"


def test_reject_leaves_file_unchanged(tmp_path: Path):
    target = tmp_path / "app.py"
    target.write_text("value = 1\n", encoding="utf-8")

    queue = ApprovalQueue(RepoTools(tmp_path))
    proposal = queue.propose("app.py", "value = 9\n", "Reject demo")
    queue.reject(proposal.proposal_id)

    assert target.read_text(encoding="utf-8") == "value = 1\n"
