from pathlib import Path

from repoguard.agent import RepoGuardAgent
from repoguard.models import MockModelAdapter, ScriptedModelAdapter


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


def test_auto_low_risk_write_runs_tests_and_stops_fixed(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        "def add(a, b):\n    return a - b\n",
        encoding="utf-8",
    )
    (tmp_path / "test_app.py").write_text(
        "from app import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    model = ScriptedModelAdapter(
        responses=[
            '{"action":"read","path":"app.py"}',
            '{"action":"write","path":"app.py","content":"def add(a, b):\\n    return a + b\\n","reason":"Correct arithmetic operator"}',
        ]
    )
    agent = RepoGuardAgent(str(tmp_path), model)
    result = agent.repair(
        "add(2, 3) should return 5",
        max_steps=12,
        approval_policy="auto_low_risk",
    )

    assert result.status == "fixed"
    assert result.steps == 2
    assert result.tests is not None
    assert result.tests["returncode"] == 0
    assert result.touched_files == ["app.py"]


def test_failed_post_write_test_is_returned_to_agent(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        "def add(a, b):\n    return a - b\n",
        encoding="utf-8",
    )
    (tmp_path / "test_app.py").write_text(
        "from app import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    model = ScriptedModelAdapter(
        responses=[
            '{"action":"read","path":"app.py"}',
            '{"action":"write","path":"app.py","content":"def add(a, b):\\n    return a * b\\n","reason":"First attempt"}',
            '{"action":"write","path":"app.py","content":"def add(a, b):\\n    return a + b\\n","reason":"Correct after test feedback"}',
        ]
    )
    agent = RepoGuardAgent(str(tmp_path), model)
    result = agent.repair(
        "add(2, 3) should return 5",
        max_steps=12,
        approval_policy="auto_low_risk",
    )

    assert result.status == "fixed"
    assert result.steps == 3
    assert result.tests is not None
    assert result.tests["returncode"] == 0
