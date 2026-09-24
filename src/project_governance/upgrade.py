"""Conflict-safe upgrades for projects already governed by PGK.

The upgrade path is deliberately small and local.  It plans the Kit-owned
contract changes, refuses ambiguous merges, and writes the complete plan with
atomic replacements only after every conflict has been inspected.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import difflib
import hashlib
import os
from pathlib import Path
import re
import tempfile

from .config import load_config
from .records import expected_generated_views
from .scaffold import files_for_visibility
from .version import __version__


SUPPORTED_SOURCE_VERSIONS = frozenset({"0.2.0.dev0", __version__})
_KIT_MANAGED_HEADINGS = (
    "Read before acting",
    "Architecture limits",
    "Repository map",
    "State gates",
    "Task execution and closure",
    "Handoff",
    "Protected actions",
)
_HEADING_RE = re.compile(r"(?im)^##\s+([^\n]+?)\s*$")
_VERSION_RE = re.compile(r"(?m)^\s*kit_version\s*=\s*([\"'])([^\"']+)\1\s*$")


class UpgradeError(ValueError):
    """Base error for an upgrade that cannot be planned or applied."""


class UnsupportedUpgradeError(UpgradeError):
    """The configured Kit version has no known migration path."""


@dataclass(frozen=True, slots=True)
class UpgradeResult:
    from_version: str
    to_version: str
    changes: tuple[dict[str, object], ...]
    unchanged: tuple[str, ...]
    conflicts: tuple[dict[str, str], ...]
    dry_run: bool
    applied: bool

    @property
    def ok(self) -> bool:
        return not self.conflicts

    @property
    def changed(self) -> tuple[str, ...]:
        return tuple(str(item["path"]) for item in self.changes)

    def as_dict(self) -> dict[str, object]:
        return {
            "from_version": self.from_version,
            "to_version": self.to_version,
            "changed": list(self.changed),
            "changes": [dict(item) for item in self.changes],
            "unchanged": list(self.unchanged),
            "conflicts": [dict(item) for item in self.conflicts],
            "dry_run": self.dry_run,
            "applied": self.applied,
            "ok": self.ok,
        }


def _normal(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _preserve_newlines(path: Path, text: str) -> str:
    """Keep a file's existing newline convention during an upgrade."""

    try:
        raw = path.read_bytes()
    except OSError:
        return text
    if b"\r\n" in raw and raw.count(b"\r\n") == raw.count(b"\n"):
        return _normal(text).replace("\n", "\r\n")
    return _normal(text)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _diff(relative: str, before: str, after: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{relative}",
            tofile=f"b/{relative}",
        )
    )


def _sections(text: str) -> dict[str, tuple[str, str, int, int]]:
    """Return heading -> (canonical heading, body, start, end)."""

    matches = list(_HEADING_RE.finditer(text))
    result: dict[str, tuple[str, str, int, int]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        key = match.group(1).strip().casefold()
        result[key] = (match.group(1).strip(), text[match.end():end], match.start(), end)
    return result


def _section(text: str, heading: str) -> str | None:
    item = _sections(text).get(heading.casefold())
    if item is None:
        return None
    return f"## {item[0]}{item[1]}"


def _replace_section(text: str, heading: str, replacement: str) -> str:
    item = _sections(text).get(heading.casefold())
    if item is None:
        raise UpgradeError(f"managed section is missing: {heading}")
    _name, _body, start, end = item
    remainder = text[end:].lstrip("\n")
    return text[:start] + replacement.rstrip() + ("\n\n" if remainder else "\n") + remainder


def _insert_after_section(text: str, after: str, replacement: str) -> str:
    item = _sections(text).get(after.casefold())
    if item is None:
        raise UpgradeError(f"managed section is missing: {after}")
    _name, _body, _start, end = item
    return text[:end].rstrip() + "\n\n" + replacement.strip() + "\n\n" + text[end:].lstrip("\n")


def _insert_before_section(text: str, before: str, replacement: str) -> str:
    item = _sections(text).get(before.casefold())
    if item is None:
        raise UpgradeError(f"managed section is missing: {before}")
    _name, _body, start, _end = item
    return text[:start].rstrip() + "\n\n" + replacement.strip() + "\n\n" + text[start:]


def _remove_section(text: str, heading: str) -> str:
    item = _sections(text).get(heading.casefold())
    if item is None:
        return text
    _name, _body, start, end = item
    return text[:start].rstrip() + "\n\n" + text[end:].lstrip("\n")


def _same_section(left: str | None, right: str | None) -> bool:
    return left is not None and right is not None and left.strip() == right.strip()


def _same_text(left: str, right: str) -> bool:
    return _normal(left).rstrip() == _normal(right).rstrip()


def _legacy_agents(target: str) -> str:
    """Reconstruct the immediately previous generated Agent contract."""

    legacy = (
        "## State gates\n"
        "Requirements are drafts until user confirmation. Before implementation require an accepted requirement, applicable design/ADR, and TASK/BUG with owner and scope. Keep STATUS, user-facing documentation, configuration, and behavior synchronized in the same change chain. Complete records and code, run semantic checks, fill evidence, commit once, run read-only clean-tree checks. Do not edit the repository after the clean-tree check. Put post-commit output in the external experiment report or handoff."
    )
    if _section(target, "State gates") is None:
        raise UpgradeError("cannot identify the legacy State gates section")
    return _remove_section(_replace_section(target, "State gates", legacy), "Task execution and closure")


def _legacy_workflow(target: str) -> str:
    legacy_finalization = (
        "## Two-phase finalization\n\n"
        "1. Complete all records, source files, tests, and documentation. Synchronize\n"
        "   STATUS, user-facing documentation, and version configuration with behavior.\n"
        "2. Run semantic checks while changes are uncommitted.\n"
        "3. Fill final evidence and terminal statuses.\n"
        "4. Commit the complete task branch once.\n"
        "5. Run read-only clean-tree `pgk check` and `pgk doctor`.\n"
        "6. Do not edit the repository after the clean-tree check. Store post-commit\n"
        "   output in the external experiment report or handoff."
    )
    return _replace_section(_remove_section(target, "Record lifecycle"), "Two-phase finalization", legacy_finalization)


def _legacy_conventions(target: str) -> str:
    legacy_records = (
        "## Records\n\n"
        "The supported lifecycle RecordTypes are `requirement`, `design`, `decision`,\n"
        "`task`, `bug`, `review`, `verification`, and `migration`. Records use YAML\n"
        "frontmatter with `id`, `type`, `status`, `created`, and `updated`.\n\n"
        "The lifecycle statuses are `draft`, `accepted`, `in_progress`, `in_review`,\n"
        "`blocked`, `verified`, `done`, `rejected`, and `superseded`. A record may move to `verified` only when\n"
        "its verification section names the evidence used.\n\n"
        "Strict risk, security, release, runbook, incident, and postmortem documents are\n"
        "ordinary Markdown. Do not add lifecycle frontmatter or invent a RecordType for\n"
        "them. Unknown governance directories, records, statuses, and business modules\n"
        "require an accepted design and task.\n\n"
        "Indexes link to records but do not duplicate their bodies. Meaningful updates\n"
        "append a short timeline entry to the existing record. Do not create a separate\n"
        "implementation log for every progress message."
    )
    legacy_verification = (
        "## Verification\n\n"
        "Verification must name the command or inspection evidence used. A passing test\n"
        "suite does not by itself prove external services, deployment, performance, or\n"
        "long-running behavior."
    )
    legacy_finalization = (
        "## Two-phase finalization\n\n"
        "Complete records and code, run semantic checks, fill evidence, commit once, run\n"
        "read-only clean-tree checks, and do not edit the repository after the clean-tree\n"
        "check. Post-commit output belongs in the external experiment report or handoff."
    )
    result = _remove_section(target, "Kit upgrades")
    result = _replace_section(result, "Records", legacy_records)
    result = _replace_section(result, "Verification", legacy_verification)
    return _replace_section(result, "Two-phase finalization", legacy_finalization)


def _legacy_template(target: str, kind: str) -> str:
    result = target.replace("<!-- PGK_CONTRACT: terminal-v2 -->\n\n", "", 1)
    if kind in {"task", "bug", "verification"}:
        result = result.replace("- AC-1: replace with one observable acceptance criterion\n", "", 1)
        result = result.replace("- AC-1: pending\n", "", 1)
    return result


def _merge_section_document(
    current: str,
    target: str,
    legacy: str,
    specifications: tuple[tuple[str, str | None], ...],
) -> tuple[str | None, tuple[str, ...]]:
    """Merge managed sections and report conflicts without changing custom sections.

    Each specification is ``(heading, insert_before)``. A heading absent from
    the legacy document is considered newly managed and may be inserted.
    """

    conflicts: list[str] = []
    for heading, _insert_before in specifications:
        existing = _section(current, heading)
        target_section = _section(target, heading)
        legacy_section = _section(legacy, heading)
        if target_section is None:
            conflicts.append(f"Kit target section is missing: {heading}")
        elif existing is None and legacy_section is not None:
            conflicts.append(f"managed section is missing: {heading}")
        elif existing is not None and not (
            _same_section(existing, target_section) or _same_section(existing, legacy_section)
        ):
            conflicts.append(f"managed section was customized: {heading}")
    if conflicts:
        return None, tuple(conflicts)

    updated = current
    for heading, insert_before in specifications:
        target_section = _section(target, heading)
        if target_section is None:
            continue
        existing_section = _section(updated, heading)
        if _same_section(existing_section, target_section):
            continue
        if existing_section is None:
            if insert_before is None:
                raise UpgradeError(f"no insertion anchor for new managed section: {heading}")
            updated = _insert_before_section(updated, insert_before, target_section)
        else:
            updated = _replace_section(updated, heading, target_section)
    return updated, ()


def _read(path: Path) -> str:
    try:
        return _normal(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise UpgradeError(f"managed file is missing: {path.as_posix()}") from exc


def _conflict(conflicts: list[dict[str, str]], path: str, message: str) -> None:
    conflicts.append({"path": path, "message": message})


def _config_upgrade(root: Path, target: str) -> tuple[str, str, str]:
    path = root / ".project-governance.toml"
    before = _read(path)
    matches = list(_VERSION_RE.finditer(before))
    if len(matches) != 1:
        raise UpgradeError(".project-governance.toml must contain exactly one kit_version")
    current = matches[0].group(2)
    after = before[:matches[0].start(2)] + target + before[matches[0].end(2):]
    return current, before, after


def _render_targets(root: Path) -> dict[Path, str]:
    config = load_config(root / ".project-governance.toml")
    templates = files_for_visibility(
        config.profile,
        config.visibility,
        config.governance_dir,
        config.public_docs_dir,
    )
    rendered: dict[Path, str] = {}
    values = {
        "project_name": root.name,
        "date": datetime.now().date().isoformat(),
        "git_state": "git_initialized",
        "profile": config.profile,
        "collaboration_mode": config.collaboration_mode,
        "visibility": config.visibility,
        "governance_dir": config.governance_dir,
        "public_docs_dir": config.public_docs_dir,
        "kit_version": __version__,
    }
    for relative, content in templates.items():
        if relative == ".project-governance.toml":
            continue
        try:
            content = content.format(**values)
        except KeyError as exc:
            raise UpgradeError(f"cannot render Kit template {relative}: {exc}") from exc
        rendered[root / relative] = _normal(content)
    return rendered


def _plan_file(
    root: Path,
    path: Path,
    after: str,
    changed: list[dict[str, object]],
    unchanged: list[str],
) -> None:
    relative = path.relative_to(root).as_posix()
    before = _read(path)
    after = _normal(after)
    if before == after:
        unchanged.append(relative)
        return
    changed.append(
        {
            "path": relative,
            "before_hash": _hash(before),
            "after_hash": _hash(after),
            "diff": _diff(relative, before, after),
        }
    )


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".pgk-tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".pgk-tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _upgrade_activity(before: str, from_version: str) -> str:
    event = f" | upgrade | N/A | {from_version}->{__version__} |"
    if event in before:
        return before
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    if not before.endswith("\n"):
        before += "\n"
    return before + f"{timestamp} | pgk | upgrade | N/A | {from_version}->{__version__} | governed contract upgraded\n"


def _generated_marker(path: Path, governance_dir: Path) -> str:
    relative = path.relative_to(governance_dir).as_posix()
    if relative == "work/BOARD.md":
        return "board"
    if relative == "work/INDEX.md":
        return "work-index"
    if relative == "activity/ACTIVITY.md":
        return "activity"
    if relative.endswith("/INDEX.md"):
        directory = Path(relative).parent.name
        directory = {
            "requirements": "requirement",
            "decisions": "decision",
            "tasks": "task",
            "bugs": "bug",
            "reviews": "review",
            "migrations": "migration",
        }.get(directory, directory)
        return f"{directory}-index"
    return ""


def upgrade_project(root: str | Path, *, apply: bool = False) -> UpgradeResult:
    """Plan or apply the known governed-project Kit upgrade.

    ``apply=False`` is the default and never writes the target project.
    """

    root = Path(root).resolve()
    if not root.is_dir():
        raise UpgradeError(f"project root does not exist: {root}")
    config_path = root / ".project-governance.toml"
    if not config_path.is_file():
        raise UpgradeError("target is not a governed project: .project-governance.toml is missing")

    from_version, _config_before, config_after = _config_upgrade(root, __version__)
    if from_version not in SUPPORTED_SOURCE_VERSIONS:
        raise UnsupportedUpgradeError(f"unsupported Kit upgrade source version: {from_version}")

    rendered = _render_targets(root)
    conflicts: list[dict[str, str]] = []
    planned: dict[Path, str] = {}

    agents = root / "AGENTS.md"
    try:
        current_agents = _read(agents)
        target_agents = rendered[agents]
        legacy_agents = _legacy_agents(target_agents)
        for heading in _KIT_MANAGED_HEADINGS:
            expected_target = _section(target_agents, heading)
            existing = _section(current_agents, heading)
            if expected_target is None:
                continue
            if existing is None:
                if heading == "Task execution and closure":
                    continue
                _conflict(conflicts, "AGENTS.md", f"managed section is missing: {heading}")
                continue
            expected_legacy = _section(legacy_agents, heading)
            if not (
                _same_section(existing, expected_legacy)
                or _same_section(existing, expected_target)
            ):
                _conflict(conflicts, "AGENTS.md", f"managed section was customized: {heading}")
        if not any(item["path"] == "AGENTS.md" for item in conflicts):
            updated = current_agents
            for heading in _KIT_MANAGED_HEADINGS:
                expected_target = _section(target_agents, heading)
                if expected_target is None:
                    continue
                if _section(updated, heading) is None:
                    if heading == "Task execution and closure":
                        updated = _insert_after_section(updated, "State gates", expected_target)
                else:
                    updated = _replace_section(updated, heading, expected_target)
            planned[agents] = updated
    except UpgradeError as exc:
        _conflict(conflicts, "AGENTS.md", str(exc))

    governance_targets = {
        "WORKFLOW.md": (
            _legacy_workflow,
            "workflow",
            (
                ("Record lifecycle", "Two-phase finalization"),
                ("Two-phase finalization", None),
            ),
        ),
        "project-conventions.md": (
            _legacy_conventions,
            "project-conventions",
            (
                ("Records", None),
                ("Verification", None),
                ("Kit upgrades", "Two-phase finalization"),
                ("Two-phase finalization", None),
            ),
        ),
    }
    config = load_config(config_path)
    governance_dir = Path(config.governance_dir)
    for filename, (legacy_builder, label, specifications) in governance_targets.items():
        relative = (governance_dir / filename).as_posix()
        path = root / relative
        try:
            before = _read(path)
            target = rendered.get(path)
            if target is None:
                raise UpgradeError(f"Kit template is unavailable for {relative}")
            if f"<!-- PGK_GENERATED: {label} -->" not in before:
                raise UpgradeError("generated marker is missing")
            legacy = legacy_builder(target)
            merged, merge_conflicts = _merge_section_document(before, target, legacy, specifications)
            for message in merge_conflicts:
                _conflict(conflicts, relative, message)
            if merged is not None:
                planned[path] = merged
        except UpgradeError as exc:
            _conflict(conflicts, relative, str(exc))

    for kind in ("task", "bug", "verification"):
        relative = (governance_dir / "templates" / f"{kind}.md").as_posix()
        path = root / relative
        try:
            before = _read(path)
            target = rendered.get(path)
            if target is None:
                raise UpgradeError(f"Kit template is unavailable for {relative}")
            if "<!-- PGK_CONTRACT: terminal-v2 -->" not in target:
                raise UpgradeError("target template has no terminal-v2 marker")
            if not (_same_text(before, _legacy_template(target, kind)) or _same_text(before, target)):
                _conflict(conflicts, relative, "Kit template was customized")
            else:
                planned[path] = target
        except UpgradeError as exc:
            _conflict(conflicts, relative, str(exc))

    try:
        generated = expected_generated_views(root)
    except (OSError, ValueError) as exc:
        _conflict(conflicts, "generated views", f"cannot render generated views: {exc}")
        generated = {}
    managed_changes = from_version != __version__ or any(
        not _same_text(_read(path), target)
        for path, target in planned.items()
    )
    for path, target in generated.items():
        relative = path.relative_to(root).as_posix()
        try:
            before = _read(path)
            marker = _generated_marker(path, root / governance_dir)
            if not marker or f"<!-- PGK_GENERATED: {marker} -->" not in before:
                raise UpgradeError("generated marker is missing")
            planned[path] = _normal(target)
        except UpgradeError as exc:
            _conflict(conflicts, relative, str(exc))

    activity = root / governance_dir / "activity/ACTIVITY.md"
    try:
        before = _read(activity)
        if "<!-- PGK_GENERATED: activity -->" not in before:
            raise UpgradeError("generated marker is missing")
        planned[activity] = _upgrade_activity(before, from_version) if managed_changes else before
    except UpgradeError as exc:
        _conflict(conflicts, activity.relative_to(root).as_posix(), str(exc))

    planned[config_path] = config_after
    planned = {
        path: _preserve_newlines(path, target)
        for path, target in planned.items()
    }
    changed: list[dict[str, object]] = []
    unchanged: list[str] = []
    for path, target in sorted(planned.items(), key=lambda item: item[0].relative_to(root).as_posix()):
        _plan_file(root, path, target, changed, unchanged)

    if conflicts or not apply:
        return UpgradeResult(from_version, __version__, tuple(changed), tuple(sorted(unchanged)), tuple(conflicts), not apply, False)

    originals = {path: path.read_bytes() for path in planned if path.exists()}
    written: list[Path] = []
    try:
        # The configuration is deliberately last: it is the version claim for
        # the already-written governed contract.
        for path, target in sorted(planned.items(), key=lambda item: (item[0] == config_path, item[0].as_posix())):
            if originals.get(path, b"").decode("utf-8") == target:
                continue
            _atomic_write(path, target)
            written.append(path)
    except Exception as exc:
        for path in reversed(written):
            try:
                _atomic_write_bytes(path, originals[path])
            except OSError:
                pass
        conflict = {"path": "apply", "message": f"upgrade rolled back after write failure: {exc}"}
        return UpgradeResult(from_version, __version__, tuple(changed), tuple(sorted(unchanged)), (conflict,), False, False)

    return UpgradeResult(from_version, __version__, tuple(changed), tuple(sorted(unchanged)), (), False, True)


__all__ = [
    "SUPPORTED_SOURCE_VERSIONS",
    "UpgradeError",
    "UnsupportedUpgradeError",
    "UpgradeResult",
    "upgrade_project",
]
