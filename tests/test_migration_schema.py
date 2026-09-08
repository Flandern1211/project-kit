from pathlib import Path

from project_governance.frontmatter import parse_frontmatter
from project_governance.models import RecordType
from project_governance.records import create_record
from project_governance.scaffold import init_project


def test_migration_record_type_and_directory(tmp_path: Path):
    init_project(tmp_path)

    path = create_record(tmp_path, "migration", "MIG-001", "Initial migration")

    assert path.relative_to(tmp_path).as_posix() == "docs/migrations/MIG-001-initial-migration.md"
    metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    assert metadata.type is RecordType.MIGRATION


def test_supplement_mode_uses_adoption_review_for_missing_status(tmp_path: Path):
    init_project(tmp_path, mode="supplement")

    assert "project_stage: adoption_review" in (tmp_path / "docs/STATUS.md").read_text(encoding="utf-8")


def test_supplement_mode_preserves_existing_status(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    status = docs / "STATUS.md"
    status.write_text("project_stage: maintenance\ncustom: preserve\n", encoding="utf-8")

    init_project(tmp_path, mode="supplement")

    assert status.read_text(encoding="utf-8") == "project_stage: maintenance\ncustom: preserve\n"
