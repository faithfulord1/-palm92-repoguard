from __future__ import annotations

HIGH_RISK_PATTERNS = (
    ".github/workflows/",
    "auth",
    "permission",
    "secret",
    "payment",
    "database/migrations",
    "terraform",
    "iam",
)

def assess_path_risk(path: str) -> dict[str, str]:
    lowered = path.lower()
    matched = [pattern for pattern in HIGH_RISK_PATTERNS if pattern in lowered]
    if matched:
        return {
            "level": "high",
            "reason": f"Sensitive path/pattern detected: {', '.join(matched)}",
        }
    return {"level": "normal", "reason": "No sensitive path pattern detected."}
