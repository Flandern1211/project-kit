from pathlib import Path

from project_governance.migration import (
    MigrationCandidate,
    approve_migration,
    create_migration_plan,
    load_migration_plan,
    scan_project,
)
from project_governance.scaffold import init_project


def test_plan_has_stable_targets_and_does_not_write_on_dry_run(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (
        MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "filename hint", False, None),
    )

    path = create_migration_plan(tmp_path, candidates, migration_id="MIG-001", dry_run=True)

    assert path.as_posix().endswith("docs/migrations/MIG-001-migration-plan.md")
    assert not path.exists()


def test_plan_loads_stable_items_and_approval_changes_only_selected_items(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (
        MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "hint", False, None),
        MigrationCandidate("docs/notes.txt", "b" * 64, "text", None, "low", "no hint", False, None),
    )
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")

    before = load_migration_plan(tmp_path, "MIG-001")
    assert [entry.item_id for entry in before.entries] == ["ITEM-001", "ITEM-002"]
    assert before.entries[0].target_id == "REQ-MIG-001-001"
    assert before.entries[1].status == "needs_review"

    approve_migration(tmp_path, "MIG-001", item_ids=["ITEM-001"])
    after = load_migration_plan(tmp_path, "MIG-001")
    assert after.entries[0].status == "approved"
    assert after.entries[1].status == "needs_review"
    assert after.approval == "approved"


def test_exclude_item_marks_only_candidate_as_excluded(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "hint", False, None),)
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")

    approve_migration(tmp_path, "MIG-001", exclude_item_ids=["ITEM-001"])

    plan = load_migration_plan(tmp_path, "MIG-001")
    assert plan.entries[0].status == "excluded"
    assert plan.approval == "pending"


def test_auto_migration_ids_advance_without_reusing_mig_001(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "hint", False, None),)

    first = create_migration_plan(tmp_path, candidates)
    second = create_migration_plan(tmp_path, candidates)

    assert first.name.startswith("MIG-001-")
    assert second.name.startswith("MIG-002-")


def test_approve_can_retry_failed_item_after_manual_review(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "hint", False, None),)
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    plan = next((tmp_path / "docs/migrations").glob("MIG-001-*.md"))
    plan.write_text(plan.read_text(encoding="utf-8").replace("status: candidate", "status: failed"), encoding="utf-8")

    approve_migration(tmp_path, "MIG-001", item_ids=["ITEM-001"])

    assert load_migration_plan(tmp_path, "MIG-001").entries[0].status == "approved"


def test_reapproving_source_changed_item_refreshes_source_hash(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("v1", encoding="utf-8")
    create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    source.write_text("v2", encoding="utf-8")
    from project_governance.migration import apply_migration
    assert apply_migration(tmp_path, "MIG-001").changed == ["ITEM-001"]

    approve_migration(tmp_path, "MIG-001", item_ids=["ITEM-001"])

    plan = load_migration_plan(tmp_path, "MIG-001")
    assert plan.entries[0].status == "approved"
    assert plan.entries[0].source_hash != "a" * 64


def test_migration_plan_contains_source_root_and_git_snapshot_fields(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("requirements", encoding="utf-8")

    path = create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    text = path.read_text(encoding="utf-8")

    assert "source_root: ." in text
    assert "## Git" in text
    assert "branch:" in text and "head:" in text and "dirty:" in text


def test_migration_plan_rejects_mismatched_item_id_and_invalid_hash(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "hint", False, None),)
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    plan = next((tmp_path / "docs/migrations").glob("MIG-001-*.md"))
    text = plan.read_text(encoding="utf-8").replace("item_id: ITEM-001", "item_id: BAD").replace("source_hash: " + "a" * 64, "source_hash: bad")
    plan.write_text(text, encoding="utf-8")

    import pytest
    with pytest.raises(ValueError, match="item_id|source metadata"):
        load_migration_plan(tmp_path, "MIG-001")


def test_migration_plan_rejects_target_path_that_does_not_match_target_id(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "hint", False, None),)
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    plan = next((tmp_path / "docs/migrations").glob("MIG-001-*.md"))
    text = plan.read_text(encoding="utf-8").replace("REQ-MIG-001-001-readme.md", "REQ-MIG-001-001-other.md")
    plan.write_text(text, encoding="utf-8")

    import pytest
    with pytest.raises(ValueError, match="target path"):
        load_migration_plan(tmp_path, "MIG-001")


def test_load_rejects_glob_like_migration_id(tmp_path: Path):
    init_project(tmp_path, mode="supplement")

    import pytest
    with pytest.raises(ValueError, match="migration id"):
        load_migration_plan(tmp_path, "MIG-*")
