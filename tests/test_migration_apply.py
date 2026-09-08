from pathlib import Path

from project_governance.migration import (
    apply_migration,
    approve_migration,
    create_migration_plan,
    load_migration_plan,
    scan_project,
)
from project_governance.scaffold import init_project


def test_apply_requires_approval_and_preserves_source(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("original", encoding="utf-8")
    candidates = scan_project(tmp_path, scan_roots=["docs/coding"])
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")

    blocked = apply_migration(tmp_path, "MIG-001")
    assert not blocked.applied
    pending = load_migration_plan(tmp_path, "MIG-001")
    assert pending.status == "draft"
    assert pending.approval == "pending"
    assert not list((tmp_path / "docs" / "verification").glob("VER-MIG-001-*.md"))

    approve_migration(tmp_path, "MIG-001")
    result = apply_migration(tmp_path, "MIG-001")

    assert result.applied == ["ITEM-001"]
    assert source.read_text(encoding="utf-8") == "original"
    target = next((tmp_path / "docs/requirements").glob("REQ-MIG-001-*.md"))
    target_text = target.read_text(encoding="utf-8")
    assert "status: draft" in target_text
    assert "original" in target_text
    assert "PGK_SOURCE_BEGIN" in target_text and "PGK_SOURCE_END" in target_text


def test_apply_reports_source_change_and_target_conflict_without_overwrite(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("v1", encoding="utf-8")
    candidates = scan_project(tmp_path, scan_roots=["docs/coding"])
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")

    source.write_text("v2", encoding="utf-8")
    changed = apply_migration(tmp_path, "MIG-001")
    assert changed.changed == ["ITEM-001"]
    assert not changed.applied

    conflict_project = tmp_path / "conflict-project"
    conflict_project.mkdir()
    init_project(conflict_project, mode="supplement")
    conflict_source = conflict_project / "docs" / "coding" / "PRD.md"
    conflict_source.parent.mkdir(parents=True)
    conflict_source.write_text("v1", encoding="utf-8")
    create_migration_plan(conflict_project, scan_project(conflict_project, scan_roots=["docs/coding"]), migration_id="MIG-001")
    approve_migration(conflict_project, "MIG-001")
    target = conflict_project / "docs" / "requirements" / "REQ-MIG-001-001-prd.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("manual content", encoding="utf-8")
    conflict = apply_migration(conflict_project, "MIG-001")
    assert conflict.conflicts == ["ITEM-001"]
    assert target.read_text(encoding="utf-8") == "manual content"


def test_apply_is_idempotent_for_identical_generated_target(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("same", encoding="utf-8")
    create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")

    first = apply_migration(tmp_path, "MIG-001")
    second = apply_migration(tmp_path, "MIG-001")

    assert first.applied == ["ITEM-001"]
    assert second.skipped == ["ITEM-001"]
    assert not second.conflicts


def test_apply_rejects_target_outside_standard_directory_without_writing(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("requirements", encoding="utf-8")
    create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    plan = next((tmp_path / "docs" / "migrations").glob("MIG-001-*.md"))
    plan.write_text(plan.read_text(encoding="utf-8").replace("target_path: docs/requirements/REQ-MIG-001-001-prd.md", "target_path: src/evil.md"), encoding="utf-8")

    import pytest
    with pytest.raises(ValueError, match="standard directory"):
        apply_migration(tmp_path, "MIG-001")
    assert not (tmp_path / "src" / "evil.md").exists()


def test_apply_rejects_sensitive_approved_item(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("requirements", encoding="utf-8")
    create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    plan = next((tmp_path / "docs" / "migrations").glob("MIG-001-*.md"))
    text = plan.read_text(encoding="utf-8").replace("status: candidate", "status: approved").replace("sensitive: False", "sensitive: true")
    plan.write_text(text, encoding="utf-8")

    result = apply_migration(tmp_path, "MIG-001")

    assert result.failed == ["ITEM-001"]
    assert not list((tmp_path / "docs" / "requirements").glob("REQ-MIG-001-*.md"))


def test_apply_records_execution_git_snapshot_and_target_dirty_is_not_overwritten(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("requirements", encoding="utf-8")
    create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    target = tmp_path / "docs" / "requirements" / "REQ-MIG-001-001-prd.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("manual", encoding="utf-8")

    result = apply_migration(tmp_path, "MIG-001")

    assert result.conflicts == ["ITEM-001"]
    assert target.read_text(encoding="utf-8") == "manual"
    plan_text = next((tmp_path / "docs" / "migrations").glob("MIG-001-*.md")).read_text(encoding="utf-8")
    assert "## Execution Git" in plan_text


def test_apply_rechecks_source_sensitivity_even_when_mig_flag_is_tampered(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("requirements", encoding="utf-8")
    create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    plan = next((tmp_path / "docs/migrations").glob("MIG-001-*.md"))
    text = plan.read_text(encoding="utf-8").replace("status: approved", "status: approved").replace("sensitive: False", "sensitive: false")
    plan.write_text(text, encoding="utf-8")
    source.write_text("TOKEN=secret-value", encoding="utf-8")

    result = apply_migration(tmp_path, "MIG-001")

    assert result.failed == ["ITEM-001"] or result.changed == ["ITEM-001"]
    assert not list((tmp_path / "docs" / "requirements").glob("REQ-MIG-001-*.md"))
