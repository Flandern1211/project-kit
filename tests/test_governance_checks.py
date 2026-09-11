from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from project_governance.authorization import authorization_matches
from project_governance.checks import _scope_values, run_checks
from project_governance.git_context import inspect_git
from project_governance.records import create_record
from project_governance.scaffold import init_project


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _task(root: Path, record_id: str, *, scope: str = "src/app.py", include_scope: bool = True) -> Path:
    body = "# Task\n\n## Purpose\nwork\n\n"
    if include_scope:
        body += f"## Scope\n- {scope}\n\n"
    body += "## Acceptance\npass\n\n## Evidence\npytest\n\n## Changes\ncode\n\n## Blockers\nnone\n\n## Next action\nship\n"
    path = root / "docs/work/tasks" / f"{record_id}.md"
    path.write_text(
        "---\n"
        f"id: {record_id}\n"
        "type: task\nstatus: in_progress\n"
        "created: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n" + body,
        encoding="utf-8",
    )
    return path


def test_checks_require_standard_views_and_indexes(tmp_path: Path):
    init_project(tmp_path)
    (tmp_path / "docs/WORKFLOW.md").unlink()
    (tmp_path / "docs/reviews/INDEX.md").unlink()

    result = run_checks(tmp_path)

    assert not result.ok
    codes = {issue["code"] for issue in result.issues}
    assert "missing_required_view" in codes
    assert "missing_record_index" in codes


def test_checks_ignore_local_agent_projection_documents(tmp_path: Path):
    init_project(tmp_path)
    projection = tmp_path / ".agent/manifest.json"
    projection.parent.mkdir()
    projection.write_text('{"id": "not-a-record"}', encoding="utf-8")
    projection_doc = tmp_path / ".agent/projection.md"
    projection_doc.write_text("[broken](missing.md)", encoding="utf-8")

    result = run_checks(tmp_path)

    assert ".agent/projection.md" not in result.checked_files
    assert not any(issue["path"].startswith(".agent/") for issue in result.issues)


def test_checks_do_not_skip_views_when_governance_marker_lacks_stage(tmp_path: Path):
    init_project(tmp_path)
    status = tmp_path / "docs/STATUS.md"
    status.write_text("# Project status\n", encoding="utf-8")
    (tmp_path / "docs/WORKFLOW.md").unlink()
    (tmp_path / "docs/reviews/INDEX.md").unlink()

    result = run_checks(tmp_path)
    codes = {issue["code"] for issue in result.issues}
    assert "missing_required_view" in codes
    assert "missing_record_index" in codes


def test_checks_report_missing_task_field(tmp_path: Path):
    init_project(tmp_path)
    _task(tmp_path, "TASK-001", include_scope=False)

    result = run_checks(tmp_path)

    assert not result.ok
    assert any(issue["code"] == "missing_record_field" and "Scope" in issue["message"] for issue in result.issues)


def test_checks_require_task_owner_files_and_git_fields(tmp_path: Path):
    init_project(tmp_path)
    _task(tmp_path, "TASK-001", scope="src/app.py")

    result = run_checks(tmp_path)

    missing = {issue["message"] for issue in result.issues if issue["code"] == "missing_record_field"}
    assert {"missing required field: Owner", "missing required field: Files", "missing required field: Branch", "missing required field: Worktree", "missing required field: Base Commit", "missing required field: Head Commit"} <= missing


def test_checks_validate_review_verification_sections_ids_and_related(tmp_path: Path):
    init_project(tmp_path)
    path = tmp_path / "docs/reviews/REVIEW-bad.md"
    path.write_text("""---
id: BAD
type: review
status: in_review
created: 2026-09-04
updated: 2026-09-04
related:
  - NOT-A-RECORD
---
# Review
## Purpose
work
""", encoding="utf-8")

    result = run_checks(tmp_path)
    codes = {issue["code"] for issue in result.issues}
    assert "invalid_record_id" in codes
    assert "invalid_related_id" in codes
    assert "missing_record_field" in codes


def test_checks_normalize_directory_and_separator_file_scope_overlap(tmp_path: Path):
    init_project(tmp_path)
    _task(tmp_path, "TASK-001", scope="src/")
    _task(tmp_path, "TASK-002", scope=".\\src\\app.py")

    result = run_checks(tmp_path)

    assert any(issue["code"] == "overlapping_file_scope" for issue in result.issues)


def test_scope_values_strip_punctuation_around_inline_code_paths():
    assert _scope_values("## Scope\n- `tests/`.\n") == ("tests/",)


def test_checks_report_revoked_authorization_consistently(tmp_path: Path):
    init_project(tmp_path)
    path = tmp_path / "docs/decisions/ADR-001-auth.md"
    path.write_text("""---
id: ADR-001
type: decision
status: accepted
created: 2026-09-04
updated: 2026-09-04
related:
---
## Authorization
action: commit
target: repo/main
scope: TASK-001
valid_from: 2026-09-01T00:00:00+00:00
expires_at: 2026-09-30T00:00:00+00:00
status: active
revoked: true
""", encoding="utf-8")

    result = run_checks(tmp_path)

    assert any(issue["code"] == "invalid_authorization" and "revoked" in issue["message"] for issue in result.issues)


def test_checks_require_accepted_requirement_and_design_for_actionable_task(tmp_path: Path):
    init_project(tmp_path)
    req = tmp_path / "docs/requirements/REQ-001-draft.md"
    req.write_text("""---
id: REQ-001
type: requirement
status: draft
created: 2026-09-04
updated: 2026-09-04
related:
---
# Requirement
""", encoding="utf-8")
    task = _task(tmp_path, "TASK-001")
    task.write_text(task.read_text(encoding="utf-8").replace("related:\n---", "related:\n  - REQ-001\n  - DES-001\n---"), encoding="utf-8")

    result = run_checks(tmp_path)
    codes = {issue["code"] for issue in result.issues}
    assert "unaccepted_upstream_record" in codes
    assert "missing_upstream_record" in codes


def test_authorization_rejects_expired_revoked_and_mismatched_actions():
    record = """---
id: AUTH-001
type: decision
status: accepted
created: 2026-09-01
updated: 2026-09-01
related:
---
## Authorization
action: commit
target: repo/main
scope: TASK-001
valid_from: 2026-09-01T00:00:00+00:00
expires_at: 2026-09-30T00:00:00+00:00
status: active
"""
    at = datetime(2026, 9, 4, tzinfo=timezone.utc)

    assert authorization_matches(record, "commit", "repo/main", at)
    assert not authorization_matches(record.replace("status: active", "status: revoked"), "commit", "repo/main", at)
    assert not authorization_matches(record.replace("expires_at: 2026-09-30", "expires_at: 2026-09-03"), "commit", "repo/main", at)
    assert not authorization_matches(record, "push", "repo/main", at)
    assert authorization_matches(record, "commit", "repo/main", at, scope="TASK-001")
    assert not authorization_matches(record, "commit", "repo/main", at, scope="TASK-002")
    assert not authorization_matches(record.replace("status: active", "status: pending"), "commit", "repo/main", at)
    assert not authorization_matches(record.replace("status: active", "status: unknown"), "commit", "repo/main", at)


def test_checks_report_dirty_git_and_overlapping_file_scopes(tmp_path: Path):
    init_project(tmp_path)
    _task(tmp_path, "TASK-001", scope="src/shared.py")
    _task(tmp_path, "TASK-002", scope="src/shared.py")
    _git(tmp_path, "init", "--quiet")
    _git(tmp_path, "config", "user.email", "test@example.test")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "baseline")
    (tmp_path / "dirty.txt").write_text("changed", encoding="utf-8")

    result = run_checks(tmp_path)

    codes = {issue["code"] for issue in result.issues}
    assert "dirty_worktree" in codes
    assert "overlapping_file_scope" in codes


def test_checks_validate_status_and_generated_view_contracts(tmp_path: Path):
    init_project(tmp_path)
    status = tmp_path / "docs/STATUS.md"
    status.write_text(
        "# status\n\n```yaml\nproject_stage: maintenance\nowner: root\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "docs/WORKFLOW.md").write_text("# workflow\n", encoding="utf-8")
    (tmp_path / "docs/work/BOARD.md").write_text("# board\n", encoding="utf-8")
    (tmp_path / "docs/requirements/INDEX.md").write_text("# index\n", encoding="utf-8")
    (tmp_path / "docs/activity/ACTIVITY.md").write_text("# activity\n", encoding="utf-8")

    result = run_checks(tmp_path)
    codes = {issue["code"] for issue in result.issues}
    assert "missing_status_field" in codes
    assert "invalid_view_marker" in codes
    assert "invalid_workflow_contract" in codes
    assert "invalid_board_contract" in codes
    assert "invalid_activity_header" in codes


def test_checks_validate_status_record_references(tmp_path: Path):
    init_project(tmp_path)
    task = create_record(tmp_path, "task", "TASK-404", "Status reference type fixture")
    task_text = task.read_text(encoding="utf-8").replace("related:\n---", "related:\n  - REQ-001\n---")
    task.write_text(task_text, encoding="utf-8")
    status = tmp_path / "docs/STATUS.md"
    status.write_text(
        status.read_text(encoding="utf-8")
        .replace("current_requirement: N/A", "current_requirement: TASK-404")
        .replace("current_design: N/A", "current_design: DES-404")
        .replace("current_task: N/A", "active_task: TASK-405\ncurrent_task: TASK-404"),
        encoding="utf-8",
    )

    result = run_checks(tmp_path)
    issues = [issue for issue in result.issues if issue["path"] == "docs/STATUS.md"]

    assert any(issue["code"] == "invalid_status_reference" and "current_requirement" in issue["message"] for issue in issues)
    assert any(issue["code"] == "unknown_status_reference" and "current_design" in issue["message"] for issue in issues)
    assert any(issue["code"] == "status_reference_mismatch" for issue in issues)


def test_checks_require_status_upstreams_to_match_current_task(tmp_path: Path):
    init_project(tmp_path)
    for record_id, kind in (
        ("REQ-001", "requirement"),
        ("REQ-002", "requirement"),
        ("DES-001", "design"),
        ("DES-002", "design"),
    ):
        create_record(tmp_path, kind, record_id, record_id, status="accepted")
    create_record(
        tmp_path, "task", "TASK-001", "Current task", status="in_progress",
        related=("REQ-001", "DES-001"),
    )
    status = tmp_path / "docs/STATUS.md"
    status.write_text(
        status.read_text(encoding="utf-8")
        .replace("current_requirement: N/A", "current_requirement: REQ-002")
        .replace("current_design: N/A", "current_design: DES-002")
        .replace("current_task: N/A", "current_task: TASK-001"),
        encoding="utf-8",
    )

    result = run_checks(tmp_path)
    messages = [
        issue["message"] for issue in result.issues
        if issue["code"] == "status_reference_mismatch"
    ]

    assert any("current_requirement" in message for message in messages)
    assert any("current_design" in message for message in messages)


def test_checks_require_review_and_verification_contract_sections(tmp_path: Path):
    init_project(tmp_path)
    review = tmp_path / "docs/reviews/REVIEW-001-review.md"
    review.write_text(
        "---\nid: REVIEW-001\ntype: review\nstatus: in_review\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n"
        "# Review\n\n## Owner\nagent\n\n## Scope\ncode\n\n## Evidence\npytest\n",
        encoding="utf-8",
    )
    verification = tmp_path / "docs/verification/VER-002-verification.md"
    verification.write_text(
        "---\nid: VER-002\ntype: verification\nstatus: verified\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n"
        "# Verification\n\n## Owner\nagent\n\n## Scope\nfixture\n\n## Evidence\npytest\n",
        encoding="utf-8",
    )
    result = run_checks(tmp_path)
    missing = [issue for issue in result.issues if issue["code"] == "missing_record_field"]
    assert any(issue["path"].endswith("REVIEW-001-review.md") and "Verdict" in issue["message"] for issue in missing)
    assert any(issue["path"].endswith("VER-002-verification.md") and "Acceptance" in issue["message"] for issue in missing)


def test_checks_accept_branch_declared_in_handoff(tmp_path: Path):
    _git(tmp_path, "init", "--quiet")
    _git(tmp_path, "config", "user.email", "test@example.test")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "baseline.txt").write_text("baseline", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "baseline")
    _git(tmp_path, "checkout", "-qb", "task/TASK-001-demo")
    init_project(tmp_path)
    _task(tmp_path, "TASK-001", scope="src/app.py")
    (tmp_path / "docs/requirements/REQ-001.md").write_text(
        "---\nid: REQ-001\ntype: requirement\nstatus: accepted\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n",
        encoding="utf-8",
    )
    (tmp_path / "docs/design/DES-001.md").write_text(
        "---\nid: DES-001\ntype: design\nstatus: accepted\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n",
        encoding="utf-8",
    )
    task = tmp_path / "docs/work/tasks/TASK-001.md"
    task.write_text(task.read_text(encoding="utf-8").replace("related:\n---", "related:\n  - REQ-001\n  - DES-001\n---"), encoding="utf-8")
    task.write_text(task.read_text(encoding="utf-8") + "\n## Handoff\n\n<!-- PGK_HANDOFF_START -->\n<!-- PGK_HANDOFF_END -->\n", encoding="utf-8")
    from project_governance.handoff import update_handoff
    update_handoff(tmp_path, "TASK-001", next_action="continue")

    result = run_checks(tmp_path)
    assert not any(issue["code"] == "unregistered_branch" for issue in result.issues)


def test_checks_accept_branch_declared_by_verified_task(tmp_path: Path):
    init_project(tmp_path)
    task = create_record(tmp_path, "task", "TASK-901", "Verified branch", status="verified")
    text = task.read_text(encoding="utf-8")
    task.write_text(text.replace("branch: N/A", "branch: task/TASK-901-verified"), encoding="utf-8")

    result = run_checks(tmp_path)

    assert not any(
        issue["code"] == "unregistered_branch" and "task/TASK-901-verified" in issue["message"]
        for issue in result.issues
    )


def test_checks_ignore_unregistered_branch_already_merged_into_head(tmp_path: Path):
    _git(tmp_path, "init", "--quiet")
    _git(tmp_path, "config", "user.email", "test@example.test")
    _git(tmp_path, "config", "user.name", "Test")
    init_project(tmp_path)
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "baseline")
    main_branch = subprocess.run(
        ["git", "branch", "--show-current"], cwd=tmp_path, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    _git(tmp_path, "checkout", "-qb", "task/TASK-999-historical")
    (tmp_path / "historical.txt").write_text("merged", encoding="utf-8")
    _git(tmp_path, "add", "historical.txt")
    _git(tmp_path, "commit", "-qm", "historical task")
    _git(tmp_path, "checkout", "-q", main_branch)
    _git(tmp_path, "merge", "--no-ff", "-qm", "merge historical task", "task/TASK-999-historical")

    result = run_checks(tmp_path)

    assert not any(
        issue["code"] == "unregistered_branch" and "task/TASK-999-historical" in issue["message"]
        for issue in result.issues
    )


def test_checks_report_current_unregistered_task_branch(tmp_path: Path):
    _git(tmp_path, "init", "--quiet")
    _git(tmp_path, "config", "user.email", "test@example.test")
    _git(tmp_path, "config", "user.name", "Test")
    init_project(tmp_path)
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "baseline")
    _git(tmp_path, "checkout", "-qb", "task/TASK-999-unregistered")

    result = run_checks(tmp_path)

    assert any(
        issue["code"] == "unregistered_branch" and "task/TASK-999-unregistered" in issue["message"]
        for issue in result.issues
    )


def test_checks_require_standard_baseline_files(tmp_path: Path):
    init_project(tmp_path)
    (tmp_path / "README.md").unlink()
    (tmp_path / ".gitignore").unlink()
    (tmp_path / ".project-governance.toml").unlink()
    result = run_checks(tmp_path)
    missing = {issue["path"] for issue in result.issues if issue["code"] == "missing_baseline"}
    assert {"README.md", ".gitignore", ".project-governance.toml"} <= missing


def test_checks_reject_actionable_task_with_unassigned_values(tmp_path: Path):
    init_project(tmp_path)
    _task(tmp_path, "TASK-010", scope="N/A")
    task = tmp_path / "docs/work/tasks/TASK-010.md"
    task.write_text(task.read_text(encoding="utf-8").replace("related:\n---", "related:\n  - REQ-010\n  - DES-010\n---"), encoding="utf-8")
    (tmp_path / "docs/requirements/REQ-010.md").write_text(
        "---\nid: REQ-010\ntype: requirement\nstatus: accepted\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n", encoding="utf-8"
    )
    (tmp_path / "docs/design/DES-010.md").write_text(
        "---\nid: DES-010\ntype: design\nstatus: accepted\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n", encoding="utf-8"
    )
    result = run_checks(tmp_path)
    assert any(issue["code"] == "missing_record_value" for issue in result.issues)


def test_checks_block_actionable_work_without_git_repository(tmp_path: Path):
    init_project(tmp_path)
    _task(tmp_path, "TASK-011", scope="src/app.py")
    task = tmp_path / "docs/work/tasks/TASK-011.md"
    task.write_text(task.read_text(encoding="utf-8").replace("related:\n---", "related:\n  - REQ-011\n  - DES-011\n---"), encoding="utf-8")
    (tmp_path / "docs/requirements/REQ-011.md").write_text(
        "---\nid: REQ-011\ntype: requirement\nstatus: accepted\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n", encoding="utf-8"
    )
    (tmp_path / "docs/design/DES-011.md").write_text(
        "---\nid: DES-011\ntype: design\nstatus: accepted\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n", encoding="utf-8"
    )
    result = run_checks(tmp_path)
    assert any(issue["code"] == "git_not_initialized" for issue in result.issues)


def test_checks_report_status_git_state_mismatch(tmp_path: Path):
    init_project(tmp_path)
    status = tmp_path / "docs/STATUS.md"
    status.write_text(status.read_text(encoding="utf-8").replace("git_state: git_not_initialized", "git_state: git_initialized"), encoding="utf-8")
    result = run_checks(tmp_path)
    assert any(issue["code"] == "git_state_mismatch" for issue in result.issues)


def test_checks_require_non_empty_terminal_review_and_verification_values(tmp_path: Path):
    init_project(tmp_path)
    review = tmp_path / "docs/reviews/REVIEW-010-empty.md"
    review.write_text(
        "---\nid: REVIEW-010\ntype: review\nstatus: verified\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n"
        "# Review\n## Owner\nagent\n## Scope\ncode\n## Acceptance\naccepted\n## Evidence\npytest\n## Blockers\nnone\n## Next action\nnone\n## Base commit\n\n## Head commit\n\n## Findings\n\n## Verdict\n\n",
        encoding="utf-8",
    )
    verification = tmp_path / "docs/verification/VER-010-empty.md"
    verification.write_text(
        "---\nid: VER-010\ntype: verification\nstatus: verified\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n---\n"
        "# Verification\n## Owner\nagent\n## Scope\nfixture\n## Acceptance\n\n## Evidence\n\n## Blockers\nnone\n## Next action\nnone\n",
        encoding="utf-8",
    )
    result = run_checks(tmp_path)
    values = [issue for issue in result.issues if issue["code"] == "missing_record_value"]
    assert any(issue["path"].endswith("REVIEW-010-empty.md") and "Verdict" in issue["message"] for issue in values)
    assert any(issue["path"].endswith("VER-010-empty.md") and "Evidence" in issue["message"] for issue in values)


def test_checks_report_unknown_related_record_ids(tmp_path: Path):
    init_project(tmp_path)
    review = tmp_path / "docs/reviews/REVIEW-011-unknown.md"
    review.write_text(
        "---\nid: REVIEW-011\ntype: review\nstatus: in_review\ncreated: 2026-09-04\nupdated: 2026-09-04\nrelated:\n  - TASK-999\n---\n"
        "# Review\n## Owner\nagent\n## Scope\ncode\n## Acceptance\naccepted\n## Evidence\npytest\n## Blockers\nnone\n## Next action\ncontinue\n## Base commit\nabc\n## Head commit\ndef\n## Findings\nnone\n## Verdict\npass\n",
        encoding="utf-8",
    )
    result = run_checks(tmp_path)
    assert any(issue["code"] == "unknown_related_id" and "TASK-999" in issue["message"] for issue in result.issues)


def test_checks_require_complete_standard_scaffold_artifacts(tmp_path: Path):
    init_project(tmp_path)
    missing_paths = (
        "docs/templates/INDEX.md",
        "docs/templates/review.md",
        "docs/operations/runbooks/INDEX.md",
        "docs/operations/incidents/INDEX.md",
        "docs/operations/postmortems/INDEX.md",
    )
    for relative in missing_paths:
        (tmp_path / relative).unlink()
    result = run_checks(tmp_path)
    reported = {issue["path"] for issue in result.issues if issue["code"] == "missing_required_artifact"}
    assert set(missing_paths) <= reported


def test_inspect_git_reports_deterministic_worktrees_and_branch(tmp_path: Path):
    _git(tmp_path, "init", "--quiet")
    _git(tmp_path, "config", "user.email", "test@example.test")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "tracked.txt").write_text("one", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "baseline")

    context = inspect_git(tmp_path)

    assert context.branch
    assert context.head != "unborn"
    assert context.worktrees
    assert context.worktrees == tuple(sorted(context.worktrees, key=lambda item: item["path"]))
    assert Path(context.worktrees[0]["path"]).resolve() == tmp_path.resolve()
