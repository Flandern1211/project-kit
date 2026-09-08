"""Safe initialization and read-only adoption inspection."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from .git_context import inspect_git

_EMPTY = "# {title}\n\nNo records yet.\n"
STANDARD_FILES: dict[str, str] = {
    "AGENTS.md": "# Agent instructions for {project_name}\n\n## Read before acting\nRead `AGENTS.md`, `docs/INDEX.md`, `docs/STATUS.md`, linked requirement/design/task/bug/review/verification records, then Git branch, HEAD, worktree and status.\n\n## State gates\nRequirements are drafts until user confirmation. Before implementation require an accepted requirement, applicable design/ADR, and TASK/BUG with owner, scope and file range. Stop and record blockers for missing or conflicting records.\n\n## Handoff\nRecord completed and remaining work, branch, worktree, HEAD, workspace status, uncommitted changes, blockers, verification, and one next action.\n\n## Protected actions\nCommit, push, Issue/PR, merge, tag, release/publication, and deletion require explicit user authorization naming action, target, scope, and expiry. Authorization never carries to another action; without a match prepare a preview only.\n",
    "README.md": "# {project_name}\n\nStart with [docs/INDEX.md](docs/INDEX.md).\n",
    "CONTRIBUTING.md": "# Contributing to {project_name}\n\nStart non-trivial work from a task or bug record. Keep code, tests, documentation, and verification linked.\n",
    "CHANGELOG.md": "# Changelog\n\n## Unreleased\n\n",
    ".gitignore": "# Project Governance Kit\n__pycache__/\n*.py[cod]\n.venv/\n.agent/\n",
    ".project-governance.toml": "kit_version = \"0.2.0\"\nschema_version = 2\nprofile = \"standard\"\ndocs_dir = \"docs\"\nrecords_dir = \"docs/work\"\n",
    "docs/INDEX.md": "# Project documentation index\n\nRead [STATUS](STATUS.md), then the relevant requirement, design, migration, task, review and verification records.\n",
    "docs/STATUS.md": "# Project status\n\n```yaml\nproject_stage: requirements_discussion\ncurrent_requirement: N/A\ncurrent_design: N/A\ncurrent_task: N/A\nowner: N/A\nblocker: none\nnext_action: discuss and record project requirements\nupdated: {date}\ngit_state: {git_state}\n```\n\nNo business requirements are created by initialization.\n",
    "docs/WORKFLOW.md": "<!-- PGK_GENERATED: workflow -->\n# Governance workflow\n\n```mermaid\nstateDiagram-v2\n[*] --> initialized\ninitialized --> requirements_discussion\nrequirements_discussion --> requirements_review\nrequirements_review --> active_development\nactive_development --> maintenance\nactive_development --> blocked\nmaintenance --> active_development\nblocked --> active_development: resolve blocker and resume\nblocked --> requirements_review: revise requirements\n```\n",
    "docs/templates/INDEX.md": "# Record templates\n\nTemplates: requirement, design, decision, task, bug, review, verification, migration.\n",
    "docs/requirements/INDEX.md": "<!-- PGK_GENERATED: requirement-index -->\n# Requirement index\n\nNo records yet.\n",
    "docs/design/INDEX.md": "<!-- PGK_GENERATED: design-index -->\n# Design index\n\nNo records yet.\n",
    "docs/decisions/INDEX.md": "<!-- PGK_GENERATED: decision-index -->\n# Decision index\n\nNo records yet.\n",
    "docs/work/BOARD.md": "<!-- PGK_GENERATED: board -->\n# Work board\n\n| ID | type | status | owner | related | branch/worktree | verification | blocker | next |\n|---|---|---|---|---|---|---|---|---|\n",
    "docs/work/tasks/INDEX.md": "<!-- PGK_GENERATED: task-index -->\n# Task index\n\nNo records yet.\n",
    "docs/work/bugs/INDEX.md": "<!-- PGK_GENERATED: bug-index -->\n# Bug index\n\nNo records yet.\n",
    "docs/reviews/INDEX.md": "<!-- PGK_GENERATED: review-index -->\n# Review index\n\nNo records yet.\n",
    "docs/verification/INDEX.md": "<!-- PGK_GENERATED: verification-index -->\n# Verification index\n\nNo records yet.\n",
    "docs/migrations/INDEX.md": "<!-- PGK_GENERATED: migration-index -->\n# Migration index\n\nNo records yet.\n",
    "docs/activity/ACTIVITY.md": "<!-- PGK_GENERATED: activity -->\n# Activity\n\n<!-- timestamp | actor | action | record_id | git_ref | result -->\n{date} | pgk | initialize | N/A | N/A | initialized -> requirements_discussion\n",
    "docs/operations/runbooks/INDEX.md": _EMPTY.format(title="Runbooks index"),
    "docs/operations/incidents/INDEX.md": _EMPTY.format(title="Incidents index"),
    "docs/operations/postmortems/INDEX.md": _EMPTY.format(title="Postmortems index"),
    "docs/work/INDEX.md": "<!-- PGK_GENERATED: work-index -->\n# Work index\n\nThe index is generated from task and bug records.\n\n## Active\n\nNo active records yet.\n\n## Bugs\n\nNo bug records yet.\n",
}
for _kind in ("requirement", "design", "decision", "task", "bug", "verification"):
    _template = f"# {_kind.title()} template\n\n## Purpose\n"
    if _kind in {"task", "bug", "verification"}:
        _template += "## Owner\nN/A\n"
    _template += "## Scope\nN/A\n"
    if _kind in {"task", "bug"}:
        _template += "## Files\nN/A\n"
    _template += "## Acceptance\n## Evidence\n## Changes\n## Blockers\n## Next action\n"
    if _kind in {"task", "bug"}:
        _template += "N/A\n\n## Git\nbranch: N/A\nworktree: N/A\nbase_commit: N/A\nhead_commit: N/A\n"
    STANDARD_FILES[f"docs/templates/{_kind}.md"] = _template
STANDARD_FILES["docs/templates/review.md"] = "# Review template\n\n## Purpose\n## Owner\n## Scope\n## Acceptance\n## Evidence\n## Changes\n## Blockers\n## Next action\n## Authorization\n## Base commit\n## Head commit\n## Findings\n## Verdict\n"
STANDARD_FILES["docs/templates/migration.md"] = "# Migration template\n\n## Purpose\n## Owner\nN/A\n## Scope\nN/A\n## Scan\nN/A\n## Items\nN/A\n## Approval\npending\n## Acceptance\n## Evidence\n## Changes\n## Blockers\n## Next action\nN/A\n\n## Git\nbranch: N/A\nworktree: N/A\nbase_commit: N/A\nhead_commit: N/A\n\n## Handoff\n\n<!-- PGK_HANDOFF_START -->\n<!-- PGK_HANDOFF_END -->\n"
STANDARD_DIRECTORIES = tuple(sorted({str(Path(p).parent).replace("\\", "/") for p in STANDARD_FILES}))

@dataclass(frozen=True, slots=True)
class ScaffoldResult:
    created: tuple[str, ...]
    skipped: tuple[str, ...]
    git_state: str
    project_stage: str
    errors: dict[str, str] = field(default_factory=dict)
    def as_dict(self) -> dict[str, object]:
        return {"created": list(self.created), "skipped": list(self.skipped), "git_state": self.git_state, "project_stage": self.project_stage, "errors": dict(self.errors or {})}

@dataclass(frozen=True, slots=True)
class AdoptionReport:
    existing: tuple[str, ...]
    missing: tuple[str, ...]
    mappings: tuple[dict[str, str], ...]
    candidates: tuple[dict[str, object], ...] = ()
    scan_roots: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    git: dict[str, object] = field(default_factory=dict)
    def as_dict(self) -> dict[str, object]:
        return {
            "existing": list(self.existing),
            "missing": list(self.missing),
            "mappings": [dict(item) for item in self.mappings],
            "candidates": [dict(item) for item in self.candidates],
            "scan_roots": list(self.scan_roots),
            "exclude_patterns": list(self.exclude_patterns),
            "git": dict(self.git),
        }

def init_project(root: str | Path, *, project_name: str | None = None, profile: str = "standard", mode: str = "new", dry_run: bool = False) -> ScaffoldResult:
    if profile != "standard": raise ValueError(f"unsupported profile: {profile}")
    if mode not in {"new", "supplement"}: raise ValueError(f"unsupported initialization mode: {mode}")
    root = Path(root)
    if not root.exists() or not root.is_dir(): raise ValueError(f"project root does not exist: {root}")
    name = (project_name or root.name).strip() or root.name
    try: inspect_git(root); git_state = "git_initialized"
    except ValueError: git_state = "git_not_initialized"
    for relative in STANDARD_FILES:
        path = root / relative
        if path.exists() and path.is_dir():
            raise ValueError(f"required path is a directory: {relative}")
    created, skipped, errors = [], [], {}
    if not dry_run:
        for directory in STANDARD_DIRECTORIES:
            try:
                (root / directory).mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                errors[directory] = str(exc)
    project_stage = "adoption_review" if mode == "supplement" else "requirements_discussion"
    for relative, template in STANDARD_FILES.items():
        path = root / relative
        if path.exists():
            skipped.append(relative); continue
        if not dry_run:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                rendered = template.format(project_name=name, date=date.today().isoformat(), git_state=git_state)
                if relative == "docs/STATUS.md" and mode == "supplement":
                    rendered = rendered.replace("project_stage: requirements_discussion", "project_stage: adoption_review", 1)
                path.write_text(rendered, encoding="utf-8")
            except OSError as exc:
                errors[relative] = str(exc)
                continue
        created.append(relative)
    if mode == "supplement" and (root / "docs/STATUS.md").exists() and "docs/STATUS.md" in skipped:
        existing_status = (root / "docs/STATUS.md").read_text(encoding="utf-8")
        if "project_stage:" in existing_status:
            match = __import__("re").search(r"(?im)^\s*project_stage\s*:\s*([^\s]+)", existing_status)
            project_stage = match.group(1) if match else "adoption_review"
    return ScaffoldResult(tuple(created), tuple(skipped), git_state, project_stage, errors)

_MAPPINGS = {"docs/coding/PRD.md": "requirements_index", "docs/coding/TSD.md": "design_index", "docs/coding/DESIGN.md": "ui_design_index", "docs/coding/API.md": "api_contract_index"}
def adopt_project(root: str | Path) -> AdoptionReport:
    root = Path(root)
    if not root.exists() or not root.is_dir(): raise ValueError(f"project root does not exist: {root}")
    existing = tuple(relative for relative in STANDARD_FILES if (root / relative).exists())
    missing = tuple(relative for relative in STANDARD_FILES if not (root / relative).exists())
    mappings = tuple({"path": path, "role": role} for path, role in _MAPPINGS.items() if (root / path).exists())
    from .migration import DEFAULT_EXCLUDE_PATTERNS, DEFAULT_SCAN_ROOTS, scan_project
    candidates = tuple(item.as_dict() for item in scan_project(root))
    try:
        git_context = inspect_git(root)
        git = {
            "available": True,
            "branch": git_context.branch,
            "head": git_context.head,
            "dirty": git_context.dirty,
            "recent_commits": list(git_context.recent_commits),
            "worktrees": [dict(item) for item in git_context.worktrees],
        }
    except ValueError:
        git = {
            "available": False,
            "branch": "unavailable",
            "head": "unavailable",
            "dirty": False,
            "recent_commits": [],
            "worktrees": [],
        }
    return AdoptionReport(existing, missing, mappings, candidates, DEFAULT_SCAN_ROOTS, DEFAULT_EXCLUDE_PATTERNS, git)
