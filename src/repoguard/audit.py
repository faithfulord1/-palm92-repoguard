from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

@dataclass
class AuditEvent:
    event_type: str
    details: dict[str, Any]
    timestamp: str

class AuditLedger:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def record(self, event_type: str, **details: Any) -> None:
        self.events.append(
            AuditEvent(
                event_type=event_type,
                details=details,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {"events": [asdict(event) for event in self.events]}

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
