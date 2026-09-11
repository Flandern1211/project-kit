from pathlib import Path

import pytest

from project_governance.frontmatter import parse_frontmatter
from project_governance.records import DuplicateRecordError, create_record, update_work_index
from project_governance.scaffold import init_project


def test_create_record_writes_metadata_body_and_rejects_duplicate_id(tmp_path: Path):
    init_project(tmp_path, project_name="Example")

    created = create_record(
        tmp_path,
        "task",
        "TASK-001",
        "Build the first task",
        related=["REQ-001"],
        status="in_progress",
    )

    assert created.relative_to(tmp_path).as_posix() == "docs/work/tasks/TASK-001-build-the-first-task.md"
    metadata, body = parse_frontmatter(created.read_text(encoding="utf-8"))
    assert metadata.id == "TASK-001"
    assert metadata.related == ["REQ-001"]
    assert "## Acceptance" in body
    assert "PGK_HANDOFF_START" in body

    with pytest.raises(DuplicateRecordError, match="TASK-001"):
        create_record(tmp_path, "task", "TASK-001", "Another title")


def test_related_id_cannot_inject_malformed_frontmatter(tmp_path: Path):
    init_project(tmp_path)
    with pytest.raises(ValueError, match="related ids"):
        create_record(tmp_path, "task", "TASK-009", "Unsafe relation", related=["REQ-001\nstatus: accepted"])


def test_update_work_index_is_deterministic_and_does_not_duplicate_records(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    create_record(tmp_path, "task", "TASK-002", "Second task")
    create_record(tmp_path, "task", "TASK-003", "Active task", status="in_progress")
    create_record(tmp_path, "task", "TASK-004", "Completed task", status="verified")
    create_record(tmp_path, "bug", "BUG-001", "Observed issue")

    index = update_work_index(tmp_path)
    content = index.read_text(encoding="utf-8")

    assert sum(line.startswith("- [TASK-002]") for line in content.splitlines()) == 1
    assert sum(line.startswith("- [TASK-003]") for line in content.splitlines()) == 1
    assert sum(line.startswith("- [TASK-004]") for line in content.splitlines()) == 1
    assert sum(line.startswith("- [BUG-001]") for line in content.splitlines()) == 1
    assert "## Active\n\n- [TASK-003]" in content
    assert "## Planned\n\n- [TASK-002]" in content
    assert "## Completed\n\n- [TASK-004]" in content
    active = content.split("## Active\n", 1)[1].split("## Planned\n", 1)[0]
    assert "TASK-004" not in active
    assert "## Bugs\n\n- [BUG-001]" in content


def test_create_record_rejects_unmarked_legacy_work_index_before_writing(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    work_index = tmp_path / "docs/work/INDEX.md"
    work_index.write_text("# project-owned work index\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="INDEX[.]md"):
        create_record(tmp_path, "task", "TASK-003", "Blocked write")

    assert not list((tmp_path / "docs/work/tasks").glob("TASK-003-*.md"))


def test_create_record_appends_activity_but_dry_run_does_not(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    activity = tmp_path / "docs/activity/ACTIVITY.md"
    before = activity.read_text(encoding="utf-8").splitlines()

    create_record(tmp_path, "task", "TASK-003", "Activity task")
    lines = activity.read_text(encoding="utf-8").splitlines()
    created = [line for line in lines if " | create | TASK-003 | " in line]
    assert len(created) == 1
    assert len(created[0].split(" | ")) == 6

    dry_root = tmp_path / "dry-run"
    dry_root.mkdir()
    init_project(dry_root, project_name="Dry run")
    dry_activity = dry_root / "docs/activity/ACTIVITY.md"
    dry_before = dry_activity.read_text(encoding="utf-8")
    create_record(dry_root, "task", "TASK-004", "Dry activity task", dry_run=True)
    assert dry_activity.read_text(encoding="utf-8") == dry_before


def test_create_record_refreshes_legacy_work_index_without_dry_run_mutation(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    work_index = tmp_path / "docs/work/INDEX.md"
    before = work_index.read_text(encoding="utf-8")
    create_record(tmp_path, "task", "TASK-005", "Indexed task")
    assert "[TASK-005]" in work_index.read_text(encoding="utf-8")

    dry_root = tmp_path / "dry-index"
    dry_root.mkdir()
    init_project(dry_root, project_name="Dry index")
    dry_index = dry_root / "docs/work/INDEX.md"
    dry_before = dry_index.read_text(encoding="utf-8")
    create_record(dry_root, "task", "TASK-006", "Preview task", dry_run=True)
    assert dry_index.read_text(encoding="utf-8") == dry_before
