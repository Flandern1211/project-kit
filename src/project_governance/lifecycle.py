"""Record-type lifecycle rules used by commands and checks."""

from __future__ import annotations

from .models import RecordType, Status


TERMINAL_STATUSES = frozenset({Status.VERIFIED, Status.DONE})

ALLOWED_STATUSES: dict[RecordType, frozenset[Status]] = {
    RecordType.REQUIREMENT: frozenset({Status.DRAFT, Status.ACCEPTED, Status.REJECTED, Status.SUPERSEDED}),
    RecordType.DESIGN: frozenset({Status.DRAFT, Status.ACCEPTED, Status.REJECTED, Status.SUPERSEDED}),
    RecordType.DECISION: frozenset({Status.DRAFT, Status.ACCEPTED, Status.REJECTED, Status.SUPERSEDED}),
    RecordType.TASK: frozenset(Status),
    RecordType.BUG: frozenset(Status),
    RecordType.REVIEW: frozenset({Status.DRAFT, Status.IN_REVIEW, Status.BLOCKED, Status.VERIFIED, Status.DONE, Status.REJECTED, Status.SUPERSEDED}),
    RecordType.VERIFICATION: frozenset({Status.DRAFT, Status.IN_REVIEW, Status.BLOCKED, Status.VERIFIED, Status.DONE, Status.REJECTED, Status.SUPERSEDED}),
    RecordType.MIGRATION: frozenset({Status.DRAFT, Status.IN_PROGRESS, Status.BLOCKED, Status.VERIFIED, Status.DONE, Status.REJECTED, Status.SUPERSEDED}),
}

_APPROVAL_TRANSITIONS = {
    Status.DRAFT: frozenset({Status.ACCEPTED, Status.REJECTED}),
    Status.ACCEPTED: frozenset({Status.SUPERSEDED}),
    Status.REJECTED: frozenset({Status.DRAFT, Status.SUPERSEDED}),
    Status.SUPERSEDED: frozenset(),
}

_WORK_TRANSITIONS = {
    Status.DRAFT: frozenset({Status.ACCEPTED, Status.IN_PROGRESS, Status.REJECTED, Status.SUPERSEDED}),
    Status.ACCEPTED: frozenset({Status.IN_PROGRESS, Status.REJECTED, Status.SUPERSEDED}),
    Status.IN_PROGRESS: frozenset({Status.IN_REVIEW, Status.BLOCKED}),
    Status.BLOCKED: frozenset({Status.IN_PROGRESS, Status.REJECTED, Status.SUPERSEDED}),
    Status.IN_REVIEW: frozenset({Status.IN_PROGRESS, Status.BLOCKED, Status.VERIFIED}),
    Status.VERIFIED: frozenset({Status.DONE, Status.IN_PROGRESS, Status.SUPERSEDED}),
    Status.DONE: frozenset({Status.IN_PROGRESS, Status.SUPERSEDED}),
    Status.REJECTED: frozenset({Status.DRAFT, Status.SUPERSEDED}),
    Status.SUPERSEDED: frozenset(),
}

_REVIEW_TRANSITIONS = {
    Status.DRAFT: frozenset({Status.IN_REVIEW, Status.REJECTED}),
    Status.IN_REVIEW: frozenset({Status.BLOCKED, Status.VERIFIED, Status.REJECTED}),
    Status.BLOCKED: frozenset({Status.IN_REVIEW, Status.REJECTED}),
    Status.VERIFIED: frozenset({Status.DONE, Status.IN_REVIEW, Status.SUPERSEDED}),
    Status.DONE: frozenset({Status.IN_REVIEW, Status.SUPERSEDED}),
    Status.REJECTED: frozenset({Status.DRAFT, Status.SUPERSEDED}),
    Status.SUPERSEDED: frozenset(),
}

_VERIFICATION_TRANSITIONS = {
    Status.DRAFT: frozenset({Status.IN_REVIEW, Status.VERIFIED, Status.REJECTED}),
    Status.IN_REVIEW: frozenset({Status.BLOCKED, Status.VERIFIED, Status.REJECTED}),
    Status.BLOCKED: frozenset({Status.IN_REVIEW, Status.REJECTED}),
    Status.VERIFIED: frozenset({Status.IN_REVIEW, Status.DONE, Status.SUPERSEDED}),
    Status.DONE: frozenset({Status.IN_REVIEW, Status.SUPERSEDED}),
    Status.REJECTED: frozenset({Status.DRAFT, Status.SUPERSEDED}),
    Status.SUPERSEDED: frozenset(),
}

_MIGRATION_TRANSITIONS = {
    Status.DRAFT: frozenset({Status.IN_PROGRESS, Status.REJECTED}),
    Status.IN_PROGRESS: frozenset({Status.BLOCKED, Status.VERIFIED}),
    Status.BLOCKED: frozenset({Status.IN_PROGRESS, Status.REJECTED}),
    Status.VERIFIED: frozenset({Status.DONE, Status.IN_PROGRESS, Status.SUPERSEDED}),
    Status.DONE: frozenset({Status.IN_PROGRESS, Status.SUPERSEDED}),
    Status.REJECTED: frozenset({Status.DRAFT, Status.SUPERSEDED}),
    Status.SUPERSEDED: frozenset(),
}

ALLOWED_TRANSITIONS: dict[RecordType, dict[Status, frozenset[Status]]] = {
    RecordType.REQUIREMENT: _APPROVAL_TRANSITIONS,
    RecordType.DESIGN: _APPROVAL_TRANSITIONS,
    RecordType.DECISION: _APPROVAL_TRANSITIONS,
    RecordType.TASK: _WORK_TRANSITIONS,
    RecordType.BUG: _WORK_TRANSITIONS,
    RecordType.REVIEW: _REVIEW_TRANSITIONS,
    RecordType.VERIFICATION: _VERIFICATION_TRANSITIONS,
    RecordType.MIGRATION: _MIGRATION_TRANSITIONS,
}


def status_allowed(record_type: RecordType, status: Status) -> bool:
    return status in ALLOWED_STATUSES[record_type]


def transition_allowed(record_type: RecordType, current: Status, target: Status) -> bool:
    return target in ALLOWED_TRANSITIONS[record_type].get(current, frozenset())


__all__ = [
    "ALLOWED_STATUSES", "ALLOWED_TRANSITIONS", "TERMINAL_STATUSES",
    "status_allowed", "transition_allowed",
]
