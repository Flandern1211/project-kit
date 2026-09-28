from pathlib import Path
import subprocess

from project_governance.checks import run_checks
from project_governance.migration import (
    apply_migration,
    approve_migration,
    create_migration_plan,
    load_migration_plan,
    scan_project,
)
from project_governance.migration import _render_governance_copy
from project_governance.scaffold import init_project


def test_migration_uses_custom_governance_directory_end_to_end(tmp_path: Path):
    governance_dir = "governance/internal"
    init_project(
        tmp_path,
        mode="supplement",
        visibility="public",
        governance_dir=governance_dir,
    )
    source = tmp_path / "docs/coding/PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("custom-root requirement", encoding="utf-8")

    candidates = scan_project(tmp_path, scan_roots=["docs/coding"])
    plan_path = create_migration_plan(tmp_path, candidates, migration_id="MIG-001")

    assert plan_path == tmp_path / governance_dir / "migrations/MIG-001-migration-plan.md"
    assert not (tmp_path / "docs/migrations").exists()
    assert load_migration_plan(tmp_path, "MIG-001").path == plan_path

    approve_migration(tmp_path, "MIG-001")
    result = apply_migration(tmp_path, "MIG-001")

    target = tmp_path / governance_dir / "requirements/REQ-MIG-001-001-prd.md"
    assert result.applied == ["ITEM-001"]
    assert target.is_file()
    assert list((tmp_path / governance_dir / "verification").glob("VER-MIG-001-*.md"))
    assert not any(
        item.source_path.startswith(governance_dir + "/requirements/")
        or item.source_path.startswith(governance_dir + "/verification/")
        or item.source_path.startswith(governance_dir + "/migrations/")
        for item in scan_project(tmp_path, scan_roots=["."])
    )
    assert run_checks(tmp_path).ok


def test_migration_blocks_dirty_target_even_when_bytes_match_generated_copy(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs/coding/PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("dirty target requirement", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "pgk@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "PGK Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=tmp_path, check=True, capture_output=True)

    candidates = scan_project(tmp_path, scan_roots=["docs/coding"])
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    plan = load_migration_plan(tmp_path, "MIG-001")
    entry = plan.entries[0]
    target = tmp_path / entry.target_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        _render_governance_copy(tmp_path, "MIG-001", entry, source.read_text(encoding="utf-8"), {entry.source_path: entry.target_path}),
        encoding="utf-8",
    )

    result = apply_migration(tmp_path, "MIG-001")

    assert result.conflicts == ["ITEM-001"]
    assert result.skipped == []
    assert load_migration_plan(tmp_path, "MIG-001").status == "blocked"
