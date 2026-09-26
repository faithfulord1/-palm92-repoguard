from directory import ancestors


def effective_access(*, user_active: bool, user_team: str, grant_team: str, revoked: bool) -> bool:
    """A grant to an ancestor team covers descendants, unless revoked or inactive."""
    # BUG: tests whether either team shares any ancestor; ignores inactive user.
    return bool(ancestors(user_team) & ancestors(grant_team)) and not revoked
