"""Read-only discovery and safe document migration primitives."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Sequence

from .config import load_config
from .frontmatter import parse_frontmatter, render_frontmatter
from .git_context import inspect_git
from .models import RecordMetadata, RecordType, Status
from .records import RECORD_DIRECTORIES, RECORD_PREFIXES, append_activity, create_record, update_indexes


DEFAULT_SCAN_ROOTS = ("README.md", "CONTRIBUTING.md", "CHANGELOG.md", "docs", "doc", "documentation", "设计", "需求")
DEFAULT_EXCLUDE_PATTERNS = (
    ".git", ".agent", ".venv", "node_modules", "vendor", "build", "dist", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".worktrees", ".superpowers", "tmp", "temp", ".tmp",
)
GENERATED_DOCUMENT_DIRS = {
    "docs/requirements", "docs/design", "docs/decisions", "docs/migrations", "docs/work",
    "docs/reviews", "docs/verification", "docs/templates", "docs/operations",
}
SUPPORTED_SUFFIXES = {".md": "markdown", ".markdown": "markdown", ".txt": "text"}
NON_DOCUMENT_SUFFIXES = {".py", ".pyc", ".go", ".js", ".ts", ".java", ".rs", ".c", ".h", ".cpp", ".class", ".dll", ".exe", ".bin"}
MAX_SOURCE_BYTES = 2 * 1024 * 1024
_HINTS: tuple[tuple[str, str, str], ...] = (
    ("requirement", "requirement", "requirement or PRD filename hint"),
    ("requirements", "requirement", "requirements filename hint"),
    ("prd", "requirement", "PRD filename hint"),
    ("design", "design", "design filename hint"),
    ("architecture", "design", "architecture filename hint"),
    ("tsd", "design", "TSD filename hint"),
    ("adr", "decision", "ADR filename hint"),
    ("bug", "bug", "bug filename hint"),
    ("issue", "bug", "issue filename hint"),
    ("task", "task", "task filename hint"),
)
_SENSITIVE_NAME_PARTS = (".env", "secret", "password", "passwd", "token", "credential", "private-key", "private_key", "certificate", "account")
_SENSITIVE_CONTENT = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"(?im)^\s*(?:password|passwd|secret|token|api[_-]?key)\s*[:=]"),
)


@dataclass(frozen=True, slots=True)
class MigrationCandidate:
    source_path: str
    source_hash: str
    source_format: str
    suggested_type: str | None
    confidence: str
    reason: str
    sensitive: bool
    sensitive_reason: str | None
    status: str = "candidate"

    def as_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "source_hash": self.source_hash,
            "source_format": self.source_format,
            "suggested_type": self.suggested_type,
            "confidence": self.confidence,
            "reason": self.reason,
            "sensitive": self.sensitive,
            "sensitive_reason": self.sensitive_reason,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class MigrationEntry:
    item_id: str
    source_path: str
    source_hash: str
    source_format: str
    target_id: str | None
    target_path: str | None
    suggested_type: str | None
    confidence: str
    reason: str
    sensitive: bool
    status: str
    result: str = ""
    error: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "source_path": self.source_path,
            "source_hash": self.source_hash,
            "source_format": self.source_format,
            "target_id": self.target_id,
            "target_path": self.target_path,
            "suggested_type": self.suggested_type,
            "confidence": self.confidence,
            "reason": self.reason,
            "sensitive": self.sensitive,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


@dataclass(frozen=True, slots=True)
class MigrationPlan:
    migration_id: str
    path: Path
    status: str
    approval: str
    entries: tuple[MigrationEntry, ...]
    source_root: str = "."
    git_snapshot: tuple[tuple[str, str], ...] = ()
    execution_git: tuple[tuple[str, str], ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "migration_id": self.migration_id,
            "path": self.path.as_posix(),
            "status": self.status,
            "approval": self.approval,
            "entries": [entry.as_dict() for entry in self.entries],
        }


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("scan path must stay inside project root") from exc


def _is_excluded(relative: str, path: Path, patterns: Sequence[str]) -> bool:
    normalized = relative.casefold()
    parts = set(normalized.split("/"))
    for pattern in patterns:
        value = pattern.replace("\\", "/").strip().casefold().rstrip("/")
        if not value:
            continue
        if value in parts or normalized == value or normalized.startswith(value + "/"):
            return True
    return False


def _is_generated(relative: str) -> bool:
    normalized = relative.casefold()
    return any(normalized == item or normalized.startswith(item + "/") for item in GENERATED_DOCUMENT_DIRS)


def _is_sensitive_name(path: Path) -> str | None:
    name = path.name.casefold()
    for part in _SENSITIVE_NAME_PARTS:
        if part in name:
            return f"sensitive filename pattern: {part}"
    return None


def _sensitive_reason(path: Path, data: bytes) -> str | None:
    name_reason = _is_sensitive_name(path)
    if name_reason:
        return name_reason
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return next((pattern.pattern for pattern in _SENSITIVE_CONTENT if pattern.search(text)), None)


def _classify(path: Path) -> tuple[str | None, str, str, str]:
    tokens = re.split(r"[^a-z0-9]+", path.stem.casefold())
    matches = [(kind, reason) for token in tokens for hint, kind, reason in _HINTS if token == hint]
    kinds = {kind for kind, _reason in matches}
    if len(kinds) == 1:
        kind = next(iter(kinds))
        return kind, "high", "; ".join(dict.fromkeys(reason for _kind, reason in matches)), "candidate"
    if len(kinds) > 1:
        return None, "low", "conflicting filename hints", "needs_review"
    return None, "low", "no supported filename hint", "needs_review"


def _default_roots(root: Path) -> tuple[str, ...]:
    config = load_config(root / ".project-governance.toml")
    return config.scan_roots or DEFAULT_SCAN_ROOTS


def _default_excludes(root: Path) -> tuple[str, ...]:
    config = load_config(root / ".project-governance.toml")
    return tuple(DEFAULT_EXCLUDE_PATTERNS) + tuple(config.exclude_patterns)


def _expand_roots(root: Path, scan_roots: Sequence[str]) -> tuple[Path, ...]:
    result: list[Path] = []
    for raw in scan_roots:
        requested = Path(raw)
        path = requested.resolve() if requested.is_absolute() else (root / requested).resolve()
        _relative(root, path)
        if not path.exists():
            continue
        result.append(path)
    return tuple(dict.fromkeys(result))


def _files_under(root: Path, base: Path, patterns: Sequence[str]) -> list[tuple[str, Path]]:
    paths = [base] if base.is_file() else sorted(base.rglob("*"))
    result: list[tuple[str, Path]] = []
    for path in paths:
        if not path.is_file():
            continue
        relative = _relative(root, path)
        if _is_excluded(relative, path, patterns) or _is_generated(relative):
            continue
        result.append((relative, path))
    return result


def scan_project(
    root: str | Path,
    *,
    scan_roots: Sequence[str] | None = None,
    exclude_patterns: Sequence[str] | None = None,
) -> tuple[MigrationCandidate, ...]:
    """Return deterministic, read-only migration candidates for a project."""

    root = Path(root).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    roots = _expand_roots(root, tuple(scan_roots) if scan_roots is not None else _default_roots(root))
    patterns = tuple(exclude_patterns) if exclude_patterns is not None else _default_excludes(root)
    discovered: dict[str, Path] = {}
    for base in roots:
        for relative, path in _files_under(root, base, patterns):
            discovered[relative] = path

    result: list[MigrationCandidate] = []
    for relative in sorted(discovered):
        path = discovered[relative]
        try:
            size = path.stat().st_size
        except OSError:
            continue
        suffix = path.suffix.casefold()
        if suffix in NON_DOCUMENT_SUFFIXES:
            continue
        source_format = SUPPORTED_SUFFIXES.get(suffix, suffix.removeprefix(".") or "unknown")
        if size > MAX_SOURCE_BYTES:
            result.append(MigrationCandidate(relative, "", source_format, None, "low", "file exceeds 2 MiB limit", False, None, "needs_review"))
            continue
        try:
            data = path.read_bytes()
        except OSError:
            result.append(MigrationCandidate(relative, "", source_format, None, "low", "source cannot be read", False, None, "needs_review"))
            continue
        name_reason = _sensitive_reason(path, data)
        source_hash = hashlib.sha256(data).hexdigest()
        if name_reason:
            result.append(MigrationCandidate(relative, source_hash, source_format, None, "low", name_reason, True, name_reason, "needs_review"))
            continue
        if suffix not in SUPPORTED_SUFFIXES:
            result.append(MigrationCandidate(relative, source_hash, source_format, None, "low", "format requires manual review", False, None, "needs_review"))
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            result.append(MigrationCandidate(relative, source_hash, source_format, None, "low", "source is not UTF-8 text", False, None, "needs_review"))
            continue
        sensitive_reason = _sensitive_reason(path, data)
        if sensitive_reason:
            result.append(MigrationCandidate(relative, source_hash, source_format, None, "low", "sensitive content pattern detected", True, sensitive_reason, "needs_review"))
            continue
        suggested_type, confidence, reason, status = _classify(path)
        result.append(MigrationCandidate(relative, source_hash, source_format, suggested_type, confidence, reason, False, None, status))
    return tuple(result)


_TYPE_DIRECTORY = {
    "requirement": Path("docs/requirements"),
    "design": Path("docs/design"),
    "decision": Path("docs/decisions"),
    "task": Path("docs/work/tasks"),
    "bug": Path("docs/work/bugs"),
}
_MIGRATION_ID_RE = re.compile(r"^MIG-[A-Za-z0-9][A-Za-z0-9._-]*$")


def _validate_entry_shape(root: Path, entry: MigrationEntry) -> None:
    if not entry.source_path or Path(entry.source_path).is_absolute() or ".." in Path(entry.source_path).parts:
        raise ValueError(f"invalid migration source path: {entry.item_id}")
    if not entry.suggested_type:
        if entry.target_id or entry.target_path:
            raise ValueError(f"migration target metadata has no type: {entry.item_id}")
        return
    expected_directory = (root / _TYPE_DIRECTORY[entry.suggested_type]).resolve()
    expected_prefix = RECORD_PREFIXES[RecordType(entry.suggested_type)]
    if not entry.target_id or not entry.target_id.startswith(expected_prefix):
        raise ValueError(f"migration target id does not match type: {entry.item_id}")
    if not entry.target_path or Path(entry.target_path).is_absolute() or ".." in Path(entry.target_path).parts:
        raise ValueError(f"invalid migration target path: {entry.item_id}")
    target = (root / entry.target_path).resolve()
    try:
        target.relative_to(expected_directory)
    except ValueError as exc:
        raise ValueError(f"migration target is outside standard directory: {entry.item_id}") from exc
    slug = re.sub(r"[^\w]+", "-", Path(entry.source_path).stem, flags=re.UNICODE).strip("-").lower() or "document"
    expected_name = f"{entry.target_id}-{slug}.md"
    if Path(entry.target_path).name != expected_name:
        raise ValueError(f"migration target path does not match target id: {entry.item_id}")


def _migration_path(root: Path, migration_id: str) -> Path:
    if not _MIGRATION_ID_RE.fullmatch(migration_id):
        raise ValueError(f"invalid migration id: {migration_id}")
    matches = sorted((root / "docs/migrations").glob(f"{migration_id}-*.md"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError(f"migration record not found: {migration_id}")
    raise ValueError(f"multiple migration records found: {migration_id}")


def _target_for(root: Path, migration_id: str, index: int, candidate: MigrationCandidate) -> tuple[str | None, str | None]:
    if candidate.suggested_type not in _TYPE_DIRECTORY:
        return None, None
    prefix = RECORD_PREFIXES[RecordType(candidate.suggested_type)]
    target_id = f"{prefix}{migration_id}-{index:03d}"
    slug = re.sub(r"[^\w]+", "-", Path(candidate.source_path).stem, flags=re.UNICODE).strip("-").lower() or "document"
    target_path = (_TYPE_DIRECTORY[candidate.suggested_type] / f"{target_id}-{slug}.md").as_posix()
    return target_id, target_path


def _entry_block(entry: MigrationEntry) -> str:
    values = entry.as_dict()
    lines = [f"### {entry.item_id}"]
    for key in ("item_id", "source_path", "source_hash", "source_format", "target_id", "target_path", "suggested_type", "confidence", "reason", "sensitive", "status", "result", "error"):
        value = values[key]
        if value is None:
            value = ""
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _plan_text(metadata: RecordMetadata, *, approval: str, entries: Sequence[MigrationEntry], scan_roots: Sequence[str] = (), exclude_patterns: Sequence[str] = (), source_root: str = ".", git_snapshot: Sequence[tuple[str, str]] = (), execution_git: Sequence[tuple[str, str]] = ()) -> str:
    extras = ["mode: migrate", f"approval: {approval}"]
    scan_value = ", ".join(scan_roots) if scan_roots else "N/A"
    exclude_value = ", ".join(exclude_patterns) if exclude_patterns else "N/A"
    body = ["# Migration plan", "", "## Purpose", "Review and approve source-document migration candidates.", "", "## Scan", f"source_root: {source_root}", f"scan_roots: {scan_value}", f"exclude_patterns: {exclude_value}", "", "## Git"]
    body.extend(f"{key}: {value}" for key, value in git_snapshot)
    if execution_git:
        body.extend(["", "## Execution Git"])
        body.extend(f"execution_{key}: {value}" for key, value in execution_git)
    body.extend(["", "## Items", ""])
    body.extend(_entry_block(entry) + "\n" for entry in entries)
    body.extend(["## Evidence", "Plan generated by `pgk migrate plan`.", "", "## Blockers", "N/A", "", "## Next action", "Review candidates and approve eligible items.", ""])
    frontmatter = render_frontmatter(metadata)
    frontmatter = frontmatter.replace("\n---\n", "\n" + "\n".join(extras) + "\n---\n", 1)
    return frontmatter + "\n".join(body)


def _parse_value(block: str, key: str) -> str:
    match = re.search(rf"(?im)^[ \t]*{re.escape(key)}:[ \t]*([^\r\n]*)$", block)
    return match.group(1).strip() if match else ""


def _parse_plan(path: Path) -> MigrationPlan:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)
    if metadata.type is not RecordType.MIGRATION:
        raise ValueError(f"not a migration record: {path}")
    approval = _parse_value(text, "approval") or "pending"
    entries: list[MigrationEntry] = []
    seen: set[str] = set()
    blocks = re.split(r"(?m)^###\s+(ITEM-[A-Za-z0-9._-]+)\s*$", body)
    for index in range(1, len(blocks), 2):
        item_id = blocks[index].strip()
        block = blocks[index + 1]
        if not re.fullmatch(r"ITEM-[0-9]{3,}", item_id):
            raise ValueError(f"invalid migration item id: {item_id}")
        if item_id in seen:
            raise ValueError(f"duplicate migration item: {item_id}")
        seen.add(item_id)
        suggested_type = _parse_value(block, "suggested_type") or None
        target_id = _parse_value(block, "target_id") or None
        target_path = _parse_value(block, "target_path") or None
        source_path = _parse_value(block, "source_path")
        source_hash = _parse_value(block, "source_hash")
        target_id = _parse_value(block, "target_id") or None
        target_path = _parse_value(block, "target_path") or None
        suggested_type = _parse_value(block, "suggested_type") or None
        status = _parse_value(block, "status") or "candidate"
        if not source_path or not source_hash or not re.fullmatch(r"[0-9a-fA-F]{64}", source_hash):
            raise ValueError(f"invalid migration source metadata: {item_id}")
        if status not in {"candidate", "approved", "excluded", "applied", "needs_review", "conflict", "source_changed", "failed"}:
            raise ValueError(f"invalid migration item status: {status}")
        if suggested_type not in set(_TYPE_DIRECTORY) | {None}:
            raise ValueError(f"invalid migration type: {suggested_type}")
        if suggested_type and (not target_id or not target_path):
            raise ValueError(f"migration target metadata is incomplete: {item_id}")
        entry = MigrationEntry(
            item_id=item_id,
            source_path=source_path,
            source_hash=source_hash,
            source_format=_parse_value(block, "source_format"),
            target_id=target_id,
            target_path=target_path,
            suggested_type=suggested_type,
            confidence=_parse_value(block, "confidence"),
            reason=_parse_value(block, "reason"),
            sensitive=_parse_value(block, "sensitive").casefold() == "true",
            status=status,
            result=_parse_value(block, "result"),
            error=_parse_value(block, "error"),
        )
        if _parse_value(block, "item_id") != item_id:
            raise ValueError(f"migration item heading does not match item_id: {item_id}")
        _validate_entry_shape(path.parents[2], entry)
        entries.append(entry)
    source_root = _parse_value(body, "source_root") or "."
    git_snapshot = tuple((key, _parse_value(body, key)) for key in ("branch", "head", "worktree", "dirty") if _parse_value(body, key))
    execution_git = tuple((key, _parse_value(body, f"execution_{key}")) for key in ("branch", "head", "worktree", "dirty") if _parse_value(body, f"execution_{key}"))
    return MigrationPlan(metadata.id, path, metadata.status.value, approval, tuple(entries), source_root, git_snapshot, execution_git)


def load_migration_plan(root: str | Path, migration_id: str) -> MigrationPlan:
    root = Path(root).resolve()
    plan = _parse_plan(_migration_path(root, migration_id))
    if plan.migration_id != migration_id:
        raise ValueError(f"migration record id does not match filename: {migration_id}")
    return plan


def _next_migration_id(root: Path) -> str:
    used = {
        match.group(1)
        for path in (root / "docs/migrations").glob("MIG-*-migration-plan.md")
        if (match := re.match(r"^(MIG-[A-Za-z0-9][A-Za-z0-9._-]*)-migration-plan\.md$", path.name))
    }
    number = 1
    while f"MIG-{number:03d}" in used:
        number += 1
    return f"MIG-{number:03d}"


def create_migration_plan(
    root: str | Path,
    candidates: Sequence[MigrationCandidate],
    *,
    migration_id: str | None = None,
    scan_roots: Sequence[str] = (),
    exclude_patterns: Sequence[str] = (),
    dry_run: bool = False,
) -> Path:
    root = Path(root).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    migration_id = migration_id or _next_migration_id(root)
    if not _MIGRATION_ID_RE.fullmatch(migration_id):
        raise ValueError("migration id must use MIG- prefix and safe filename characters")
    if migration_id in {
        match.group(1)
        for path in (root / "docs/migrations").glob("MIG-*-migration-plan.md")
        if (match := re.match(r"^(MIG-[A-Za-z0-9][A-Za-z0-9._-]*)-migration-plan\.md$", path.name))
    }:
        raise FileExistsError(f"migration record already exists: {migration_id}")
    entries: list[MigrationEntry] = []
    for index, candidate in enumerate(sorted(candidates, key=lambda item: item.source_path), 1):
        target_id, target_path = _target_for(root, migration_id, index, candidate)
        entry_status = candidate.status
        if candidate.suggested_type is None and entry_status == "candidate":
            entry_status = "needs_review"
        entries.append(MigrationEntry(
            item_id=f"ITEM-{index:03d}", source_path=candidate.source_path, source_hash=candidate.source_hash,
            source_format=candidate.source_format, target_id=target_id, target_path=target_path,
            suggested_type=candidate.suggested_type, confidence=candidate.confidence, reason=candidate.reason,
            sensitive=candidate.sensitive, status=entry_status,
        ))
    path = root / "docs/migrations" / f"{migration_id}-migration-plan.md"
    if dry_run:
        return path
    created = create_record(root, "migration", migration_id, "Migration plan", status=Status.DRAFT, dry_run=False)
    metadata, _ = parse_frontmatter(created.read_text(encoding="utf-8"))
    git_snapshot = _capture_git_snapshot(root)
    created.write_text(_plan_text(metadata, approval="pending", entries=entries, scan_roots=scan_roots, exclude_patterns=exclude_patterns, git_snapshot=git_snapshot), encoding="utf-8")
    update_indexes(root)
    append_activity(root, "pgk", "plan", migration_id, "N/A", f"planned {len(entries)} migration items")
    return created


def _capture_git_snapshot(root: Path) -> tuple[tuple[str, str], ...]:
    try:
        context = inspect_git(root)
    except ValueError:
        return (("branch", "unavailable"), ("head", "unavailable"), ("worktree", str(root)), ("dirty", "unknown"))
    return (("branch", context.branch), ("head", context.head), ("worktree", str(root)), ("dirty", str(context.dirty).lower()))


def _rewrite_plan(plan: MigrationPlan, *, approval: str, entries: Sequence[MigrationEntry], status: str | None = None, execution_git: Sequence[tuple[str, str]] | None = None) -> None:
    metadata, _ = parse_frontmatter(plan.path.read_text(encoding="utf-8"))
    if status:
        metadata = replace(metadata, status=Status(status))
    text = plan.path.read_text(encoding="utf-8")
    scan_raw = _parse_value(text, "scan_roots")
    exclude_raw = _parse_value(text, "exclude_patterns")
    scan_roots = tuple(item.strip() for item in scan_raw.split(",") if item.strip() and item.strip().casefold() != "n/a")
    exclude = tuple(item.strip() for item in exclude_raw.split(",") if item.strip() and item.strip().casefold() != "n/a")
    plan.path.write_text(_plan_text(metadata, approval=approval, entries=entries, scan_roots=scan_roots, exclude_patterns=exclude, source_root=plan.source_root, git_snapshot=plan.git_snapshot, execution_git=execution_git if execution_git is not None else plan.execution_git), encoding="utf-8")


def approve_migration(root: str | Path, migration_id: str, *, item_ids: Sequence[str] | None = None, exclude_item_ids: Sequence[str] = ()) -> Path:
    root = Path(root).resolve()
    plan = load_migration_plan(root, migration_id)
    selected = set(item_ids) if item_ids is not None else None
    excluded = set(exclude_item_ids)
    known = {entry.item_id for entry in plan.entries}
    unknown = (selected or set()) | excluded
    if not unknown <= known:
        raise ValueError("unknown migration item id: " + ", ".join(sorted(unknown - known)))
    changed = False
    entries: list[MigrationEntry] = []
    for entry in plan.entries:
        current = entry
        if entry.status in {"candidate", "failed", "source_changed", "conflict"} and entry.item_id in excluded:
            current = replace(entry, status="excluded")
            changed = True
        elif entry.status in {"candidate", "failed", "source_changed", "conflict"} and (selected is None or entry.item_id in selected):
            current = replace(entry, status="approved")
            source = (root / entry.source_path).resolve()
            if source.is_file():
                try:
                    data = source.read_bytes()
                    if _sensitive_reason(source, data):
                        current = replace(entry, status="needs_review", error="sensitive_source")
                    else:
                        current = replace(current, source_hash=hashlib.sha256(data).hexdigest())
                except OSError:
                    current = replace(entry, status="failed", error="source_missing")
            changed = True
        entries.append(current)
    approval = "approved" if any(entry.status == "approved" for entry in entries) else plan.approval
    if changed:
        _rewrite_plan(plan, approval=approval, entries=entries, status="accepted")
        append_activity(Path(root), "pgk", "approve", migration_id, "N/A", f"approved {sum(entry.status == 'approved' for entry in entries)} items")
    return plan.path


@dataclass(frozen=True, slots=True)
class MigrationApplyResult:
    migration_id: str
    applied: list[str]
    skipped: list[str]
    conflicts: list[str]
    failed: list[str]
    changed: list[str]
    verification_paths: list[str]
    dry_run: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "migration_id": self.migration_id,
            "applied": list(self.applied),
            "skipped": list(self.skipped),
            "conflicts": list(self.conflicts),
            "failed": list(self.failed),
            "changed": list(self.changed),
            "verification_paths": list(self.verification_paths),
            "dry_run": self.dry_run,
        }


def _render_governance_copy(root: Path, migration_id: str, entry: MigrationEntry, source_text: str) -> str:
    if not entry.target_id or not entry.suggested_type or entry.suggested_type not in _TYPE_DIRECTORY:
        raise ValueError("migration item has no supported target type")
    metadata = RecordMetadata(
        entry.target_id,
        RecordType(entry.suggested_type),
        Status.DRAFT,
        date.today(),
        date.today(),
        [migration_id],
    )
    extras = [
        f"migration_id: {migration_id}",
        f"source_path: {entry.source_path}",
        f"source_hash: {entry.source_hash}",
        f"source_format: {entry.source_format}",
        "migration_status: applied",
        f"confidence: {entry.confidence}",
    ]
    frontmatter = render_frontmatter(metadata).replace("\n---\n", "\n" + "\n".join(extras) + "\n---\n", 1)
    return (
        frontmatter
        + f"> This draft was copied from `{entry.source_path}` by migration `{migration_id}`.\n> Review and confirm it before using it as a project requirement or design.\n\n"
        + "<!-- PGK_SOURCE_BEGIN -->\n"
        + source_text.rstrip()
        + "\n<!-- PGK_SOURCE_END -->\n"
    )


def _normalize_generated(text: str) -> str:
    return re.sub(r"(?im)^(created|updated):\s*\d{4}-\d{2}-\d{2}\s*$", r"\1: <date>", text)


def _verification_text(metadata: RecordMetadata, migration_id: str, applied: Sequence[str], paths: Sequence[str]) -> str:
    return render_frontmatter(metadata) + "\n".join([
        f"# Verify migration {migration_id}", "", "## Purpose", f"Verify approved migration batch {migration_id}.",
        "", "## Owner", "pgk", "", "## Scope", f"Migration batch `{migration_id}`.", "",
        "## Acceptance", "All approved items were applied or idempotently skipped; source files remained in place.",
        "", "## Evidence", f"Applied items: {', '.join(applied) or 'none'}.", f"Generated paths: {', '.join(paths) or 'none'}.",
        "", "## Blockers", "none", "", "## Next action", "Review the generated governance drafts.", "",
    ])


def _create_migration_verification(root: Path, migration_id: str, applied: Sequence[str], paths: Sequence[str]) -> list[str]:
    verification_id = f"VER-{migration_id}"
    existing = sorted((root / "docs/verification").glob(f"{verification_id}-*.md"))
    if existing:
        return [path.relative_to(root).as_posix() for path in existing]
    created = create_record(root, "verification", verification_id, f"Verify migration {migration_id}", related=[migration_id], status=Status.VERIFIED)
    metadata, _ = parse_frontmatter(created.read_text(encoding="utf-8"))
    created.write_text(_verification_text(metadata, migration_id, applied, paths), encoding="utf-8")
    return [created.relative_to(root).as_posix()]


def apply_migration(root: str | Path, migration_id: str, *, item_ids: Sequence[str] | None = None, dry_run: bool = False) -> MigrationApplyResult:
    root = Path(root).resolve()
    plan = load_migration_plan(root, migration_id)
    selected = set(item_ids) if item_ids is not None else None
    known = {entry.item_id for entry in plan.entries}
    if selected is not None and not selected <= known:
        raise ValueError("unknown migration item id: " + ", ".join(sorted(selected - known)))
    approved_count = sum(
        entry.status == "approved" and (selected is None or entry.item_id in selected)
        for entry in plan.entries
    )
    applied: list[str] = []
    skipped: list[str] = []
    conflicts: list[str] = []
    failed: list[str] = []
    changed: list[str] = []
    verification_paths: list[str] = []
    updated_entries: list[MigrationEntry] = []
    generated_paths: list[str] = []

    for entry in plan.entries:
        if entry.status != "approved" or (selected is not None and entry.item_id not in selected):
            if selected is None and entry.status not in {"candidate", "approved"}:
                skipped.append(entry.item_id)
            updated_entries.append(entry)
            continue
        current = entry
        try:
            source = (root / entry.source_path).resolve()
            _relative(root, source)
            if not source.is_file():
                current = replace(entry, status="failed", error="source_missing")
                failed.append(entry.item_id)
                updated_entries.append(current)
                continue
            data = source.read_bytes()
            actual_hash = hashlib.sha256(data).hexdigest()
            if actual_hash != entry.source_hash:
                current = replace(entry, status="source_changed", error="source_hash_mismatch")
                changed.append(entry.item_id)
                updated_entries.append(current)
                continue
            if entry.sensitive:
                failed.append(entry.item_id)
                updated_entries.append(replace(entry, status="failed", error="sensitive_source"))
                continue
            sensitivity = _sensitive_reason(source, data)
            if sensitivity:
                failed.append(entry.item_id)
                updated_entries.append(replace(entry, status="failed", error="sensitive_source"))
                continue
            text = data.decode("utf-8")
            if not entry.target_path:
                current = replace(entry, status="failed", error="unsupported_target_type")
                failed.append(entry.item_id)
                updated_entries.append(current)
                continue
            target = (root / entry.target_path).resolve()
            _validate_entry_shape(root, entry)
            _relative(root, target)
            generated = _render_governance_copy(root, migration_id, entry, text)
            if target.exists():
                if _normalize_generated(target.read_text(encoding="utf-8")) == _normalize_generated(generated):
                    skipped.append(entry.item_id)
                    generated_paths.append(entry.target_path)
                    updated_entries.append(replace(entry, status="applied", result="idempotent"))
                else:
                    conflicts.append(entry.item_id)
                    updated_entries.append(replace(entry, status="conflict", error="target_exists"))
                continue
            if dry_run:
                skipped.append(entry.item_id)
                generated_paths.append(entry.target_path)
                updated_entries.append(entry)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8", newline="") as handle:
                handle.write(generated)
            applied.append(entry.item_id)
            generated_paths.append(entry.target_path)
            updated_entries.append(replace(entry, status="applied", result="written"))
        except UnicodeDecodeError:
            failed.append(entry.item_id)
            updated_entries.append(replace(current, status="failed", error="source_not_utf8"))
        except (OSError, ValueError) as exc:
            failed.append(entry.item_id)
            category = "target_path_invalid" if "inside project root" in str(exc) else "write_failed"
            updated_entries.append(replace(current, status="failed", error=category))

    if dry_run:
        return MigrationApplyResult(migration_id, applied, skipped, conflicts, failed, changed, generated_paths, True)

    if approved_count == 0:
        return MigrationApplyResult(migration_id, applied, skipped, conflicts, failed, changed, generated_paths)

    terminal_success = not conflicts and not failed and not changed and all(
        entry.status in {"applied", "excluded", "needs_review", "conflict", "source_changed", "failed"} for entry in updated_entries
    )
    all_approved_handled = all(entry.status != "approved" for entry in updated_entries)
    next_status = "verified" if terminal_success and all_approved_handled else ("blocked" if conflicts or failed or changed else None)
    execution_git = _capture_git_snapshot(root)
    _rewrite_plan(plan, approval=plan.approval, entries=updated_entries, status=next_status or "in_progress", execution_git=execution_git)
    update_indexes(root)
    append_activity(root, "pgk", "apply", migration_id, "N/A", f"applied {len(applied)} items; conflicts {len(conflicts)}; failed {len(failed)}")
    if next_status == "verified":
        verification_paths = _create_migration_verification(root, migration_id, applied, generated_paths)
        update_indexes(root)
    return MigrationApplyResult(migration_id, applied, skipped, conflicts, failed, changed, verification_paths)


__all__ = [
    "MigrationApplyResult", "MigrationCandidate", "MigrationEntry", "MigrationPlan", "apply_migration",
    "approve_migration", "create_migration_plan", "load_migration_plan", "scan_project",
]
