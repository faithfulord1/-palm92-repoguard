import pytest
from permissions import effective_access


@pytest.mark.parametrize("team,grant,expected", [
    ("platform", "engineering", True),
    ("platform", "company", True),
    ("platform", "finance", False),
    ("payroll", "engineering", False),
    ("finance", "finance", True),
])
def test_team_inheritance(team, grant, expected):
    assert effective_access(user_active=True, user_team=team, grant_team=grant, revoked=False) is expected


def test_inactive_user_denied():
    assert effective_access(user_active=False, user_team="platform", grant_team="engineering", revoked=False) is False


def test_revoked_grant_denied():
    assert effective_access(user_active=True, user_team="platform", grant_team="engineering", revoked=True) is False
