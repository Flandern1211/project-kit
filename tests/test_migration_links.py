from pathlib import Path

from project_governance.migration import apply_migration, approve_migration, create_migration_plan, scan_project
from project_governance.checks import run_checks
from project_governance.scaffold import init_project


def test_migration_rewrites_relative_links_to_migrated_targets(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source_dir = tmp_path / "docs" / "coding"
    source_dir.mkdir(parents=True)
    (source_dir / "PRD.md").write_text("See [design](TSD.md).", encoding="utf-8")
    (source_dir / "TSD.md").write_text("# Design", encoding="utf-8")

    candidates = scan_project(tmp_path, scan_roots=["docs/coding"])
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    result = apply_migration(tmp_path, "MIG-001")

    assert result.applied == ["ITEM-001", "ITEM-002"]
    requirement = (tmp_path / "docs" / "requirements" / "REQ-MIG-001-001-prd.md").read_text(encoding="utf-8")
    assert "../design/DES-MIG-001-002-tsd.md" in requirement
    assert run_checks(tmp_path).ok


def test_migration_rewrites_links_to_preserved_sources_and_keeps_external_links(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source_dir = tmp_path / "docs" / "coding"
    source_dir.mkdir(parents=True)
    (source_dir / "PRD.md").write_text(
        "See [conventions](../project-conventions.md) and [site](https://example.com/a).",
        encoding="utf-8",
    )
    candidates = scan_project(tmp_path, scan_roots=["docs/coding"])
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    result = apply_migration(tmp_path, "MIG-001")

    assert result.applied == ["ITEM-001"]
    requirement = (tmp_path / "docs" / "requirements" / "REQ-MIG-001-001-prd.md").read_text(encoding="utf-8")
    assert "../project-conventions.md" in requirement
    assert "https://example.com/a" in requirement
