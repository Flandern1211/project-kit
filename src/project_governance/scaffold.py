"""Safe initialization and read-only adoption inspection."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from .config import default_visibility_dirs, validate_collaboration_mode, validate_profile, validate_visibility, validate_visibility_dirs
from .git_context import inspect_git

_EMPTY = "# {title}\n\nNo records yet.\n"
_AGENTS_TEMPLATE = """# Agent instructions for {project_name}

Governance profile: {profile}
Collaboration mode: {collaboration_mode}

## Read before acting
Read `AGENTS.md`, `docs/INDEX.md`, `docs/project-structure.md`, and `docs/STATUS.md` before changing files. Then read the linked requirement, design or decision, task or bug, review, and verification records that govern the change.

## Architecture limits
Supported lifecycle RecordTypes are `requirement`, `design`, `decision`, `task`, `bug`, `review`, `verification`, and `migration`.
Strict risk/security/release/runbook/incident/postmortem paths contain ordinary control Markdown, not new RecordTypes. Do not add lifecycle frontmatter types for them.
Do not create new governance directories, records, statuses, or business modules unless an accepted design and task authorize them. Unknown business directories require an accepted design and task before use.

## Repository map
- `docs/requirements/`: product intent and acceptance criteria; keep requirements authoritative and confirmed through the requirements gate.
- `docs/design/`: accepted architecture and implementation design; do not substitute plans or code for design decisions.
- `docs/decisions/`: durable decisions and alternatives; record changes instead of silently rewriting history.
- `docs/work/tasks/`: scoped implementation tasks; every non-trivial change needs an owner, files, and evidence.
- `docs/work/bugs/`: reproducible defects and their fix scope; do not use bugs as new requirements.
- `docs/reviews/`: review findings and verdicts; review records do not silently modify implementation branches.
- `docs/verification/`: evidence-backed validation; do not claim verified without commands or inspection evidence.
- `docs/migrations/`: migration plans and outcomes; source documents stay at their original paths.
- `docs/activity/`: concise activity timeline; coordination history is not a replacement for source-of-truth records.
- `docs/operations/runbooks/`, `docs/operations/incidents/`, `docs/operations/postmortems/`: operational control Markdown; keep them ordinary Markdown without lifecycle frontmatter types.
- `docs/risk/`, `docs/security/`, `docs/releases/`: Strict control Markdown for risk, security, and release evidence; keep them ordinary Markdown without lifecycle frontmatter types.
- `docs/templates/`: record templates only; copy and complete the supported lifecycle template rather than creating a new type.
- `docs/INDEX.md`, `docs/project-structure.md`, `docs/WORKFLOW.md`, `docs/project-conventions.md`, and `docs/STATUS.md`: navigation, structure, workflow, conventions, and current state; do not duplicate record bodies.
- `docs/work/INDEX.md` and `docs/work/BOARD.md`: generated task/bug navigation and board; update source records, then regenerate indexes.

## State gates
Requirements are drafts until user confirmation. Before implementation require an accepted requirement, applicable design/ADR, and TASK/BUG with owner and scope. Complete records and code, run semantic checks, fill evidence, commit once, run read-only clean-tree checks, and do not edit the repository after the clean-tree check. Put post-commit output in the external experiment report or handoff.

## Handoff
Record completed and remaining work, branch, HEAD, workspace status, uncommitted changes, blockers, verification, and one next action.

## Protected actions
Commit, push, Issue/PR, merge, tag, release/publication, and deletion require explicit user authorization naming action, target, scope, and expiry. Authorization never carries to another action; without a match prepare a preview only.
"""
_PROJECT_STRUCTURE_TEMPLATE = """<!-- PGK_GENERATED: project-structure -->
# Project structure

This map distinguishes Kit-owned governance documents from project business
content. The generated folders are safe defaults; a new governance directory,
record, status, or business module requires an accepted design and task.

## Root files

| Path | Purpose | Boundary |
|---|---|---|
| `AGENTS.md` | Agent contract and architecture limits | Read before acting; do not weaken its gates silently. |
| `README.md` | Project entry point | Link to documentation; do not duplicate governance records. |
| `CONTRIBUTING.md` | Contribution guidance | Keep implementation work linked to a task or bug. |
| `CHANGELOG.md` | Release-facing change summary | Do not use it as a release record or verification record. |
| `.project-governance.toml` | Kit profile and path configuration | Change only through an accepted governance change. |
| `.gitignore` | Local/generated exclusions | Never use it to hide required evidence. |

## Governance documents

| Path | Purpose | Boundary |
|---|---|---|
| `docs/INDEX.md` | Navigation to current governance documents | Links only; it does not replace record bodies. |
| `docs/STATUS.md` | Current project stage, ownership, blocker, and next action | Keep it synchronized with accepted records and evidence. |
| `docs/WORKFLOW.md` | Lifecycle states and finalization sequence | Describes process; it is not a task record. |
| `docs/project-structure.md` | Detailed Kit-owned directory map | Update with an accepted design when the Kit structure changes. |
| `docs/project-conventions.md` | Record, Git, verification, and security conventions | Do not invent lifecycle types or statuses here. |
| `docs/requirements/` | Product intent and acceptance criteria | Use `requirement` records; acceptance is a user decision. |
| `docs/design/` | Architecture and implementation design | Use `design` records; implementation does not imply acceptance. |
| `docs/decisions/` | Durable decisions, alternatives, and consequences | Use `decision` records; preserve superseded history. |
| `docs/work/tasks/` | Planned and active implementation tasks | Use `task` records with owner, scope, files, and evidence. |
| `docs/work/bugs/` | Reproducible defects and fix scope | Use `bug` records; do not turn a bug into a new schema type. |
| `docs/work/INDEX.md` | Generated task and bug navigation | Regenerate from source records instead of editing bodies here. |
| `docs/work/BOARD.md` | Generated work status board | Keep it a view of task and bug records. |
| `docs/reviews/` | Review findings and verdicts | Use `review` records; reviewers do not silently modify branches. |
| `docs/verification/` | Validation and acceptance evidence | Use `verification` records; claims need command or inspection evidence. |
| `docs/migrations/` | Migration plans and per-run outcomes | Use `migration` records; never move or overwrite source files. |
| `docs/activity/` | Concise project activity timeline | Coordination material does not replace authoritative records. |
| `docs/templates/` | Templates for supported lifecycle records | Templates are not records and do not authorize new types. |

## Strict control documents

Strict `risk`, `security`, `release`, `runbook`, `incident`, and `postmortem`
documents are ordinary Markdown under their respective directories. They do
not use lifecycle frontmatter and do not add RecordTypes. Their paths are:

- `docs/risk/`: risk register and risk-control evidence.
- `docs/security/`: security controls, findings, and review evidence.
- `docs/releases/`: release notes and release evidence.
- `docs/operations/runbooks/`: repeatable operational procedures.
- `docs/operations/incidents/`: incident records and response timelines.
- `docs/operations/postmortems/`: learning and follow-up after incidents.

## Optional coordination paths

`docs/plans/`, `docs/superpowers/plans/`, and `docs/superpowers/specs/` may hold
plans or proposals. They coordinate work but do not become accepted
requirements, designs, tasks, or verification records until copied into the
supported source-of-truth locations. `.agent/` contains local session and
handoff projections when used; it is not a governance record and is ignored by
default.

## Source of truth versus coordination

Requirements, designs, decisions, tasks, bugs, reviews, verification records,
and migrations are the supported lifecycle source of truth. Indexes, boards,
activity, plans, specs, handoffs, and chat are coordination material and must
point back to authoritative records. Unknown business directories are not
pre-approved; an accepted design and task must authorize them first.
"""
_WORKFLOW_TEMPLATE = """<!-- PGK_GENERATED: workflow -->
# Governance workflow

```mermaid
stateDiagram-v2
[*] --> initialized
initialized --> requirements_discussion
requirements_discussion --> requirements_review
requirements_review --> active_development
active_development --> maintenance
active_development --> blocked
maintenance --> active_development
blocked --> active_development: resolve blocker and resume
blocked --> requirements_review: revise requirements
```

## Two-phase finalization

1. Complete all records, source files, tests, and documentation.
2. Run semantic checks while changes are uncommitted.
3. Fill final evidence and terminal statuses.
4. Commit the complete task branch once.
5. Run read-only clean-tree `pgk check` and `pgk doctor`.
6. Do not edit the repository after the clean-tree check. Store post-commit
   output in the external experiment report or handoff.
"""
_CONVENTIONS_TEMPLATE = """<!-- PGK_GENERATED: project-conventions -->
# Project conventions

## Records

The supported lifecycle RecordTypes are `requirement`, `design`, `decision`,
`task`, `bug`, `review`, `verification`, and `migration`. Records use YAML
frontmatter with `id`, `type`, `status`, `created`, and `updated`.

The lifecycle statuses are `draft`, `accepted`, `in_progress`, `blocked`,
`verified`, `done`, and `rejected`. A record may move to `verified` only when
its verification section names the evidence used.

Strict risk, security, release, runbook, incident, and postmortem documents are
ordinary Markdown. Do not add lifecycle frontmatter or invent a RecordType for
them. Unknown governance directories, records, statuses, and business modules
require an accepted design and task.

Indexes link to records but do not duplicate their bodies. Meaningful updates
append a short timeline entry to the existing record. Do not create a separate
implementation log for every progress message.

## Git

`main` is an integration branch. A non-trivial task uses one short-lived
branch and one worktree when parallel work is active. A reviewer does not
silently modify the implementer's branch.

## Verification

Verification must name the command or inspection evidence used. A passing test
suite does not by itself prove external services, deployment, performance, or
long-running behavior.

## Two-phase finalization

Complete records and code, run semantic checks, fill evidence, commit once, run
read-only clean-tree checks, and do not edit the repository after the clean-tree
check. Post-commit output belongs in the external experiment report or handoff.

## Security

Secrets, private data, complete model payloads, and unredacted runtime logs do
not belong in repository documents. The core toolkit performs local checks and
does not call external services.
"""
STANDARD_FILES: dict[str, str] = {
    "AGENTS.md": _AGENTS_TEMPLATE,
    "README.md": "# {project_name}\n\nStart with [docs/INDEX.md](docs/INDEX.md).\n",
    "CONTRIBUTING.md": "# Contributing to {project_name}\n\nStart non-trivial work from a task or bug record. Keep code, tests, documentation, and verification linked.\n",
    "CHANGELOG.md": "# Changelog\n\n## Unreleased\n\n",
    ".gitignore": "# Project Governance Kit\n__pycache__/\n*.py[cod]\n.venv/\n.agent/\n",
    ".project-governance.toml": "kit_version = \"0.1.0\"\nschema_version = 1\nprofile = \"{profile}\"\ncollaboration_mode = \"{collaboration_mode}\"\nvisibility = \"{visibility}\"\ngovernance_dir = \"{governance_dir}\"\npublic_docs_dir = \"{public_docs_dir}\"\ndocs_dir = \"docs\"\nrecords_dir = \"docs/work\"\n",
    "docs/INDEX.md": "# Project documentation index\n\nRead [STATUS](STATUS.md), then [Project structure](project-structure.md) and [Project conventions](project-conventions.md). Next read the relevant requirement, design, task, review, verification, and migration records.\n",
    "docs/STATUS.md": "# Project status\n\n```yaml\nproject_stage: requirements_discussion\nprofile: {profile}\ncollaboration_mode: {collaboration_mode}\ncurrent_requirement: N/A\ncurrent_design: N/A\ncurrent_task: N/A\nowner: N/A\nblocker: none\nnext_action: discuss and record project requirements\nupdated: {date}\ngit_state: {git_state}\n```\n\nNo business requirements are created by initialization.\n",
    "docs/WORKFLOW.md": _WORKFLOW_TEMPLATE,
    "docs/project-structure.md": _PROJECT_STRUCTURE_TEMPLATE,
    "docs/project-conventions.md": _CONVENTIONS_TEMPLATE,
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

LITE_KEYS = {
    "AGENTS.md", "README.md", "CONTRIBUTING.md", "CHANGELOG.md", ".gitignore",
    ".project-governance.toml", "docs/INDEX.md", "docs/STATUS.md", "docs/WORKFLOW.md",
    "docs/templates/INDEX.md", "docs/templates/requirement.md", "docs/templates/task.md",
    "docs/templates/bug.md", "docs/templates/verification.md", "docs/requirements/INDEX.md",
    "docs/work/BOARD.md", "docs/work/tasks/INDEX.md", "docs/work/bugs/INDEX.md",
    "docs/verification/INDEX.md", "docs/activity/ACTIVITY.md",
}
STRICT_FILES: dict[str, str] = {
    "docs/risk/INDEX.md": _EMPTY.format(title="Risk index"),
    "docs/security/INDEX.md": _EMPTY.format(title="Security index"),
    "docs/releases/INDEX.md": _EMPTY.format(title="Releases index"),
}


def files_for_profile(profile: str) -> dict[str, str]:
    profile = validate_profile(profile)
    if profile == "lite":
        return {key: STANDARD_FILES[key] for key in STANDARD_FILES if key in LITE_KEYS}
    files = dict(STANDARD_FILES)
    if profile == "strict":
        files.update(STRICT_FILES)
    return files


def files_for_visibility(
    profile: str,
    visibility: str,
    governance_dir: str | None = None,
    public_docs_dir: str | None = None,
) -> dict[str, str]:
    visibility = validate_visibility(visibility)
    default_governance, default_public = default_visibility_dirs(visibility)
    governance_dir, public_docs_dir = validate_visibility_dirs(visibility, governance_dir or default_governance, public_docs_dir or default_public)
    source = files_for_profile(profile)
    if visibility == "public":
        return source
    result: dict[str, str] = {}
    for relative, template in source.items():
        mapped = f"{governance_dir}/{relative[5:]}" if relative.startswith("docs/") else relative
        rendered = template.replace("docs/", f"{governance_dir}/")
        result[mapped] = rendered
    if visibility == "hybrid":
        result[f"{public_docs_dir}/INDEX.md"] = "# Public documentation index\n\nPublic project documentation belongs here. Internal governance records are stored separately.\n"
    return result


def required_artifacts_for_profile(profile: str) -> tuple[str, ...]:
    files = files_for_profile(profile)
    baseline = {"docs/templates/INDEX.md", "docs/templates/requirement.md", "docs/templates/design.md",
                "docs/templates/decision.md", "docs/templates/task.md", "docs/templates/bug.md",
                "docs/templates/review.md", "docs/templates/verification.md", "docs/operations/runbooks/INDEX.md",
                "docs/templates/migration.md", "docs/migrations/INDEX.md", "docs/operations/incidents/INDEX.md", "docs/operations/postmortems/INDEX.md"}
    return tuple(sorted(path for path in files if path in baseline or path.startswith("docs/risk/") or path.startswith("docs/security/") or path.startswith("docs/releases/")))

@dataclass(frozen=True, slots=True)
class ScaffoldResult:
    created: tuple[str, ...]
    skipped: tuple[str, ...]
    git_state: str
    project_stage: str
    errors: dict[str, str] = field(default_factory=dict)
    profile: str = "standard"
    collaboration_mode: str = "single-agent"
    visibility: str = "public"
    governance_dir: str = "docs"
    public_docs_dir: str = "docs"
    def as_dict(self) -> dict[str, object]:
        return {"created": list(self.created), "skipped": list(self.skipped), "git_state": self.git_state, "project_stage": self.project_stage, "profile": self.profile, "collaboration_mode": self.collaboration_mode, "visibility": self.visibility, "governance_dir": self.governance_dir, "public_docs_dir": self.public_docs_dir, "errors": dict(self.errors or {})}

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
        return {"existing": list(self.existing), "missing": list(self.missing), "mappings": [dict(item) for item in self.mappings], "candidates": [dict(item) for item in self.candidates], "scan_roots": list(self.scan_roots), "exclude_patterns": list(self.exclude_patterns), "git": dict(self.git)}

def init_project(root: str | Path, *, project_name: str | None = None, profile: str = "standard", mode: str = "new", collaboration_mode: str = "single-agent", visibility: str = "public", governance_dir: str | None = None, public_docs_dir: str | None = None, dry_run: bool = False) -> ScaffoldResult:
    if mode not in {"new", "supplement"}:
        raise ValueError(f"unsupported initialization mode: {mode}")
    profile = validate_profile(profile)
    collaboration_mode = validate_collaboration_mode(collaboration_mode, v01=True)
    visibility = validate_visibility(visibility)
    default_governance, default_public = default_visibility_dirs(visibility)
    governance_dir, public_docs_dir = validate_visibility_dirs(visibility, governance_dir or default_governance, public_docs_dir or default_public)
    root = Path(root)
    if not root.exists() or not root.is_dir(): raise ValueError(f"project root does not exist: {root}")
    name = (project_name or root.name).strip() or root.name
    try: inspect_git(root); git_state = "git_initialized"
    except ValueError: git_state = "git_not_initialized"
    files = files_for_visibility(profile, visibility, governance_dir, public_docs_dir)
    for relative in files:
        path = root / relative
        if path.exists() and path.is_dir():
            raise ValueError(f"required path is a directory: {relative}")
    created, skipped, errors = [], [], {}
    if not dry_run:
        directories = tuple(sorted({str(Path(p).parent).replace("\\", "/") for p in files}))
        for directory in directories:
            try:
                (root / directory).mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                errors[directory] = str(exc)
    for relative, template in files.items():
        path = root / relative
        if path.exists():
            skipped.append(relative); continue
        if not dry_run:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                rendered = template
                if relative == ".gitignore" and visibility == "hybrid":
                    rendered += f"\n{governance_dir.rstrip('/')}/\n"
                if relative == "README.md" and visibility != "public":
                    landing = f"{public_docs_dir}/INDEX.md" if visibility == "hybrid" else f"{governance_dir}/INDEX.md"
                    rendered = f"# {name}\n\nStart with [{landing}]({landing}).\n"
                if visibility != "public" and relative not in {"README.md", ".gitignore", ".project-governance.toml"}:
                    rendered = rendered.replace("docs/", f"{governance_dir}/")
                rendered = rendered.format(project_name=name, date=date.today().isoformat(), git_state=git_state, profile=profile, collaboration_mode=collaboration_mode, visibility=visibility, governance_dir=governance_dir, public_docs_dir=public_docs_dir)
                if mode == "supplement" and relative.endswith("STATUS.md"):
                    rendered = rendered.replace("project_stage: requirements_discussion", "project_stage: adoption_review", 1)
                path.write_text(rendered, encoding="utf-8")
            except OSError as exc:
                errors[relative] = str(exc)
                continue
        created.append(relative)
    project_stage = "adoption_review" if mode == "supplement" else "requirements_discussion"
    status_path = root / governance_dir / "STATUS.md"
    if mode == "supplement" and status_path in [root / item for item in skipped]:
        existing = status_path.read_text(encoding="utf-8") if status_path.exists() else ""
        match = __import__("re").search(r"(?im)^\s*project_stage\s*:\s*([^\s]+)", existing)
        project_stage = match.group(1) if match else project_stage
    return ScaffoldResult(tuple(created), tuple(skipped), git_state, project_stage, errors, profile, collaboration_mode, visibility, governance_dir, public_docs_dir)

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
        git = {"available": True, "branch": git_context.branch, "head": git_context.head, "dirty": git_context.dirty, "recent_commits": list(git_context.recent_commits), "worktrees": [dict(item) for item in git_context.worktrees]}
    except ValueError:
        git = {"available": False, "branch": "unavailable", "head": "unavailable", "dirty": False, "recent_commits": [], "worktrees": []}
    return AdoptionReport(existing, missing, mappings, candidates, DEFAULT_SCAN_ROOTS, DEFAULT_EXCLUDE_PATTERNS, git)
