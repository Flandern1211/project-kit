"""Deterministic record-contract checks without business-semantic inference."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Mapping

from .lifecycle import TERMINAL_STATUSES, status_allowed
from .models import RecordMetadata, RecordType


TERMINAL_CONTRACT_MARKER = "<!-- PGK_CONTRACT: terminal-v2 -->"
_PLACEHOLDER = re.compile(
    r"(?i)^(?:n/?a|none|pending(?:[-_ ].*)?|working[-_ ]?tree|this commit|"
    r"current commit|final task commit|todo|tbd|not (?:run|verified|provided)|"
    r"待补|待验证|未执行|未验证)$"
)
_AC_LINE = re.compile(
    r"^\s*[-*]\s*(?:\[[ xX]\]\s*)?(AC-[A-Za-z0-9][A-Za-z0-9._-]*)\s*[:：-]\s*(.+?)\s*$"
)
_COMMIT_ID = re.compile(r"[0-9a-fA-F]{7,40}")
_V2_RECORD_TYPES = frozenset({RecordType.TASK, RecordType.BUG, RecordType.VERIFICATION})


@dataclass(frozen=True, slots=True)
class ContractIssue:
    code: str
    message: str


RecordMap = Mapping[str, tuple[str, RecordMetadata, str]]


def body_sections(body: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?im)^##\s+([^\n]+)\s*$", body))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result[match.group(1).strip().casefold()] = body[match.end():end].strip()
    return result


def section_value(body: str, name: str) -> str:
    value = body_sections(body).get(name.casefold(), "")
    for line in value.splitlines():
        candidate = line.strip(" -*\t`").strip()
        if candidate:
            return candidate
    return ""


def is_declared(value: str) -> bool:
    return bool(value and not _PLACEHOLDER.fullmatch(value.strip()))


def acceptance_map(body: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in body_sections(body).get("acceptance", "").splitlines():
        match = _AC_LINE.match(line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def evidence_map(body: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in body_sections(body).get("evidence", "").splitlines():
        match = _AC_LINE.match(line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def literal_file_references(body: str) -> tuple[str, ...]:
    section = body_sections(body).get("files", "")
    values: list[str] = []
    for line in section.splitlines():
        # A Files section can document an external repository or an optional
        # directory. Validate only literal paths owned by this repository.
        if re.search(r"(?i)external\s+(?:repository|repo)|外部仓库", line):
            continue
        for value in re.findall(r"`([^`]+)`", line):
            raw = value.strip()
            directory_hint = raw.endswith(("/", "\\"))
            normalized = raw.rstrip("/\\")
            if not normalized or directory_hint or any(character in normalized for character in "*?[]{}"):
                continue
            if normalized.casefold() in {"n/a", "none"}:
                continue
            if ":" in normalized or normalized.startswith(("/", "\\")):
                continue
            if "/" not in normalized and "\\" not in normalized and "." not in Path(normalized).name:
                continue
            values.append(normalized.replace("\\", "/"))
    return tuple(dict.fromkeys(values))


def git_field(body: str, name: str) -> str:
    section = body_sections(body).get("git", "")
    match = re.search(rf"(?im)^\s*{re.escape(name)}\s*:\s*(.+?)\s*$", section)
    return match.group(1).strip().strip("`") if match else ""


def _record_commit_resolves(root: Path, relative: str) -> bool:
    """Resolve record-commit after commit while allowing the pre-commit dirty phase."""

    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", relative],
            cwd=root, check=True, capture_output=True, text=True,
        ).stdout.strip()
        if dirty:
            return True
        commit = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", relative],
            cwd=root, check=True, capture_output=True, text=True,
        ).stdout.strip()
        return bool(re.fullmatch(r"[0-9a-fA-F]{40}", commit))
    except (OSError, subprocess.CalledProcessError):
        return False


def _commit_id_resolves(root: Path, value: str) -> bool:
    if not _COMMIT_ID.fullmatch(value):
        return False
    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{value}^{{commit}}"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _accepted(records: RecordMap, related: list[str], kinds: set[RecordType]) -> bool:
    return any(
        item[1].type in kinds and item[1].status.value == "accepted"
        for record_id in related
        if (item := records.get(record_id)) is not None
    )


def record_contract_issues(
    root: Path,
    relative: str,
    metadata: RecordMetadata,
    body: str,
    records: RecordMap,
    *,
    profile: str,
    require_v2: bool = False,
) -> tuple[ContractIssue, ...]:
    issues: list[ContractIssue] = []
    if not status_allowed(metadata.type, metadata.status):
        issues.append(ContractIssue("invalid_status_for_type", f"{metadata.type.value} does not support status {metadata.status.value}"))

    if metadata.type in {RecordType.TASK, RecordType.BUG}:
        for value in literal_file_references(body):
            if not (root / value).exists():
                issues.append(ContractIssue("missing_declared_file", f"declared file does not exist: {value}"))

    if metadata.status not in TERMINAL_STATUSES:
        return tuple(issues)

    if metadata.type in {RecordType.TASK, RecordType.BUG}:
        for field in ("owner", "scope", "files", "acceptance", "evidence"):
            if not is_declared(section_value(body, field)):
                issues.append(ContractIssue("missing_record_value", f"terminal record field is not declared: {field.title()}"))
        head_commit = git_field(body, "head_commit")
        if not head_commit or _PLACEHOLDER.fullmatch(head_commit):
            issues.append(ContractIssue("untraceable_head_commit", "terminal task/bug head_commit must be a commit id or record-commit"))
        elif head_commit == "record-commit":
            if not _record_commit_resolves(root, relative):
                issues.append(ContractIssue("untraceable_head_commit", "record-commit requires a committed version or a modified task record in a Git repository"))
        elif head_commit != "record-commit" and not _commit_id_resolves(root, head_commit):
            issues.append(ContractIssue("untraceable_head_commit", "terminal task/bug head_commit is not a commit in this repository"))
    elif metadata.type is RecordType.VERIFICATION:
        for field in ("owner", "scope", "acceptance", "evidence"):
            if not is_declared(section_value(body, field)):
                issues.append(ContractIssue("missing_record_value", f"terminal record field is not declared: {field.title()}"))
    elif metadata.type is RecordType.REVIEW:
        for field in ("owner", "scope", "acceptance", "evidence", "base commit", "head commit", "findings", "verdict"):
            if not is_declared(section_value(body, field)):
                issues.append(ContractIssue("missing_record_value", f"terminal record field is not declared: {field.title()}"))

    uses_v2 = TERMINAL_CONTRACT_MARKER in body
    if require_v2 and metadata.type in _V2_RECORD_TYPES and not uses_v2:
        issues.append(ContractIssue("missing_terminal_contract", "terminal transition requires the terminal-v2 contract marker"))
    if metadata.type not in _V2_RECORD_TYPES or not uses_v2:
        return tuple(issues)

    if metadata.type in {RecordType.TASK, RecordType.BUG}:
        if metadata.type is RecordType.TASK:
            if not _accepted(records, metadata.related, {RecordType.REQUIREMENT}):
                issues.append(ContractIssue("unaccepted_upstream_record", "terminal task requires an accepted requirement"))
            if profile != "lite" and not _accepted(records, metadata.related, {RecordType.DESIGN, RecordType.DECISION}):
                issues.append(ContractIssue("unaccepted_upstream_record", "terminal task requires an accepted design or decision"))

        task_acceptance = acceptance_map(body)
        if not task_acceptance:
            issues.append(ContractIssue("missing_acceptance_ids", "terminal-v2 task/bug acceptance must use AC-* identifiers"))

        verifications = [
            item for item in records.values()
            if item[1].type is RecordType.VERIFICATION
            and metadata.id in item[1].related
            and item[1].status in TERMINAL_STATUSES
        ]
        if not verifications:
            issues.append(ContractIssue("missing_terminal_verification", "terminal task/bug requires a reciprocal verified verification record"))
        else:
            evidence = body_sections(body).get("evidence", "")
            if not any(item[1].id in evidence for item in verifications):
                issues.append(ContractIssue("missing_terminal_verification", "task/bug Evidence must name its verified VER record"))
            covered_acceptance: dict[str, str] = {}
            covered_evidence: dict[str, str] = {}
            for _path, _meta, verification_body in verifications:
                covered_acceptance.update(acceptance_map(verification_body))
                covered_evidence.update(evidence_map(verification_body))
            for acceptance_id in task_acceptance:
                if not is_declared(covered_acceptance.get(acceptance_id, "")) or not is_declared(covered_evidence.get(acceptance_id, "")):
                    issues.append(ContractIssue("unverified_acceptance", f"acceptance {acceptance_id} lacks declared verification outcome and evidence"))

        if profile == "strict":
            reviews = [
                item for item in records.values()
                if item[1].type is RecordType.REVIEW
                and metadata.id in item[1].related
                and item[1].status in TERMINAL_STATUSES
            ]
            if not reviews:
                issues.append(ContractIssue("missing_terminal_review", "strict profile terminal task/bug requires a reciprocal verified review"))

    elif metadata.type is RecordType.VERIFICATION:
        targets = [records[item] for item in metadata.related if item in records and records[item][1].type in {RecordType.TASK, RecordType.BUG}]
        if not targets:
            issues.append(ContractIssue("missing_verification_target", "terminal verification requires a related task or bug"))
        for _path, target, target_body in targets:
            for acceptance_id in acceptance_map(target_body):
                if not is_declared(acceptance_map(body).get(acceptance_id, "")) or not is_declared(evidence_map(body).get(acceptance_id, "")):
                    issues.append(ContractIssue("unverified_acceptance", f"verification does not cover {target.id} acceptance {acceptance_id}"))

    return tuple(issues)


__all__ = [
    "ContractIssue", "TERMINAL_CONTRACT_MARKER", "acceptance_map", "body_sections",
    "evidence_map", "git_field", "is_declared", "literal_file_references",
    "record_contract_issues", "section_value",
]
