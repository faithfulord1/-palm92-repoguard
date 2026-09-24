from repoguard.risk import assess_path_risk

def test_normal_path():
    assert assess_path_risk("src/utils.py")["level"] == "normal"

def test_sensitive_path():
    assert assess_path_risk(".github/workflows/deploy.yml")["level"] == "high"
