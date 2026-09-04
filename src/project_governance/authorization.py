"""Read-only parsing of document-based protected-action authorization."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from collections.abc import Mapping
import re


_KEY_ALIASES = {
    "valid_from": ("valid_from", "starts_at", "not_before"),
    "expires_at": ("expires_at", "expires", "valid_until"),
}


def _text(record: str | Path | Mapping[str, object]) -> str:
    if isinstance(record, Mapping):
        return "\n".join(f"{key}: {value}" for key, value in record.items())
    if isinstance(record, Path):
        return record.read_text(encoding="utf-8")
    candidate = Path(record)
    if "\n" not in record and candidate.exists():
        return candidate.read_text(encoding="utf-8")
    return record


def _authorization_fields(record: str | Path | Mapping[str, object]) -> dict[str, str]:
    text = _text(record)
    section = re.search(r"(?im)^##\s+Authorization\s*$([\s\S]*?)(?=^##\s+|\Z)", text)
    source = section.group(1) if section else text
    values: dict[str, str] = {}
    for line in source.splitlines():
        match = re.match(r"^\s*(action|target|scope|valid_from|starts_at|not_before|expires_at|expires|valid_until|status|revoked)\s*:\s*(.*?)\s*$", line, re.I)
        if match:
            values[match.group(1).lower()] = match.group(2).strip().strip("'\"")
    for canonical, aliases in _KEY_ALIASES.items():
        if canonical not in values:
            for alias in aliases:
                if alias in values:
                    values[canonical] = values[alias]
                    break
    return values


def _when(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.combine(date.fromisoformat(value), datetime.min.time())
        except ValueError:
            return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def authorization_matches(
    record: str | Path | Mapping[str, object],
    action: str,
    target: str,
    at: datetime | date | None = None,
    *,
    scope: str | None = None,
) -> bool:
    """Return whether a document authorization matches; never performs the action."""

    try:
        fields = _authorization_fields(record)
    except (OSError, ValueError, TypeError):
        return False
    if not fields.get("action") or fields.get("action") != action:
        return False
    if not fields.get("target") or fields.get("target") != target:
        return False
    if not fields.get("scope"):
        return False
    state = fields.get("status", "active").lower()
    if state not in {"active", "approved", "accepted"}:
        return False
    if fields.get("revoked", "").lower() in {"true", "yes", "1", "revoked"} or state in {"revoked", "expired", "inactive", "rejected"}:
        return False
    if scope is not None and fields.get("scope") != scope:
        return False
    moment = at or datetime.now(timezone.utc)
    if isinstance(moment, date) and not isinstance(moment, datetime):
        moment = datetime.combine(moment, datetime.min.time(), tzinfo=timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    start = _when(fields.get("valid_from", ""))
    expiry = _when(fields.get("expires_at", ""))
    if start is None or expiry is None or moment < start or moment > expiry:
        return False
    return True


__all__ = ["authorization_matches"]
