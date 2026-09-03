"""Creation and indexing of project governance records."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence

from .frontmatter import FrontmatterError, parse_frontmatter
from .models import RecordMetadata, RecordType, Status
from .templates import render_template


RECORD_DIRECTORIES = {
    RecordType.REQUIREMENT: Path("docs/requirements"),
    RecordType.DESIGN: Path("docs/design"),
    RecordType.DECISION: Path("docs/decisions"),
    RecordType.TASK: Path("docs/work/tasks"),
    RecordType.BUG: Path("docs/work/bugs"),
    RecordType.VERIFICATION: Path("docs/verification"),
}


class DuplicateRecordError(FileExistsError):
    """Raised when a record ID or target path already exists."""


@dataclass(frozen=True, slots=True)
class RecordCandidate:
    path: Path
    metadata: RecordMetadata


def _record_files(root: Path) -> Iterable[Path]:
    ignored = {".git", ".venv", ".worktrees", ".superpowers", ".pytest_cache"}
    for path in sorted(root.rglob("*.md")):
        if not any(part in ignored for part in path.relative_to(root).parts):
            yield path


def _existing_ids(root: Path) -> set[str]:
    result: set[str] = set()
    for path in _record_files(root):
        try:
            metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, FrontmatterError):
            continue
        result.add(metadata.id)
    return result


def _slug(value: str) -> str:
    slug = re.sub(r"[^\w]+", "-", value, flags=re.UNICODE).strip("-").lower()
    return slug or "record"


def _kind(value: str | RecordType) -> RecordType:
    try:
        return value if isinstance(value, RecordType) else RecordType(value)
    except ValueError as exc:
        raise ValueError(f"unsupported record type: {value}") from exc


def create_record(
    root: str | Path,
    kind: str | RecordType,
    record_id: str,
    title: str,
    *,
    status: str | Status = Status.DRAFT,
    related: Sequence[str] = (),
    created: date | None = None,
    dry_run: bool = False,
) -> Path:
    """Create one record from a built-in template, refusing duplicates/overwrites."""

    root = Path(root)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    record_type = _kind(kind)
    try:
        record_status = status if isinstance(status, Status) else Status(status)
    except ValueError as exc:
        raise ValueError(f"unsupported record status: {status}") from exc
    if record_id in _existing_ids(root):
        raise DuplicateRecordError(f"record id already exists: {record_id}")
    metadata = RecordMetadata(
        record_id,
        record_type,
        record_status,
        created or date.today(),
        created or date.today(),
        list(related),
    )
    path = root / RECORD_DIRECTORIES[record_type] / f"{record_id}-{_slug(title)}.md"
    if path.exists():
        raise DuplicateRecordError(f"record path already exists: {path.relative_to(root).as_posix()}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_template(record_type.value, metadata, {"title": title}), encoding="utf-8")
    return path


def _index_content(candidates: Sequence[RecordCandidate], *, base_dir: Path) -> str:
    tasks = [item for item in candidates if item.metadata.type is RecordType.TASK]
    bugs = [item for item in candidates if item.metadata.type is RecordType.BUG]
    lines = [
        "<!-- PGK_GENERATED: work-index -->",
        "# Work index",
        "",
        "The index is generated from task and bug records.",
        "",
        "## Active",
        "",
    ]
    if tasks:
        for item in tasks:
            relative = item.path.relative_to(base_dir).as_posix()
            lines.append(f"- [{item.metadata.id}]({relative}) — {item.metadata.status.value}")
    else:
        lines.append("No active records yet.")
    lines.extend(["", "## Bugs", ""])
    if bugs:
        for item in bugs:
            relative = item.path.relative_to(base_dir).as_posix()
            lines.append(f"- [{item.metadata.id}]({relative}) — {item.metadata.status.value}")
    else:
        lines.append("No bug records yet.")
    return "\n".join(lines) + "\n"


def update_work_index(root: str | Path, *, dry_run: bool = False) -> Path:
    """Render the task/bug index; overwrite only a PGK-generated index."""

    root = Path(root)
    index = root / "docs/work/INDEX.md"
    candidates: list[RecordCandidate] = []
    for path in _record_files(root):
        if path == index:
            continue
        try:
            metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, FrontmatterError):
            continue
        if metadata.type in {RecordType.TASK, RecordType.BUG}:
            candidates.append(RecordCandidate(path, metadata))
    candidates.sort(key=lambda item: item.metadata.id)
    content = _index_content(candidates, base_dir=index.parent)
    if index.exists():
        existing = index.read_text(encoding="utf-8")
        if "<!-- PGK_GENERATED: work-index -->" not in existing:
            raise FileExistsError(f"refusing to overwrite project-owned index: {index}")
    if not dry_run:
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(content, encoding="utf-8")
    return index
