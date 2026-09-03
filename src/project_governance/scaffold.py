"""Safe initialization and read-only adoption inspection."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


STANDARD_FILES: dict[str, str] = {
    "AGENTS.md": """# Agent instructions for {project_name}\n\nRead `docs/INDEX.md` and `docs/STATUS.md` before changing this project. Keep\nrequirements, design, tasks, verification evidence, and Git references linked.\nDo not commit secrets or overwrite project-owned documents during adoption.\n""",
    "CONTRIBUTING.md": """# Contributing to {project_name}\n\nStart non-trivial work from a task or bug record under `docs/work/`. Keep code,\ntests, and required documentation in the same change chain. Run the project\nchecks and tests before review.\n""",
    "CHANGELOG.md": """# Changelog\n\n## Unreleased\n\n""",
    ".project-governance.toml": """kit_version = \"0.1.0\"\nschema_version = 1\nprofile = \"standard\"\ndocs_dir = \"docs\"\nrecords_dir = \"docs/work\"\ntask_record = \"repository_markdown\"\nhandoff_mode = \"task_section\"\n""",
    "docs/INDEX.md": """# Project documentation index\n\nStart with [project status](STATUS.md), then read the relevant requirement,\ndesign, task, and verification record. This index is navigation, not a copy\nof document bodies.\n""",
    "docs/STATUS.md": """# Project status\n\n```yaml\nstatus: bootstrap_in_progress\nactive_task: none\nupdated: {date}\n```\n\nRecord the current active work and next action here or in the linked task\nrecord. Do not treat this snapshot as a replacement for task history.\n""",
    "docs/project-structure.md": """# Project structure\n\nDescribe the project's modules, data flow, runtime boundaries, and ownership\nhere. Keep implementation detail in the relevant design records.\n""",
    "docs/project-conventions.md": """# Project conventions\n\nRecord stable coding, testing, security, dependency, data, and delivery\nconventions here. Keep project-specific rules in `AGENTS.md`.\n""",
    "docs/work/INDEX.md": """<!-- PGK_GENERATED: work-index -->\n# Work index\n\nThe index is generated from task and bug records.\n\n## Active\n\nNo active records yet.\n\n## Bugs\n\nNo bug records yet.\n""",
    "docs/verification/INDEX.md": """# Verification index\n\nLink evidence-backed verification records here.\n""",
}

STANDARD_DIRECTORIES = (
    "docs/requirements",
    "docs/design",
    "docs/decisions",
    "docs/plans",
    "docs/work/tasks",
    "docs/work/bugs",
    "docs/verification",
    "docs/operations/runbooks",
    "docs/operations/incidents",
    "docs/operations/postmortems",
)


@dataclass(frozen=True, slots=True)
class ScaffoldResult:
    created: tuple[str, ...]
    skipped: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {"created": list(self.created), "skipped": list(self.skipped)}


@dataclass(frozen=True, slots=True)
class AdoptionReport:
    existing: tuple[str, ...]
    missing: tuple[str, ...]
    mappings: tuple[dict[str, str], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "existing": list(self.existing),
            "missing": list(self.missing),
            "mappings": [dict(item) for item in self.mappings],
        }


def init_project(
    root: str | Path,
    *,
    project_name: str | None = None,
    profile: str = "standard",
    dry_run: bool = False,
) -> ScaffoldResult:
    """Create missing standard-profile files without overwriting existing files."""

    if profile != "standard":
        raise ValueError(f"unsupported profile: {profile}")
    root = Path(root)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    name = (project_name or root.name).strip() or root.name
    created: list[str] = []
    skipped: list[str] = []
    for directory in STANDARD_DIRECTORIES:
        if not dry_run:
            (root / directory).mkdir(parents=True, exist_ok=True)
    for relative, template in STANDARD_FILES.items():
        path = root / relative
        if path.exists():
            skipped.append(relative)
            continue
        created.append(relative)
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                template.format(project_name=name, date=date.today().isoformat()),
                encoding="utf-8",
            )
    return ScaffoldResult(tuple(created), tuple(skipped))


_MAPPINGS = {
    "docs/coding/PRD.md": "requirements_index",
    "docs/coding/TSD.md": "design_index",
    "docs/coding/DESIGN.md": "ui_design_index",
    "docs/coding/API.md": "api_contract_index",
}


def adopt_project(root: str | Path) -> AdoptionReport:
    """Inspect a project and suggest mappings without writing any files."""

    root = Path(root)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    existing = tuple(relative for relative in STANDARD_FILES if (root / relative).exists())
    missing = tuple(relative for relative in STANDARD_FILES if not (root / relative).exists())
    mappings = tuple(
        {"path": path, "role": role}
        for path, role in _MAPPINGS.items()
        if (root / path).exists()
    )
    return AdoptionReport(existing, missing, mappings)
