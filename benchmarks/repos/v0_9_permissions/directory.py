TEAM_PARENT = {
    "engineering": "company",
    "platform": "engineering",
    "finance": "company",
    "payroll": "finance",
}


def ancestors(team: str) -> set[str]:
    """Includes the team and each parent, but not sibling branches."""
    result = set()
    while team:
        if team in result:
            raise ValueError("cyclic team hierarchy")
        result.add(team)
        team = TEAM_PARENT.get(team)
    return result
