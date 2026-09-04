"""Task handoff updates with a compact, machine-readable Git snapshot."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .frontmatter import FrontmatterError, parse_frontmatter
from .git_context import GitContext, inspect_git
from .models import RecordType, Status
from .records import append_activity, update_indexes, update_work_index


START_MARKER = "<!-- PGK_HANDOFF_START -->"
END_MARKER = "<!-- PGK_HANDOFF_END -->"


class HandoffError(ValueError):
    """Raised when a task handoff cannot be updated safely."""


def _validate_handoff_value(value: str, *, field: str) -> str:
    cleaned = value.strip()
    if any(token in cleaned for token in ("\n", "\r", "|", START_MARKER, END_MARKER)) or "\n##" in cleaned:
        raise HandoffError(f"handoff field contains unsafe characters: {field}")
    return cleaned


def _work_record(root: Path, task_id: str) -> Path:
    candidates = sorted(
        list((root / "docs/work/tasks").glob("*.md"))
        + list((root / "docs/work/bugs").glob("*.md"))
    )
    for path in candidates:
        try:
            metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, FrontmatterError):
            continue
        if metadata.type in {RecordType.TASK, RecordType.BUG} and metadata.id == task_id:
            return path
    raise HandoffError(f"task or bug record not found: {task_id}")


def _git_or_unavailable(root: Path) -> GitContext:
    try:
        return inspect_git(root)
    except ValueError:
        return GitContext(branch="unavailable", head="unavailable", dirty=False, recent_commits=())


def _handoff_block(
    *,
    status: str,
    context: GitContext,
    verification: str | None,
    blockers: Sequence[str],
    next_action: str,
    scope: Sequence[str],
    authorization: str | None,
    current_work: str,
    completed_work: str,
    remaining_work: str,
) -> str:
    blocker_text = "; ".join(_validate_handoff_value(item, field="blockers") for item in blockers if item.strip()) or "none"
    verification_text = _validate_handoff_value(verification, field="verification") if verification and verification.strip() else "not provided"
    unavailable = context.branch == "unavailable"
    worktree = "dirty" if context.dirty else "clean"
    dirty_text = "true" if context.dirty else "false"
    uncommitted = "present" if context.dirty else "none"
    if unavailable:
        worktree = "unavailable (not a Git repository)"
        dirty_text = "unavailable"
        uncommitted = "unavailable"
    scope_text = "; ".join(_validate_handoff_value(item, field="scope") for item in scope if item.strip()) or "not declared"
    authorization_text = _validate_handoff_value(authorization, field="authorization") if authorization and authorization.strip() else "none"
    current_work = _validate_handoff_value(current_work, field="current_work")
    completed_work = _validate_handoff_value(completed_work, field="completed_work")
    remaining_work = _validate_handoff_value(remaining_work, field="remaining_work")
    next_action = _validate_handoff_value(next_action, field="next_action")
    return "\n".join(
        [
            f"Status: {status}",
            f"Current work: {current_work}",
            f"Completed work: {completed_work}",
            f"Remaining work: {remaining_work}",
            f"Branch: {context.branch}",
            f"HEAD: {context.head}",
            f"Worktree: {worktree}",
            f"Dirty: {dirty_text}",
            f"Uncommitted: {uncommitted}",
            f"Verification: {verification_text}",
            f"Blockers: {blocker_text}",
            f"Next action: {next_action.strip()}",
            f"Scope: {scope_text}",
            f"Authorization: {authorization_text}",
        ]
    )


def _section_value(content: str, heading: str) -> list[str]:
    """Read a declared Markdown section without retaining terminal output."""
    marker = f"## {heading}"
    start = content.find(marker)
    if start < 0:
        return []
    body = content[start + len(marker):]
    end = body.find("\n## ")
    if end >= 0:
        body = body[:end]
    return [line.strip(" -\t") for line in body.splitlines() if line.strip()]


def _prepare_handoff(
    root: str | Path,
    task_id: str,
    *,
    next_action: str,
    status: str | Status | None,
    verification: str | None,
    blockers: Sequence[str],
    scope: Sequence[str],
    authorization: str | None,
    current_work: str | None,
    completed_work: str | None,
    remaining_work: str | None,
) -> tuple[Path, str, GitContext, str]:
    if not next_action.strip():
        raise HandoffError("next_action must not be empty")
    root = Path(root)
    record = _work_record(root, task_id)
    content = record.read_text(encoding="utf-8")
    start = content.find(START_MARKER)
    end = content.find(END_MARKER, start + len(START_MARKER)) if start >= 0 else -1
    if start < 0 or end < 0:
        raise HandoffError(f"task record has no handoff markers: {record}")
    metadata, _ = parse_frontmatter(content)
    if status is None:
        normalized_status = metadata.status.value
    else:
        try:
            normalized_status = (status if isinstance(status, Status) else Status(status)).value
        except ValueError as exc:
            raise HandoffError(f"unsupported handoff status: {status}") from exc
    context = _git_or_unavailable(root)
    scope_values = scope or _section_value(content, "Scope")
    authorization_value = authorization if authorization is not None else "; ".join(_section_value(content, "Authorization"))
    current_value = current_work.strip() if current_work and current_work.strip() else "; ".join(_section_value(content, "Current work") or _section_value(content, "Scope"))
    completed_value = completed_work.strip() if completed_work and completed_work.strip() else "; ".join(_section_value(content, "Completed work") or _section_value(content, "Changes"))
    remaining_value = remaining_work.strip() if remaining_work and remaining_work.strip() else "; ".join(_section_value(content, "Remaining work"))
    block = _handoff_block(
        status=normalized_status,
        context=context,
        verification=verification,
        blockers=blockers,
        next_action=next_action,
        scope=scope_values,
        authorization=authorization_value,
        current_work=current_value or "not declared",
        completed_work=completed_value or "not declared",
        remaining_work=remaining_value or next_action.strip(),
    )
    replacement = f"{START_MARKER}\n{block}\n{END_MARKER}"
    updated = content[:start] + replacement + content[end + len(END_MARKER) :]
    return record, updated, context, block


def preview_handoff(
    root: str | Path,
    task_id: str,
    *,
    next_action: str,
    status: str | Status | None = None,
    verification: str | None = None,
    blockers: Sequence[str] = (),
    scope: Sequence[str] = (),
    authorization: str | None = None,
    current_work: str | None = None,
    completed_work: str | None = None,
    remaining_work: str | None = None,
) -> str:
    """Render the marked handoff block without writing or logging it."""
    _record, _updated, _context, block = _prepare_handoff(
        root, task_id, next_action=next_action, status=status, verification=verification,
        blockers=blockers, scope=scope, authorization=authorization,
        current_work=current_work, completed_work=completed_work, remaining_work=remaining_work,
    )
    return block


def update_handoff(
    root: str | Path,
    task_id: str,
    *,
    next_action: str,
    status: str | Status | None = None,
    verification: str | None = None,
    blockers: Sequence[str] = (),
    scope: Sequence[str] = (),
    authorization: str | None = None,
    current_work: str | None = None,
    completed_work: str | None = None,
    remaining_work: str | None = None,
    dry_run: bool = False,
) -> Path:
    """Update only the marked handoff section of a task record."""

    root = Path(root)
    record, updated, context, _block = _prepare_handoff(
        root, task_id, next_action=next_action, status=status, verification=verification,
        blockers=blockers, scope=scope, authorization=authorization,
        current_work=current_work, completed_work=completed_work, remaining_work=remaining_work,
    )
    if not dry_run:
        # Validate all protected views before changing the record so an
        # unmarked project-owned view cannot leave a partial handoff.
        update_work_index(root, dry_run=True)
        update_indexes(root, dry_run=True)
        activity_path = root / "docs/activity/ACTIVITY.md"
        if activity_path.exists() and "<!-- PGK_GENERATED: activity -->" not in activity_path.read_text(encoding="utf-8"):
            raise FileExistsError(f"refusing to overwrite project-owned view: {activity_path}")
        record.write_text(updated, encoding="utf-8")
        update_work_index(root)
        update_indexes(root)
        append_activity(root, "pgk", "handoff", task_id, context.head, "updated")
    return record
