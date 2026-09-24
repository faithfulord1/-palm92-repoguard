from pathlib import Path
from repoguard.tools import RepoTools

def test_list_and_search(tmp_path: Path):
    (tmp_path / "hello.py").write_text("def greet():\n    return 'hello'\n", encoding="utf-8")
    tools = RepoTools(tmp_path)
    assert "hello.py" in tools.list_files()
    hits = tools.search_text("greet")
    assert hits[0]["path"] == "hello.py"
