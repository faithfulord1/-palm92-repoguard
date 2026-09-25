from __future__ import annotations
from pathlib import Path
import subprocess


class RepoTools:
    def __init__(self, repo_root: str | Path) -> None:
        self.root = Path(repo_root).resolve()

    def _safe(self, relative_path: str) -> Path:
        target = (self.root / relative_path).resolve()
        if self.root not in target.parents and target != self.root:
            raise ValueError("Path escapes repository root")
        return target

    def list_files(
        self,
        suffixes: tuple[str, ...] = (
            ".py", ".js", ".ts", ".tsx", ".md", ".json", ".yml", ".yaml", ".toml"
        ),
    ) -> list[str]:
        results = []
        for path in self.root.rglob("*"):
            if path.is_file() and path.suffix in suffixes and ".git" not in path.parts:
                results.append(str(path.relative_to(self.root)))
        return sorted(results)

    def read_file(self, relative_path: str, max_chars: int = 30000) -> str:
        return self._safe(relative_path).read_text(encoding="utf-8")[:max_chars]

    def write_file(self, relative_path: str, content: str) -> None:
        target = self._safe(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        # CPython may reuse a same-size .pyc when consecutive edits happen
        # inside one filesystem timestamp tick. Invalidate only the touched
        # module's cached bytecode so immediate post-write verification runs
        # the new code, not a stale cached version.
        if target.suffix == ".py":
            cache_dir = target.parent / "__pycache__"
            if cache_dir.is_dir():
                for cached in cache_dir.glob(f"{target.stem}.*.pyc"):
                    cached.unlink()

    def search_text(self, query: str, max_results: int = 50) -> list[dict[str, object]]:
        hits = []
        for relative in self.list_files():
            path = self._safe(relative)
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for number, line in enumerate(lines, 1):
                if query.lower() in line.lower():
                    hits.append({"path": relative, "line": number, "text": line.strip()})
                    if len(hits) >= max_results:
                        return hits
        return hits

    def run_tests(self, command: list[str] | None = None, timeout: int = 120) -> dict[str, object]:
        command = command or ["python", "-m", "pytest", "-q"]
        completed = subprocess.run(
            command,
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-12000:],
        }
