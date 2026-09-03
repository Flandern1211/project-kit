"""Task handoff updates with a compact, machine-readable Git snapshot."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .frontmatter import FrontmatterError, parse_frontmatter
from .git_context import GitContext, inspect_git
from .models import RecordType, Status


START_MARKER = "<!-- PGK_HANDOFF_START -->"
END_MARKER = "<!-- PGK_HANDOFF_END -->"


class HandoffError(ValueError):
    """Raised when a task handoff cannot be updated safely."""


def _task_record(root: Path, task_id: str) -> Path:
    candidates = sorted((root / "docs/work/tasks").glob("*.md"))
    for path in candidates:
        try:
            metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, FrontmatterError):
            continue
        if metadata.type is RecordType.TASK and metadata.id == task_id:
            return path
    raise HandoffError(f"task record not found: {task_id}")


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
) -> str:
    blocker_text = "; ".join(item.strip() for item in blockers if item.strip()) or "none"
    verification_text = verification.strip() if verification and verification.strip() else "not provided"
    worktree = "dirty" if context.dirty else "clean"
    if context.branch == "unavailable":
        worktree = "unavailable (not a Git repository)"
    return "\n".join(
        [
            f"Status: {status}",
            f"Branch: {context.branch}",
            f"HEAD: {context.head}",
            f"Worktree: {worktree}",
            f"Verification: {verification_text}",
            f"Blockers: {blocker_text}",
            f"Next action: {next_action.strip()}",
        ]
    )


def update_handoff(
    root: str | Path,
    task_id: str,
    *,
    next_action: str,
    status: str | Status | None = None,
    verification: str | None = None,
    blockers: Sequence[str] = (),
    dry_run: bool = False,
) -> Path:
    """Update only the marked handoff section of a task record."""

    if not next_action.strip():
        raise HandoffError("next_action must not be empty")
    root = Path(root)
    record = _task_record(root, task_id)
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
    block = _handoff_block(
        status=normalized_status,
        context=_git_or_unavailable(root),
        verification=verification,
        blockers=blockers,
        next_action=next_action,
    )
    replacement = f"{START_MARKER}\n{block}\n{END_MARKER}"
    updated = content[:start] + replacement + content[end + len(END_MARKER) :]
    if not dry_run:
        record.write_text(updated, encoding="utf-8")
    return record

