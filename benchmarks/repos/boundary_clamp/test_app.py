from app import clamp

def test_low():
    assert clamp(-5, 0, 10) == 0

def test_high():
    assert clamp(15, 0, 10) == 10
