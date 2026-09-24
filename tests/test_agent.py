from pathlib import Path

from repoguard.agent import RepoGuardAgent
from repoguard.models import MockModelAdapter


def test_agent_smoke_run(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )

    agent = RepoGuardAgent(str(tmp_path), MockModelAdapter())
    result = agent.investigate("Check the add function")

    assert "PLAN:" in result.model_response
    assert "app.py" in result.files_considered
    assert result.audit["events"][0]["event_type"] == "issue_received"


def test_sensitive_repo_enables_human_gate(tmp_path: Path):
    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "deploy.yml").write_text("name: deploy\n", encoding="utf-8")

    agent = RepoGuardAgent(str(tmp_path), MockModelAdapter())
    result = agent.investigate("Change deployment behavior")

    assert result.approval_required is True
