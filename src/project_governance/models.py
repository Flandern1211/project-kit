from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

class RecordType(StrEnum):
    REQUIREMENT = "requirement"
    DESIGN = "design"
    DECISION = "decision"
    TASK = "task"
    BUG = "bug"
    REVIEW = "review"
    VERIFICATION = "verification"
    MIGRATION = "migration"

class Status(StrEnum):
    DRAFT = "draft"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    VERIFIED = "verified"
    DONE = "done"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"

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
