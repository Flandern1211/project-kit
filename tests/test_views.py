from pathlib import Path

import pytest

from project_governance.records import append_activity, create_record, update_indexes
from project_governance.scaffold import init_project


def test_all_record_indexes_link_records_and_board_has_fixed_columns(tmp_path: Path):
    init_project(tmp_path)
    records = [
        ("requirement", "REQ-001", "Requirement"),
        ("design", "DES-001", "Design"),
        ("decision", "ADR-001", "Decision"),
        ("task", "TASK-001", "Task"),
        ("bug", "BUG-001", "Bug"),
        ("review", "REVIEW-001", "Review"),
        ("verification", "VER-001", "Verification"),
    ]
    for kind, record_id, title in records:
        create_record(tmp_path, kind, record_id, title)
    update_indexes(tmp_path)
    for kind, record_id, _ in records:
        index = {
            "requirement": "docs/requirements/INDEX.md", "design": "docs/design/INDEX.md",
            "decision": "docs/decisions/INDEX.md", "task": "docs/work/tasks/INDEX.md",
            "bug": "docs/work/bugs/INDEX.md", "review": "docs/reviews/INDEX.md",
            "verification": "docs/verification/INDEX.md",
        }[kind]
        content = (tmp_path / index).read_text(encoding="utf-8")
        assert f"[{record_id}]" in content
    board = (tmp_path / "docs/work/BOARD.md").read_text(encoding="utf-8")
    assert "| ID | type | status | owner | related | branch/worktree | verification | blocker | next |" in board
    assert all(f"| {record_id} |" in board for _, record_id, _ in records)


def test_workflow_blocked_entry_and_recovery_and_activity_format(tmp_path: Path):
    init_project(tmp_path)
    workflow = (tmp_path / "docs/WORKFLOW.md").read_text(encoding="utf-8")
    assert "active_development --> blocked" in workflow
    assert "blocked --> active_development" in workflow
    activity = append_activity(tmp_path, "agent", "verify", "VER-001", "HEAD", "passed")
    line = activity.read_text(encoding="utf-8").splitlines()[-1]
    assert len(line.split(" | ")) == 6
    assert line.endswith("agent | verify | VER-001 | HEAD | passed")


def test_unmarked_view_refuses_update_and_record_creation_is_atomic(tmp_path: Path):
    init_project(tmp_path)
    view = tmp_path / "docs/reviews/INDEX.md"
    view.write_text("# project-owned\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        create_record(tmp_path, "review", "REVIEW-001", "Review")
    assert not list((tmp_path / "docs/reviews").glob("REVIEW-001-*.md"))
    with pytest.raises(FileExistsError):
        update_indexes(tmp_path)


def test_repeated_index_updates_are_deterministic(tmp_path: Path):
    init_project(tmp_path)
    create_record(tmp_path, "task", "TASK-001", "Task")
    update_indexes(tmp_path)
    first = (tmp_path / "docs/work/tasks/INDEX.md").read_text(encoding="utf-8")
    update_indexes(tmp_path)
    second = (tmp_path / "docs/work/tasks/INDEX.md").read_text(encoding="utf-8")
    assert first == second
    assert first.count("[TASK-001]") == 1


def test_board_populates_task_governance_fields_from_record(tmp_path: Path):
    init_project(tmp_path)
    record = create_record(tmp_path, "task", "TASK-001", "Traceable task", related=["REQ-001"])
    content = record.read_text(encoding="utf-8")
    content = content.replace("## Purpose\n", "## Purpose\nBuild it\n")
    content = content.replace("## Scope\n", "## Scope\nImplement scope\n")
    content = content.replace("## Evidence\n", "## Evidence\npytest -q\n")
    content = content.replace("## Blockers\n", "## Blockers\nnone\n")
    content = content.replace("## Next action\n", "## Next action\nreview\n")
    content = content.replace("## Handoff\n", "## Owner\nagent\n\n## Files\nsrc/app.py\n\n## Git\nbranch: task/TASK-001-traceable\nworktree: .worktrees/TASK-001\nbase_commit: abc\nhead_commit: def\n\n## Handoff\n")
    record.write_text(content, encoding="utf-8")
    update_indexes(tmp_path)

    board = (tmp_path / "docs/work/BOARD.md").read_text(encoding="utf-8")
    assert "| TASK-001 | task | draft | agent | REQ-001 | task/TASK-001-traceable / .worktrees/TASK-001 | pytest -q | none | review |" in board


def test_board_escapes_related_values_without_extra_columns(tmp_path: Path):
    init_project(tmp_path)
    record = create_record(tmp_path, "task", "TASK-001", "Task", related=["REQ-001", "REQ-002"])
    content = record.read_text(encoding="utf-8").replace("  - REQ-001\n", "  - REQ|001\n  - line value\n")
    record.write_text(content, encoding="utf-8")
    update_indexes(tmp_path)
    board = (tmp_path / "docs/work/BOARD.md").read_text(encoding="utf-8")
    row = next(line for line in board.splitlines() if line.startswith("| TASK-001 |"))
    assert "REQ\\|001" in row and "line value" in row


def test_board_evidence_labels_do_not_create_broken_relative_links(tmp_path: Path):
    init_project(tmp_path)
    record = create_record(tmp_path, "task", "TASK-002", "Linked evidence")
    content = record.read_text(encoding="utf-8").replace(
        "## Evidence\n", "## Evidence\nSee [VER-001](../../verification/VER-001.md).\n"
    )
    record.write_text(content, encoding="utf-8")
    update_indexes(tmp_path)
    board = (tmp_path / "docs/work/BOARD.md").read_text(encoding="utf-8")
    assert "[VER-001]" not in board
    assert "See VER-001" in board


def test_activity_rejects_pipe_or_newline_in_fields(tmp_path: Path):
    init_project(tmp_path)
    with pytest.raises(ValueError):
        append_activity(tmp_path, "agent|bad", "verify", "VER-001", "HEAD", "ok")
    with pytest.raises(ValueError):
        append_activity(tmp_path, "agent", "verify\nnext", "VER-001", "HEAD", "ok")


def test_activity_refuses_unmarked_project_owned_file(tmp_path: Path):
    init_project(tmp_path)
    activity = tmp_path / "docs/activity/ACTIVITY.md"
    activity.write_text("# project-owned activity\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        append_activity(tmp_path, "agent", "verify", "VER-001", "HEAD", "ok")
