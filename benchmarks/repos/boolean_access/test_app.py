from app import can_access

def test_access():
    assert can_access(True, True) is True
    assert can_access(True, False) is False
    assert can_access(False, True) is False
    assert can_access(False, False) is False
