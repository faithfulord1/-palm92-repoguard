from __future__ import annotations

from dataclasses import dataclass
import json
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

    def repair(
        self,
        issue: str,
        *,
        max_steps: int = 12,
        allow_low_risk_writes: bool = True,
    ) -> RepairResult:
        """Run a bounded JSON-action loop.

        The model may request list/read/search/test/write/final actions.
        Sensitive writes are never applied automatically.
        """

        files = self.tools.list_files()
        self.audit.record("repair_started", issue=issue, file_count=len(files))

        observations: list[dict[str, Any]] = []
        touched_files: list[str] = []
        last_tests: dict[str, object] | None = None
        approval_required = False
        summary = ""
        status = "max_steps_reached"

        system = """You are RepoGuard, an evidence-driven software repair agent.
Choose exactly one action per turn and output ONLY valid JSON.

Allowed actions:
{"action":"list"}
{"action":"read","path":"relative/path.py"}
{"action":"search","query":"text"}
{"action":"test"}
{"action":"write","path":"relative/path.py","content":"COMPLETE replacement file content","reason":"why"}
{"action":"final","status":"fixed|blocked|not_fixed","summary":"concise evidence-based summary"}

Rules:
- Read relevant files before editing them.
- Prefer the smallest change that addresses the issue.
- Never invent tool results.
- Use test feedback before declaring fixed.
- Sensitive writes may be blocked for human approval.
"""

        for step in range(1, max_steps + 1):
            context = {
                "issue": issue,
                "repository_files": files[:300],
                "recent_observations": observations[-8:],
                "touched_files": touched_files,
            }
            raw = self.model.generate(
                system=system,
                prompt=json.dumps(context, indent=2),
            )
            self.audit.record("model_action", step=step, raw=raw)

            try:
                action = json.loads(raw)
            except json.JSONDecodeError:
                observations.append({
                    "type": "error",
                    "message": "Model returned invalid JSON. Return one valid action object only.",
                })
                self.audit.record("invalid_model_json", step=step)
                continue

            kind = action.get("action")

            try:
                if kind == "list":
                    observation = {"type": "list", "files": files[:300]}

                elif kind == "read":
                    path = str(action["path"])
                    content = self.tools.read_file(path)
                    observation = {"type": "read", "path": path, "content": content}

                elif kind == "search":
                    query = str(action["query"])
                    hits = self.tools.search_text(query)
                    observation = {"type": "search", "query": query, "hits": hits}

                elif kind == "test":
                    last_tests = self.tools.run_tests()
                    observation = {"type": "test", **last_tests}

                elif kind == "write":
                    path = str(action["path"])
                    risk = assess_path_risk(path)
                    if risk["level"] == "high" or not allow_low_risk_writes:
                        approval_required = True
                        observation = {
                            "type": "write_blocked",
                            "path": path,
                            "risk": risk,
                            "message": "Human approval required before this write.",
                        }
                        self.audit.record(
                            "human_gate_enabled",
                            path=path,
                            reason=risk["reason"],
                        )
                    else:
                        content = str(action["content"])
                        self.tools.write_file(path, content)
                        if path not in touched_files:
                            touched_files.append(path)
                        observation = {
                            "type": "write_applied",
                            "path": path,
                            "risk": risk,
                            "reason": action.get("reason", ""),
                        }
                        self.audit.record("file_written", path=path, risk=risk)

                elif kind == "final":
                    status = str(action.get("status", "not_fixed"))
                    summary = str(action.get("summary", ""))
                    self.audit.record(
                        "repair_finished",
                        status=status,
                        summary=summary,
                        steps=step,
                    )
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
                    observation = {
                        "type": "error",
                        "message": f"Unknown action: {kind}",
                    }

            except (KeyError, ValueError, FileNotFoundError) as exc:
                observation = {"type": "tool_error", "message": str(exc)}

            observations.append(observation)
            self.audit.record("tool_observation", step=step, observation=observation)

        self.audit.record("repair_finished", status=status, summary=summary, steps=max_steps)
        return RepairResult(
            issue=issue,
            status=status,
            summary=summary,
            touched_files=touched_files,
            tests=last_tests,
            approval_required=approval_required,
            steps=max_steps,
            audit=self.audit.to_dict(),
        )
