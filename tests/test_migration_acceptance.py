from pathlib import Path

from project_governance.checks import run_checks
from project_governance.migration import apply_migration, approve_migration, create_migration_plan, scan_project
from project_governance.scaffold import init_project


def test_existing_project_migration_fixture_is_non_destructive(tmp_path: Path):
    project = tmp_path / "existing"
    project.mkdir()
    (project / "docs" / "coding").mkdir(parents=True)
    source = project / "docs" / "coding" / "PRD.md"
    source.write_text("legacy requirements", encoding="utf-8")
    before = source.read_bytes()

    init_project(project, mode="supplement")
    candidates = scan_project(project, scan_roots=["docs/coding"])
    create_migration_plan(project, candidates, migration_id="MIG-001")
    assert not apply_migration(project, "MIG-001").applied
    approve_migration(project, "MIG-001")
    result = apply_migration(project, "MIG-001")

    assert result.applied == ["ITEM-001"]
    assert source.read_bytes() == before
    target = next((project / "docs" / "requirements").glob("REQ-MIG-001-*.md"))
    assert "source_path: docs/coding/PRD.md" in target.read_text(encoding="utf-8")
    assert run_checks(project).ok


def test_non_git_project_keeps_adoption_stage_and_migration_source(tmp_path: Path):
    project = tmp_path / "non-git"
    project.mkdir()
    init_project(project, mode="supplement")

    assert "project_stage: adoption_review" in (project / "docs" / "STATUS.md").read_text(encoding="utf-8")
    assert run_checks(project).ok
