import subprocess
from pathlib import Path

import pytest

from project_governance.handoff import update_handoff
from project_governance.git_context import inspect_git
from project_governance.records import create_record
from project_governance.scaffold import init_project


def test_handoff_updates_only_marked_section_with_git_and_next_action(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    record = create_record(tmp_path, "task", "TASK-201", "Handoff task")
    original = record.read_text(encoding="utf-8")

    updated = update_handoff(
        tmp_path,
        "TASK-201",
        next_action="run the integration suite",
        verification="unit tests: 10 passed",
        blockers=["none"],
    )

    content = updated.read_text(encoding="utf-8")
    assert updated == record
    assert content.startswith(original.split("<!-- PGK_HANDOFF_START -->")[0])
    assert "Branch:" in content
    assert "HEAD:" in content
    assert "Worktree:" in content
    assert "Next action: run the integration suite" in content
    assert "Verification: unit tests: 10 passed" in content
    assert "Blockers: none" in content


def test_task_handoff_contains_complete_resume_fields_and_dry_run(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    record = create_record(tmp_path, "task", "TASK-202", "Complete handoff")
    before = record.read_text(encoding="utf-8")
    update_handoff(
        tmp_path, "TASK-202", next_action="run checks", status="in_progress",
        verification="pytest: passed", blockers=["none"],
        scope=["src/project_governance/cli.py", "tests/test_cli.py"],
        authorization="none",
        dry_run=True,
    )
    assert record.read_text(encoding="utf-8") == before
    update_handoff(
        tmp_path, "TASK-202", next_action="run checks", status="in_progress",
        verification="pytest: passed", blockers=["none"],
        scope=["src/project_governance/cli.py", "tests/test_cli.py"],
        authorization="none",
    )
    content = record.read_text(encoding="utf-8")
    for label in ("Status:", "Current work:", "Completed work:", "Remaining work:", "Branch:",
                  "Worktree:", "HEAD:", "Dirty:", "Uncommitted:", "Verification:",
                  "Blockers:", "Next action:", "Scope:", "Authorization:"):
        assert label in content


def test_bug_handoff_is_supported_and_missing_git_is_explicit(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    record = create_record(tmp_path, "bug", "BUG-202", "Bug handoff")
    update_handoff(
        tmp_path,
        "BUG-202",
        next_action="reproduce",
        verification="not run",
        blockers=["none"],
        scope=["src/bug.py"],
        authorization="none",
        current_work="reproduce the issue",
        completed_work="recorded the report",
        remaining_work="capture the fix and verification",
    )
    content = record.read_text(encoding="utf-8")
    assert "Status: draft" in content
    assert "Branch: unavailable" in content
    assert "Worktree: unavailable (not a Git repository)" in content
    assert "HEAD: unavailable" in content
    for label in ("Current work:", "Completed work:", "Remaining work:", "Dirty:",
                  "Uncommitted:", "Verification:", "Blockers:", "Next action:",
                  "Scope:", "Authorization:"):
        assert label in content


def test_handoff_logs_activity_and_dry_run_does_not(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    record = create_record(tmp_path, "task", "TASK-203", "Activity handoff")
    activity = tmp_path / "docs/activity/ACTIVITY.md"
    before = activity.read_text(encoding="utf-8")
    update_handoff(tmp_path, "TASK-203", next_action="continue", dry_run=True)
    assert activity.read_text(encoding="utf-8") == before
    update_handoff(tmp_path, "TASK-203", next_action="continue")
    lines = activity.read_text(encoding="utf-8").splitlines()
    assert any(" | handoff | TASK-203 | " in line for line in lines)


def test_handoff_rejects_structural_injection_values(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    create_record(tmp_path, "task", "TASK-205", "Safe handoff")
    for kwargs in (
        {"next_action": "bad\n## injected"},
        {"next_action": "bad", "current_work": "<!-- PGK_HANDOFF_END -->"},
        {"next_action": "bad", "scope": ["src/a.py\nmalicious"]},
    ):
        with pytest.raises(ValueError, match="handoff field"):
            update_handoff(tmp_path, "TASK-205", **kwargs)


def test_handoff_preflights_unmarked_activity_without_partial_write(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    record = create_record(tmp_path, "task", "TASK-206", "Atomic handoff")
    activity = tmp_path / "docs/activity/ACTIVITY.md"
    activity.write_text("# project-owned activity\n", encoding="utf-8")
    before = record.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        update_handoff(tmp_path, "TASK-206", next_action="continue")
    assert record.read_text(encoding="utf-8") == before


def test_handoff_refreshes_generated_views_for_task_and_bug_and_dry_run_is_unchanged(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    task = create_record(tmp_path, "task", "TASK-204", "View task", status="in_progress")
    bug = create_record(tmp_path, "bug", "BUG-204", "View bug", status="in_progress")
    for record, owner in ((task, "Alice"), (bug, "Bob")):
        content = record.read_text(encoding="utf-8")
        content = content.replace("## Owner\nN/A", f"## Owner\n{owner}")
        content = content.replace("## Evidence\n", "## Evidence\nold evidence\n")
        content = content.replace("## Blockers\n", "## Blockers\nold blocker\n")
        content = content.replace("## Next action\nN/A", "## Next action\nold next")
        record.write_text(content, encoding="utf-8")

    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_path, check=True)

    board = tmp_path / "docs/work/BOARD.md"
    work_index = tmp_path / "docs/work/INDEX.md"
    activity = tmp_path / "docs/activity/ACTIVITY.md"
    stale_board = "<!-- PGK_GENERATED: board -->\n# stale board\n"
    stale_work_index = "<!-- PGK_GENERATED: work-index -->\n# stale work index\n"
    board.write_text(stale_board, encoding="utf-8")
    work_index.write_text(stale_work_index, encoding="utf-8")
    before_record = task.read_text(encoding="utf-8")
    before_activity = activity.read_text(encoding="utf-8")
    before_board = board.read_text(encoding="utf-8")
    before_work_index = work_index.read_text(encoding="utf-8")

    update_handoff(
        tmp_path,
        "TASK-204",
        status="in_progress",
        verification="pytest: 2 passed",
        blockers=["none"],
        next_action="review task",
        dry_run=True,
    )
    assert task.read_text(encoding="utf-8") == before_record
    assert activity.read_text(encoding="utf-8") == before_activity
    assert board.read_text(encoding="utf-8") == before_board
    assert work_index.read_text(encoding="utf-8") == before_work_index

    context = inspect_git(tmp_path)
    update_handoff(
        tmp_path,
        "TASK-204",
        status="in_progress",
        verification="pytest: 2 passed",
        blockers=["none"],
        next_action="review task",
    )
    update_handoff(
        tmp_path,
        "BUG-204",
        status="in_progress",
        verification="reproduction captured",
        blockers=["fix pending"],
        next_action="review bug",
    )

    board_text = board.read_text(encoding="utf-8")
    assert f"| TASK-204 | task | in_progress | Alice |" in board_text
    assert f"| BUG-204 | bug | in_progress | Bob |" in board_text
    assert f"| TASK-204 | task | in_progress | Alice | N/A | {context.branch} / dirty | pytest: 2 passed | none | review task |" in board_text
    assert f"| BUG-204 | bug | in_progress | Bob | N/A | {context.branch} / dirty | reproduction captured | fix pending | review bug |" in board_text
    work_index_text = work_index.read_text(encoding="utf-8")
    assert "[TASK-204]" in work_index_text
    assert "[BUG-204]" in work_index_text
    events = [line for line in activity.read_text(encoding="utf-8").splitlines() if " | handoff | " in line]
    assert len([line for line in events if " | handoff | TASK-204 | " in line]) == 1
    assert len([line for line in events if " | handoff | BUG-204 | " in line]) == 1
