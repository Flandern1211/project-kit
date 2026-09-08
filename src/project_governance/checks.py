"""Deterministic, read-only governance checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

from .authorization import _authorization_fields, _when
from .frontmatter import FrontmatterError, parse_frontmatter
from .git_context import inspect_git
from .migration import _normalize_generated, _render_governance_copy, load_migration_plan

BASELINE = ("AGENTS.md", "README.md", ".gitignore", ".project-governance.toml", "CONTRIBUTING.md", "CHANGELOG.md", "docs/INDEX.md", "docs/STATUS.md")
REQUIRED_VIEWS = ("docs/STATUS.md", "docs/WORKFLOW.md", "docs/work/BOARD.md", "docs/activity/ACTIVITY.md")
REQUIRED_STATUS_FIELDS = ("project_stage", "current_requirement", "current_design", "current_task", "owner", "blocker", "next_action", "updated", "git_state")
REQUIRED_ARTIFACTS = (
    "docs/templates/INDEX.md",
    "docs/templates/requirement.md",
    "docs/templates/design.md",
    "docs/templates/decision.md",
    "docs/templates/task.md",
    "docs/templates/bug.md",
    "docs/templates/review.md",
    "docs/templates/verification.md",
    "docs/templates/migration.md",
    "docs/migrations/INDEX.md",
    "docs/operations/runbooks/INDEX.md",
    "docs/operations/incidents/INDEX.md",
    "docs/operations/postmortems/INDEX.md",
)
VIEW_MARKERS = {
    "docs/WORKFLOW.md": "workflow",
    "docs/work/BOARD.md": "board",
    "docs/activity/ACTIVITY.md": "activity",
}
RECORD_INDEXES = {
    "requirement": "docs/requirements/INDEX.md", "design": "docs/design/INDEX.md", "decision": "docs/decisions/INDEX.md",
    "task": "docs/work/tasks/INDEX.md", "bug": "docs/work/bugs/INDEX.md", "review": "docs/reviews/INDEX.md", "verification": "docs/verification/INDEX.md", "migration": "docs/migrations/INDEX.md",
}
PROJECT_STAGES = {"initialized", "requirements_discussion", "requirements_review", "adoption_review", "active_development", "maintenance", "blocked"}
RECORD_ID_RE = re.compile(r"^(REQ|DES|ADR|TASK|BUG|REVIEW|VER|INC|MIG)-[A-Za-z0-9][A-Za-z0-9._-]*$")
RECORD_PREFIXES = {"requirement": "REQ-", "design": "DES-", "decision": "ADR-", "task": "TASK-", "bug": "BUG-", "review": "REVIEW-", "verification": "VER-", "migration": "MIG-"}

@dataclass(frozen=True)
class CheckResult:
    ok: bool
    issues: tuple[dict[str, str], ...]
    checked_files: tuple[str, ...]
    def as_dict(self) -> dict[str, object]:
        return {"ok": self.ok, "issues": [dict(item) for item in self.issues], "checked_files": list(self.checked_files)}

def _issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({"code": code, "path": path, "message": message})

def _body_sections(body: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?im)^##\s+([^\n]+)\s*$", body))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result[match.group(1).strip().casefold()] = body[match.end():end].strip()
    return result

def _scope_values(body: str) -> tuple[str, ...]:
    sections = _body_sections(body)
    source = sections.get("scope", "") + "\n" + sections.get("files", "")
    values: list[str] = []
    for line in source.splitlines():
        value = re.sub(r"^\s*[-*]\s*", "", line).strip()
        inline = re.search(r"`([^`]+)`", value)
        if inline:
            value = inline.group(1)
        value = re.sub(r"[`。，,;:。]+$", "", value).strip().strip("`")
        match = re.match(r"^(?:files?)\s*:\s*(.+)$", value, re.I)
        if match: value = match.group(1).strip()
        if value and not value.startswith("#") and not value.startswith("No "):
            values.extend(item.strip().strip("`") for item in re.split(r"[,;]", value) if item.strip())
    return tuple(dict.fromkeys(values))

def _declared_branch(body: str) -> str | None:
    matches = re.findall(r"(?im)^\s*(?:branch|git_branch)\s*:\s*([^\s]+)", body)
    for value in reversed(matches):
        value = value.strip("`")
        if value.casefold() != "n/a":
            return value
    return matches[0].strip("`") if matches else None


def _section_value(body: str, name: str) -> str:
    match = re.search(rf"(?ims)^##\s+{re.escape(name)}\s*$([\s\S]*?)(?=^##\s+|\Z)", body)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        value = line.strip(" -*\t`").strip()
        if value:
            return value
    return ""


def _is_declared(value: str) -> bool:
    return bool(value and value.casefold() not in {"n/a", "none", "not declared", "not provided"})

def _check_authorization(path: str, text: str, issues: list[dict[str, str]]) -> None:
    if not re.search(r"(?im)^##\s+Authorization\s*$", text): return
    fields = _authorization_fields(text)
    # Templates intentionally include an empty Authorization section.  Treat
    # that placeholder as "not supplied"; validate the section only once an
    # authorization field is actually declared.
    if not fields:
        return
    missing = [field for field in ("action", "target", "scope", "valid_from", "expires_at") if not fields.get(field)]
    if missing: _issue(issues, "invalid_authorization", path, "authorization missing: " + ", ".join(missing))
    if fields.get("status", "active").lower() not in {"active", "approved", "accepted"}:
        _issue(issues, "invalid_authorization", path, "authorization is not active")
    if fields.get("revoked", "").lower() in {"true", "yes", "1", "revoked"}:
        _issue(issues, "invalid_authorization", path, "authorization is revoked")
    start, expiry = _when(fields.get("valid_from", "")), _when(fields.get("expires_at", ""))
    if start is None or expiry is None or (start and expiry and expiry <= start):
        _issue(issues, "invalid_authorization", path, "authorization validity interval is invalid")

def run_checks(root: str | Path) -> CheckResult:
    root = Path(root); issues: list[dict[str, str]] = []
    ignored_dirs = {".git", ".agent", ".pytest-tmp", ".pytest_cache", ".superpowers", ".worktrees", ".venv", ".mypy_cache", ".ruff_cache", "node_modules", "dist", "build", ".tmp", "tmp", "temp"}
    files = sorted(path for path in root.rglob("*.md") if not any(part in ignored_dirs or part.startswith(".pytest-tmp") for part in path.relative_to(root).parts))
    checked_files = tuple(path.relative_to(root).as_posix() for path in files)
    ids: dict[str, str] = {}; records: list[tuple[str, object, str, str]] = []
    for path in files:
        relative = path.relative_to(root).as_posix(); text = path.read_text(encoding="utf-8"); metadata = None; body = text
        if text.startswith("---"):
            try: metadata, body = parse_frontmatter(text)
            except FrontmatterError as exc:
                message = str(exc)
                code = "invalid_status" if "status" in message.lower() and ("invalid" in message.lower() or "not a valid" in message.lower()) else "invalid_frontmatter"; _issue(issues, code, relative, message)
                candidate = re.search(r"(?im)^id:\s*(\S+)", text)
                if candidate:
                    candidate_id = candidate.group(1)
                    if candidate_id in ids: _issue(issues, "duplicate_id", relative, f"duplicate id: {candidate_id}")
                    ids[candidate_id] = relative
            if metadata is not None:
                if not RECORD_ID_RE.fullmatch(metadata.id): _issue(issues, "invalid_record_id", relative, f"invalid record id: {metadata.id}")
                if metadata.type.value in RECORD_PREFIXES and not metadata.id.startswith(RECORD_PREFIXES[metadata.type.value]): _issue(issues, "record_type_id_mismatch", relative, f"record id prefix does not match type: {metadata.type.value}")
                for related in metadata.related:
                    if not RECORD_ID_RE.fullmatch(related): _issue(issues, "invalid_related_id", relative, f"invalid related id: {related}")
                if metadata.id in ids: _issue(issues, "duplicate_id", relative, f"duplicate id: {metadata.id}")
                ids[metadata.id] = relative; records.append((relative, metadata, body, text)); _check_authorization(relative, text, issues)
                canonical_record = relative.startswith("docs/work/tasks/") or relative.startswith("docs/work/bugs/")
                if canonical_record and metadata.type.value in {"task", "bug"}:
                    sections = _body_sections(body)
                    for required in ("owner", "scope", "files", "evidence", "blockers", "next action", "git"):
                        if required not in sections: _issue(issues, "missing_record_field", relative, f"missing required field: {required.title()}")
                    git_section = sections.get("git", "")
                    handoff_match = re.search(r"PGK_HANDOFF_START\s*-->\s*(.*?)\s*<!--\s*PGK_HANDOFF_END", body, re.S)
                    handoff = handoff_match.group(1) if handoff_match else ""
                    for required in ("branch", "worktree", "base_commit", "head_commit"):
                        if not re.search(rf"(?im)^\s*{re.escape(required)}\s*:\s*(?:N/A|[^\s]+)", git_section):
                            _issue(issues, "missing_record_field", relative, f"missing required field: {required.replace('_', ' ').title()}")
                    if handoff.strip():
                            for field in ("Branch", "HEAD", "Worktree", "Dirty", "Uncommitted"):
                                if not re.search(rf"(?im)^\s*{re.escape(field)}\s*:", handoff):
                                    _issue(issues, "missing_git_field", relative, f"missing task Git field: {field}")
                    if metadata.status.value in {"in_progress", "in_review", "blocked"}:
                        worktree_match = re.search(r"(?im)^\s*worktree\s*:\s*(\S.*)$", git_section)
                        handoff_worktree = re.search(r"(?im)^\s*Worktree\s*:\s*(\S.*)$", handoff)
                        for required, value in (
                            ("Owner", _section_value(body, "Owner")),
                            ("Files", _section_value(body, "Files")),
                            ("Branch", _declared_branch(body) or ""),
                            ("Worktree", worktree_match.group(1).strip() if worktree_match else (handoff_worktree.group(1).strip() if handoff_worktree else "")),
                        ):
                            if not _is_declared(value):
                                _issue(issues, "missing_record_value", relative, f"active record field is not declared: {required}")
                elif metadata.type.value in {"review", "verification"}:
                    sections = _body_sections(body)
                    for required in ("owner", "scope", "evidence", "blockers", "next action"):
                        if required not in sections: _issue(issues, "missing_record_field", relative, f"missing required field: {required.title()}")
                    if metadata.type.value == "verification" and "acceptance" not in sections:
                        _issue(issues, "missing_record_field", relative, "missing required field: Acceptance")
                    if metadata.type.value == "review":
                        for required in ("base commit", "head commit", "findings", "verdict"):
                            if required not in sections: _issue(issues, "missing_record_field", relative, f"missing required field: {required.title()}")
                    if metadata.status.value in {"verified", "done"}:
                        terminal_fields = ("owner", "scope", "acceptance", "evidence") if metadata.type.value == "verification" else ("owner", "scope", "acceptance", "evidence", "base commit", "head commit", "findings", "verdict")
                        for required in terminal_fields:
                            if not _is_declared(_section_value(body, required)):
                                _issue(issues, "missing_record_value", relative, f"terminal record field is not declared: {required.title()}" )
        for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", text):
            target = target.split("#", 1)[0]
            if target and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) and not (path.parent / target).exists(): _issue(issues, "broken_link", relative, f"broken link: {target}")
    for relative in BASELINE:
        if not (root / relative).exists(): _issue(issues, "missing_baseline", relative, f"missing required file: {relative}")
    status_text = (root / "docs/STATUS.md").read_text(encoding="utf-8") if (root / "docs/STATUS.md").exists() else ""
    generated_project = bool(re.search(r"(?im)^\s*project_stage\s*:", status_text))
    governed_project = generated_project or (root / ".project-governance.toml").exists() or any("PGK_GENERATED:" in path.read_text(encoding="utf-8") for path in files)
    if governed_project:
        for relative in REQUIRED_ARTIFACTS:
            if not (root / relative).exists():
                _issue(issues, "missing_required_artifact", relative, f"missing required scaffold artifact: {relative}")
        for relative in REQUIRED_VIEWS:
            if not (root / relative).exists(): _issue(issues, "missing_required_view", relative, f"missing required view: {relative}")
        for kind, relative in RECORD_INDEXES.items():
            index = root / relative
            if not index.exists(): _issue(issues, "missing_record_index", relative, f"missing required record index: {relative}"); continue
            content = index.read_text(encoding="utf-8")
            for record_path, metadata, _body, _text in records:
                if metadata.type.value == kind and not re.search(rf"\[{re.escape(metadata.id)}\]\(", content): _issue(issues, "unindexed_record", record_path, f"record is not linked from {relative}: {metadata.id}")
    record_by_id = {metadata.id: (relative, metadata) for relative, metadata, _body, _text in records}
    for relative, metadata, _body, _text in records:
        for related in metadata.related:
            if RECORD_ID_RE.fullmatch(related) and related not in record_by_id:
                _issue(issues, "unknown_related_id", relative, f"related record does not exist: {related}")
    for relative, metadata, _body, _text in records:
        if metadata.type.value != "migration":
            continue
        try:
            plan = load_migration_plan(root, metadata.id)
        except (OSError, ValueError) as exc:
            _issue(issues, "invalid_migration_item", relative, str(exc))
            continue
        allowed_statuses = {"candidate", "approved", "excluded", "applied", "needs_review", "conflict", "source_changed", "failed"}
        for entry in plan.entries:
            if entry.status not in allowed_statuses:
                _issue(issues, "invalid_migration_item", relative, f"invalid migration item status: {entry.status}")
                continue
            source = (root / entry.source_path).resolve()
            try:
                source.relative_to(root.resolve())
            except ValueError:
                _issue(issues, "invalid_migration_item", relative, f"migration source escapes project root: {entry.source_path}")
                continue
            if not source.is_file():
                _issue(issues, "missing_migration_source", relative, f"migration source is missing: {entry.source_path}")
                continue
            if entry.source_hash:
                import hashlib
                if hashlib.sha256(source.read_bytes()).hexdigest() != entry.source_hash:
                    _issue(issues, "migration_source_changed", relative, f"migration source changed: {entry.source_path}")
            if entry.sensitive and entry.status in {"approved", "applied"}:
                _issue(issues, "sensitive_migration_source", relative, f"sensitive migration item is actionable: {entry.item_id}")
            if entry.target_path:
                target = (root / entry.target_path).resolve()
                try:
                    target.relative_to(root.resolve())
                except ValueError:
                    _issue(issues, "invalid_migration_item", relative, f"migration target escapes project root: {entry.target_path}")
                    continue
                if entry.status == "applied" and not target.is_file():
                    _issue(issues, "migration_target_conflict", relative, f"applied migration target is missing: {entry.target_path}")
                elif entry.status in {"approved", "applied"} and target.is_file() and not entry.sensitive:
                    try:
                        source_text = source.read_text(encoding="utf-8")
                        expected = _render_governance_copy(root, metadata.id, entry, source_text)
                        if _normalize_generated(target.read_text(encoding="utf-8")) != _normalize_generated(expected):
                            _issue(issues, "migration_target_conflict", relative, f"migration target content differs: {entry.target_path}")
                    except (OSError, UnicodeDecodeError, ValueError):
                        _issue(issues, "migration_target_conflict", relative, f"migration target cannot be verified: {entry.target_path}")
    for relative, metadata, _body, _text in records:
        if metadata.type.value != "task" or metadata.status.value not in {"in_progress", "in_review", "blocked"}:
            continue
        related = [record_by_id.get(item) for item in metadata.related]
        reqs = [item for item in related if item and item[1].type.value == "requirement"]
        designs = [item for item in related if item and item[1].type.value in {"design", "decision"}]
        if not reqs: _issue(issues, "missing_upstream_record", relative, "actionable task requires a related requirement")
        elif not any(item[1].status.value == "accepted" for item in reqs): _issue(issues, "unaccepted_upstream_record", relative, "related requirement is not accepted")
        if not designs: _issue(issues, "missing_upstream_record", relative, "actionable task requires an accepted design or decision")
        elif not any(item[1].status.value == "accepted" for item in designs): _issue(issues, "unaccepted_upstream_record", relative, "related design or decision is not accepted")
    status_path = root / "docs/STATUS.md"
    if status_path.exists():
        match = re.search(r"(?im)^\s*project_stage\s*:\s*([^\s]+)", status_text)
        if governed_project and (not match or match.group(1) not in PROJECT_STAGES): _issue(issues, "invalid_project_stage", "docs/STATUS.md", "project_stage is missing or invalid")
        if governed_project:
            for key in REQUIRED_STATUS_FIELDS:
                if not re.search(rf"(?im)^\s*{key}\s*:", status_text): _issue(issues, "missing_status_field", "docs/STATUS.md", f"missing status field: {key}")
    if governed_project:
        for view in ("docs/WORKFLOW.md", "docs/work/BOARD.md"):
            view_path = root / view
            if view_path.exists() and "PGK_GENERATED:" not in view_path.read_text(encoding="utf-8"):
                _issue(issues, "invalid_view_marker", view, "governance view is missing PGK_GENERATED marker")
        for view, marker in ((relative, f"{kind}-index") for kind, relative in RECORD_INDEXES.items()):
            view_path = root / view
            if view_path.exists() and f"<!-- PGK_GENERATED: {marker} -->" not in view_path.read_text(encoding="utf-8"):
                _issue(issues, "invalid_view_marker", view, "record index is missing PGK_GENERATED marker")
        work_index = root / "docs/work/INDEX.md"
        if work_index.exists() and "<!-- PGK_GENERATED: work-index -->" not in work_index.read_text(encoding="utf-8"):
            _issue(issues, "invalid_view_marker", "docs/work/INDEX.md", "work index is missing PGK_GENERATED marker")
        activity_view = root / "docs/activity/ACTIVITY.md"
        if activity_view.exists() and "<!-- PGK_GENERATED: activity -->" not in activity_view.read_text(encoding="utf-8"):
            _issue(issues, "invalid_view_marker", "docs/activity/ACTIVITY.md", "activity view is missing PGK_GENERATED marker")
        workflow = root / "docs/WORKFLOW.md"
        if workflow.exists():
            workflow_text = workflow.read_text(encoding="utf-8")
            if "active_development --> blocked" not in workflow_text or "blocked --> active_development" not in workflow_text:
                _issue(issues, "invalid_workflow_contract", "docs/WORKFLOW.md", "workflow lacks blocked entry/recovery")
        board = root / "docs/work/BOARD.md"
        if board.exists() and "| ID | type | status | owner | related | branch/worktree | verification | blocker | next |" not in board.read_text(encoding="utf-8"):
                _issue(issues, "invalid_board_contract", "docs/work/BOARD.md", "board header is invalid")
        if activity_view.exists() and "<!-- timestamp | actor | action | record_id | git_ref | result -->" not in activity_view.read_text(encoding="utf-8"):
            _issue(issues, "invalid_activity_header", "docs/activity/ACTIVITY.md", "activity header is invalid")
    activity = root / "docs/activity/ACTIVITY.md"
    if activity.exists():
        for number, line in enumerate(activity.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.lstrip().startswith(("#", "<!--")): continue
            fields = line.split(" | ")
            if len(fields) != 6 or any(not field.strip() for field in fields) or not re.match(r"^\d{4}-\d{2}-\d{2}(?:T|$)", fields[0].strip()):
                _issue(issues, "invalid_activity_line", "docs/activity/ACTIVITY.md", f"line {number} must have six fields")
    scopes: list[tuple[str, str, str]] = []; declared_branches: set[str] = set()
    active_records = {"in_progress", "in_review", "blocked"}
    for relative, metadata, body, _text in records:
        if metadata.type.value not in {"task", "bug"}: continue
        branch = _declared_branch(body)
        if branch: declared_branches.add(branch)
        if metadata.status.value not in active_records: continue
        scopes.extend((scope, metadata.id, relative) for scope in _scope_values(body))
    for index, (scope, record_id, relative) in enumerate(scopes):
        for other_scope, other_id, other_relative in scopes[index + 1:]:
            left = scope.replace('\\', '/').strip().lstrip('./').casefold().rstrip('/')
            right = other_scope.replace('\\', '/').strip().lstrip('./').casefold().rstrip('/')
            if left and right and left != 'n/a' and right != 'n/a' and (left == right or left.startswith(right + '/') or right.startswith(left + '/')):
                _issue(issues, "overlapping_file_scope", min(relative, other_relative), f"file scope {scope} overlaps {record_id} and {other_id}")
    try: git = inspect_git(root)
    except ValueError: git = None
    same_repository = False
    if git is not None:
        try:
            git_root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()).resolve()
            same_repository = git_root == root.resolve()
        except (OSError, subprocess.CalledProcessError):
            same_repository = False
    if git is not None and same_repository:
        if git.dirty: _issue(issues, "dirty_worktree", ".git", "Git worktree has uncommitted changes")
        for worktree in git.worktrees:
            if worktree.get("dirty") == "true": _issue(issues, "dirty_worktree", worktree.get("path", ".git"), "linked Git worktree has uncommitted changes")
        try: branches = subprocess.run(["git", "branch", "--format=%(refname:short)"], cwd=root, check=True, capture_output=True, text=True).stdout.splitlines()
        except (OSError, subprocess.CalledProcessError): branches = []
        registered = {value.strip().removeprefix("refs/heads/").casefold() for value in declared_branches}
        for branch in sorted(branches):
            normalized_branch = branch.strip().removeprefix("refs/heads/")
            if (normalized_branch.startswith("task/") or normalized_branch.startswith("bug/")) and normalized_branch.casefold() not in registered:
                _issue(issues, "unregistered_branch", ".git", f"task/bug branch is not registered: {normalized_branch}")
    if governed_project and git is None:
        if any(metadata.type.value in {"task", "bug"} and metadata.status.value in {"in_progress", "in_review", "blocked"} for _relative, metadata, _body, _text in records):
            _issue(issues, "git_not_initialized", ".git", "actionable work requires an initialized Git repository")
    if governed_project:
        status_git = re.search(r"(?im)^\s*git_state\s*:\s*([^\s]+)", status_text)
        expected_git_state = "git_initialized" if same_repository else "git_not_initialized"
        if status_git and status_git.group(1) != expected_git_state:
            _issue(issues, "git_state_mismatch", "docs/STATUS.md", f"status git_state is {status_git.group(1)}, expected {expected_git_state}")
    issues.sort(key=lambda item: (item["code"], item["path"], item["message"]))
    return CheckResult(not issues, tuple(issues), checked_files)

__all__ = ["BASELINE", "CheckResult", "run_checks"]
