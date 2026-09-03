from pathlib import Path

from project_governance.handoff import update_handoff
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

