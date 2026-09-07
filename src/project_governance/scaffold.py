"""Safe initialization and read-only adoption inspection."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from .config import default_visibility_dirs, validate_collaboration_mode, validate_profile, validate_visibility, validate_visibility_dirs
from .git_context import inspect_git

_EMPTY = "# {title}\n\nNo records yet.\n"
STANDARD_FILES: dict[str, str] = {
    "AGENTS.md": "# Agent instructions for {project_name}\n\nGovernance profile: {profile}\nCollaboration mode: {collaboration_mode}\n\n## Read before acting\nRead `AGENTS.md`, `docs/INDEX.md`, `docs/STATUS.md`, linked requirement/design/task/bug/review/verification records, then the current Git branch, HEAD and status.\n\n## State gates\nRequirements are drafts until user confirmation. Before implementation require an accepted requirement, applicable design/ADR, and TASK/BUG with owner and scope. Stop and record blockers for missing or conflicting records. v0.1 supports single-Agent work and sequential handoffs; parallel coordination is deferred.\n\n## Handoff\nRecord completed and remaining work, branch, HEAD, workspace status, uncommitted changes, blockers, verification, and one next action.\n\n## Protected actions\nCommit, push, Issue/PR, merge, tag, release/publication, and deletion require explicit user authorization naming action, target, scope, and expiry. Authorization never carries to another action; without a match prepare a preview only.\n",
    "README.md": "# {project_name}\n\nStart with [docs/INDEX.md](docs/INDEX.md).\n",
    "CONTRIBUTING.md": "# Contributing to {project_name}\n\nStart non-trivial work from a task or bug record. Keep code, tests, documentation, and verification linked.\n",
    "CHANGELOG.md": "# Changelog\n\n## Unreleased\n\n",
    ".gitignore": "# Project Governance Kit\n__pycache__/\n*.py[cod]\n.venv/\n.agent/\n",
    ".project-governance.toml": "kit_version = \"0.1.0\"\nschema_version = 1\nprofile = \"{profile}\"\ncollaboration_mode = \"{collaboration_mode}\"\nvisibility = \"{visibility}\"\ngovernance_dir = \"{governance_dir}\"\npublic_docs_dir = \"{public_docs_dir}\"\ndocs_dir = \"docs\"\nrecords_dir = \"docs/work\"\n",
    "docs/INDEX.md": "# Project documentation index\n\nRead [STATUS](STATUS.md), then the relevant requirement, design, task, review and verification records.\n",
    "docs/STATUS.md": "# Project status\n\n```yaml\nproject_stage: requirements_discussion\nprofile: {profile}\ncollaboration_mode: {collaboration_mode}\ncurrent_requirement: N/A\ncurrent_design: N/A\ncurrent_task: N/A\nowner: N/A\nblocker: none\nnext_action: discuss and record project requirements\nupdated: {date}\ngit_state: {git_state}\n```\n\nNo business requirements are created by initialization.\n",
    "docs/WORKFLOW.md": "<!-- PGK_GENERATED: workflow -->\n# Governance workflow\n\n```mermaid\nstateDiagram-v2\n[*] --> initialized\ninitialized --> requirements_discussion\nrequirements_discussion --> requirements_review\nrequirements_review --> active_development\nactive_development --> maintenance\nactive_development --> blocked\nmaintenance --> active_development\nblocked --> active_development: resolve blocker and resume\nblocked --> requirements_review: revise requirements\n```\n",
    "docs/templates/INDEX.md": "# Record templates\n\nTemplates: requirement, design, decision, task, bug, review, verification.\n",
    "docs/requirements/INDEX.md": "<!-- PGK_GENERATED: requirement-index -->\n# Requirement index\n\nNo records yet.\n",
    "docs/design/INDEX.md": "<!-- PGK_GENERATED: design-index -->\n# Design index\n\nNo records yet.\n",
    "docs/decisions/INDEX.md": "<!-- PGK_GENERATED: decision-index -->\n# Decision index\n\nNo records yet.\n",
    "docs/work/BOARD.md": "<!-- PGK_GENERATED: board -->\n# Work board\n\n| ID | type | status | owner | related | branch/worktree | verification | blocker | next |\n|---|---|---|---|---|---|---|---|---|\n",
    "docs/work/tasks/INDEX.md": "<!-- PGK_GENERATED: task-index -->\n# Task index\n\nNo records yet.\n",
    "docs/work/bugs/INDEX.md": "<!-- PGK_GENERATED: bug-index -->\n# Bug index\n\nNo records yet.\n",
    "docs/reviews/INDEX.md": "<!-- PGK_GENERATED: review-index -->\n# Review index\n\nNo records yet.\n",
    "docs/verification/INDEX.md": "<!-- PGK_GENERATED: verification-index -->\n# Verification index\n\nNo records yet.\n",
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
                "docs/operations/incidents/INDEX.md", "docs/operations/postmortems/INDEX.md"}
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
    def as_dict(self) -> dict[str, object]:
        return {"existing": list(self.existing), "missing": list(self.missing), "mappings": [dict(item) for item in self.mappings]}

def init_project(root: str | Path, *, project_name: str | None = None, profile: str = "standard", collaboration_mode: str = "single-agent", visibility: str = "public", governance_dir: str | None = None, public_docs_dir: str | None = None, dry_run: bool = False) -> ScaffoldResult:
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
                path.write_text(rendered.format(project_name=name, date=date.today().isoformat(), git_state=git_state, profile=profile, collaboration_mode=collaboration_mode, visibility=visibility, governance_dir=governance_dir, public_docs_dir=public_docs_dir), encoding="utf-8")
            except OSError as exc:
                errors[relative] = str(exc)
                continue
        created.append(relative)
    return ScaffoldResult(tuple(created), tuple(skipped), git_state, "requirements_discussion", errors, profile, collaboration_mode, visibility, governance_dir, public_docs_dir)

_MAPPINGS = {"docs/coding/PRD.md": "requirements_index", "docs/coding/TSD.md": "design_index", "docs/coding/DESIGN.md": "ui_design_index", "docs/coding/API.md": "api_contract_index"}
def adopt_project(root: str | Path) -> AdoptionReport:
    root = Path(root)
    if not root.exists() or not root.is_dir(): raise ValueError(f"project root does not exist: {root}")
    existing = tuple(relative for relative in STANDARD_FILES if (root / relative).exists())
    missing = tuple(relative for relative in STANDARD_FILES if not (root / relative).exists())
    mappings = tuple({"path": path, "role": role} for path, role in _MAPPINGS.items() if (root / path).exists())
    return AdoptionReport(existing, missing, mappings)
