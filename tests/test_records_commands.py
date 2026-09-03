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


def test_update_work_index_is_deterministic_and_does_not_duplicate_records(tmp_path: Path):
    init_project(tmp_path, project_name="Example")
    create_record(tmp_path, "task", "TASK-002", "Second task")
    create_record(tmp_path, "bug", "BUG-001", "Observed issue")

    index = update_work_index(tmp_path)
    content = index.read_text(encoding="utf-8")

    assert sum(line.startswith("- [TASK-002]") for line in content.splitlines()) == 1
    assert sum(line.startswith("- [BUG-001]") for line in content.splitlines()) == 1
    assert "## Active\n\n- [TASK-002]" in content
    assert "## Bugs\n\n- [BUG-001]" in content
