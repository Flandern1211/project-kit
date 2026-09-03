from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

class RecordType(StrEnum):
    REQUIREMENT = "requirement"
    DESIGN = "design"
    DECISION = "decision"
    TASK = "task"
    BUG = "bug"
    VERIFICATION = "verification"

class Status(StrEnum):
    DRAFT = "draft"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    REJECTED = "rejected"

@dataclass(slots=True)
class RecordMetadata:
    id: str
    type: RecordType
    status: Status
    created: date
    updated: date
    related: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {"id": self.id, "type": self.type.value, "status": self.status.value,
                "created": self.created.isoformat(), "updated": self.updated.isoformat(),
                "related": list(self.related)}
