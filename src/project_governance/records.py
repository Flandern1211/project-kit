"""Creation and indexing of project governance records."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Sequence

from .frontmatter import FrontmatterError, parse_frontmatter
from .config import load_config, record_type_enabled
from .models import RecordMetadata, RecordType, Status
from .templates import render_template


RECORD_DIRECTORIES = {
    RecordType.REQUIREMENT: Path("docs/requirements"),
    RecordType.DESIGN: Path("docs/design"),
    RecordType.DECISION: Path("docs/decisions"),
    RecordType.TASK: Path("docs/work/tasks"),
    RecordType.BUG: Path("docs/work/bugs"),
    RecordType.REVIEW: Path("docs/reviews"),
    RecordType.VERIFICATION: Path("docs/verification"),
}


def _governance_root(root: Path) -> Path:
    return Path(load_config(root / ".project-governance.toml").governance_dir)


def _record_directories(root: Path) -> dict[RecordType, Path]:
    base = _governance_root(root)
    return {kind: base / path.relative_to(Path("docs")) for kind, path in RECORD_DIRECTORIES.items()}
RECORD_ID_PATTERN = re.compile(r"^(?:REQ|DES|ADR|PLAN|TASK|BUG|REVIEW|VER|INC)-[A-Za-z0-9][A-Za-z0-9._-]*$")
RECORD_PREFIXES = {RecordType.REQUIREMENT: "REQ-", RecordType.DESIGN: "DES-", RecordType.DECISION: "ADR-", RecordType.TASK: "TASK-", RecordType.BUG: "BUG-", RecordType.REVIEW: "REVIEW-", RecordType.VERIFICATION: "VER-"}


class DuplicateRecordError(FileExistsError):
    """Raised when a record ID or target path already exists."""


@dataclass(frozen=True, slots=True)
class RecordCandidate:
    path: Path
    metadata: RecordMetadata
    body: str = ""


def _record_files(root: Path) -> Iterable[Path]:
    ignored = {".git", ".agent", ".venv", ".worktrees", ".superpowers", ".pytest_cache"}
    base = root / _governance_root(root)
    for path in sorted(base.rglob("*.md")):
        if not any(part in ignored or part.startswith(".pytest-tmp") for part in path.relative_to(root).parts):
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
    profile = load_config(root / ".project-governance.toml").profile
    if not record_type_enabled(profile, record_type.value):
        raise ValueError(f"{profile} profile does not enable {record_type.value}")
    if not record_id.startswith(RECORD_PREFIXES[record_type]):
        raise ValueError(f"record id prefix does not match type: {record_type.value}")
    if not RECORD_ID_PATTERN.fullmatch(record_id):
        raise ValueError("record id must use a safe prefix and filename characters")
    if any(not RECORD_ID_PATTERN.fullmatch(item) for item in related):
        raise ValueError("related ids must use a safe prefix and filename characters")
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
    path = root / _record_directories(root)[record_type] / f"{record_id}-{_slug(title)}.md"
    if path.exists():
        raise DuplicateRecordError(f"record path already exists: {path.relative_to(root).as_posix()}")
    if not dry_run:
        _ensure_views_writable(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_template(record_type.value, metadata, {"title": title}), encoding="utf-8")
        update_work_index(root)
        update_indexes(root)
        append_activity(root, "pgk", "create", record_id, "N/A", "created")
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
    index = root / _record_directories(root)[RecordType.TASK].parent / "INDEX.md"
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


_INDEXES = {
    RecordType.REQUIREMENT: Path("docs/requirements/INDEX.md"),
    RecordType.DESIGN: Path("docs/design/INDEX.md"),
    RecordType.DECISION: Path("docs/decisions/INDEX.md"),
    RecordType.TASK: Path("docs/work/tasks/INDEX.md"),
    RecordType.BUG: Path("docs/work/bugs/INDEX.md"),
    RecordType.REVIEW: Path("docs/reviews/INDEX.md"),
    RecordType.VERIFICATION: Path("docs/verification/INDEX.md"),
}


def _indexes_for_project(root: Path) -> dict[RecordType, Path]:
    profile = load_config(root / ".project-governance.toml").profile
    directories = _record_directories(root)
    indexes = {kind: path / "INDEX.md" for kind, path in directories.items()}
    if profile == "lite":
        return {kind: path for kind, path in indexes.items() if kind in {RecordType.REQUIREMENT, RecordType.TASK, RecordType.BUG, RecordType.VERIFICATION}}
    return indexes


def _ensure_views_writable(root: Path) -> None:
    """Fail before record creation if any generated view is project-owned."""
    views = [(root / path, f"{kind.value}-index") for kind, path in _indexes_for_project(root).items()]
    work_root = _record_directories(root)[RecordType.TASK].parent
    views.append((root / work_root / "INDEX.md", "work-index"))
    views.append((root / work_root / "BOARD.md", "board"))
    views.append((root / _governance_root(root) / "activity/ACTIVITY.md", "activity"))
    for path, marker in views:
        if path.exists() and f"<!-- PGK_GENERATED: {marker} -->" not in path.read_text(encoding="utf-8"):
            raise FileExistsError(f"refusing to overwrite project-owned view: {path}")


def _view_write(path: Path, content: str, marker: str, *, dry_run: bool) -> None:
    if path.exists() and f"<!-- PGK_GENERATED: {marker} -->" not in path.read_text(encoding="utf-8"):
        raise FileExistsError(f"refusing to overwrite project-owned view: {path}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _directory_index(items: Sequence[RecordCandidate], index: Path, marker: str, title: str) -> str:
    lines = [f"<!-- PGK_GENERATED: {marker} -->", f"# {title}", "", "The index is generated from records.", ""]
    if items:
        for item in sorted(items, key=lambda x: x.metadata.id):
            rel = item.path.relative_to(index.parent).as_posix()
            lines.append(f"- [{item.metadata.id}]({rel}) — {item.metadata.status.value}")
    else:
        lines.append("No records yet.")
    return "\n".join(lines) + "\n"


def _board_content(items: Sequence[RecordCandidate]) -> str:
    lines = ["<!-- PGK_GENERATED: board -->", "# Work board", "", "| ID | type | status | owner | related | branch/worktree | verification | blocker | next |", "|---|---|---|---|---|---|---|---|---|"]
    for item in sorted(items, key=lambda x: x.metadata.id):
        m = item.metadata
        related = ", ".join(m.related).replace("\r", " ").replace("\n", " ") if m.related else "N/A"
        def section(name: str) -> str:
            matches = re.finditer(rf"(?ims)^##\s+{re.escape(name)}\s*$([\s\S]*?)(?=^##\s+|\Z)", item.body)
            values = [next((line.strip(" -*\t") for line in match.group(1).splitlines() if line.strip()), "N/A") for match in matches]
            return next((value for value in reversed(values) if value.casefold() != "n/a"), values[-1] if values else "N/A")
        def cell(value: str) -> str:
            value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
            return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip() or "N/A"
        def git_value(name: str) -> str:
            matches = re.findall(rf"(?im)^\s*{re.escape(name)}\s*:\s*(.+)$", item.body)
            return next((value.strip() for value in reversed(matches) if value.strip().casefold() != "n/a"), "N/A")
        branch, worktree = git_value("branch"), git_value("worktree")
        handoff_matches = list(re.finditer(r"(?ims)^##\s+Handoff\s*$([\s\S]*?)(?=^##\s+|\Z)", item.body))
        handoff = handoff_matches[-1].group(1) if handoff_matches else ""
        def handoff_value(name: str) -> str:
            matches = re.findall(rf"(?im)^\s*{re.escape(name)}\s*:\s*(.+)$", handoff)
            return next((value.strip() for value in reversed(matches) if value.strip()), "N/A")

        if branch == "N/A":
            branch = handoff_value("Branch")
        if worktree == "N/A":
            worktree = handoff_value("Worktree")
        verification = handoff_value("Verification")
        if verification == "N/A":
            verification = section("Evidence")
        blocker = handoff_value("Blockers")
        if blocker == "N/A":
            blocker = section("Blockers")
        next_action = handoff_value("Next action")
        if next_action == "N/A":
            next_action = section("Next action")
        lines.append(f"| {cell(m.id)} | {cell(m.type.value)} | {cell(m.status.value)} | {cell(section('Owner'))} | {cell(related)} | {cell(branch)} / {cell(worktree)} | {cell(verification)} | {cell(blocker)} | {cell(next_action)} |")
    return "\n".join(lines) + "\n"


def update_indexes(root: str | Path, *, dry_run: bool = False) -> dict[str, Path]:
    """Refresh all generated record indexes and the work board safely."""
    root = Path(root)
    _ensure_views_writable(root)
    candidates: list[RecordCandidate] = []
    for path in _record_files(root):
        try:
            metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, FrontmatterError):
            continue
        if metadata.type in _INDEXES:
            candidates.append(RecordCandidate(path, metadata, body))
    result: dict[str, Path] = {}
    for kind, index in _indexes_for_project(root).items():
        selected = [c for c in candidates if c.metadata.type is kind]
        marker = f"{kind.value}-index"
        content = _directory_index(selected, root / index, marker, f"{kind.value.title()} index")
        _view_write(root / index, content, marker, dry_run=dry_run)
        result[kind.value] = root / index
    work_root = _record_directories(root)[RecordType.TASK].parent
    board = root / work_root / "BOARD.md"
    _view_write(board, _board_content(candidates), "board", dry_run=dry_run)
    result["board"] = board
    return result


def append_activity(root: str | Path, actor: str, action: str, record_id: str, git_ref: str, result: str) -> Path:
    """Append one fixed-format governance event to ACTIVITY.md."""
    fields = (actor, action, record_id, git_ref, result)
    if any("|" in value or "\n" in value or "\r" in value for value in fields):
        raise ValueError("activity fields must not contain pipe or newline characters")
    path = Path(root) / _governance_root(Path(root)) / "activity/ACTIVITY.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and "<!-- PGK_GENERATED: activity -->" not in path.read_text(encoding="utf-8"):
        raise FileExistsError(f"refusing to overwrite project-owned view: {path}")
    if not path.exists():
        path.write_text("<!-- PGK_GENERATED: activity -->\n# Activity\n\n<!-- timestamp | actor | action | record_id | git_ref | result -->\n", encoding="utf-8")
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{timestamp} | {actor} | {action} | {record_id} | {git_ref} | {result}\n")
    return path
