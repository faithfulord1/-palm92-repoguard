from pathlib import Path
from repoguard.tools import RepoTools

def test_list_and_search(tmp_path: Path):
    (tmp_path / "hello.py").write_text("def greet():\n    return 'hello'\n", encoding="utf-8")
    tools = RepoTools(tmp_path)
    assert "hello.py" in tools.list_files()
    hits = tools.search_text("greet")
    assert hits[0]["path"] == "hello.py"

def test_rewrite_invalidates_only_target_module_bytecode(tmp_path: Path):
    target = tmp_path / "app.py"
    target.write_text("answer = 2\n", encoding="utf-8")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    stale = cache / "app.cpython-311.pyc"
    unrelated = cache / "other.cpython-311.pyc"
    stale.write_bytes(b"stale bytecode")
    unrelated.write_bytes(b"keep")

    RepoTools(tmp_path).write_file("app.py", "answer = 3\n")

    assert not stale.exists()
    assert unrelated.read_bytes() == b"keep"
    assert target.read_text(encoding="utf-8") == "answer = 3\n"
