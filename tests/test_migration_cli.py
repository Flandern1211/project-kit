import json
from pathlib import Path

from project_governance.checks import run_checks
from project_governance.cli import main
from project_governance.migration import approve_migration, create_migration_plan, scan_project
from project_governance.scaffold import init_project


def test_cli_migrate_plan_approve_apply_flow(tmp_path: Path, capsys):
    tmp_path.mkdir(exist_ok=True)
    assert main(["init", "--root", str(tmp_path), "--mode", "supplement"]) == 0
    capsys.readouterr()
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("requirements", encoding="utf-8")

    assert main(["migrate", "plan", "--root", str(tmp_path), "--scan-root", "docs/coding", "--json"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["migration_id"] == "MIG-001"
    assert main(["migrate", "apply", "MIG-001", "--root", str(tmp_path), "--json"]) == 0
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["applied"] == []
    assert main(["migrate", "approve", "MIG-001", "--root", str(tmp_path), "--json"]) == 0
    capsys.readouterr()
    assert main(["migrate", "apply", "MIG-001", "--root", str(tmp_path), "--json"]) == 0
    applied = json.loads(capsys.readouterr().out)
    assert applied["applied"]


def test_cli_migrate_plan_dry_run_does_not_write(tmp_path: Path, capsys):
    tmp_path.mkdir(exist_ok=True)
    init_project(tmp_path, mode="supplement")
    capsys.readouterr()
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    assert main(["migrate", "plan", "--root", str(tmp_path), "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    assert result["dry_run"] is True
    assert before == after


def test_checks_accept_adoption_review_and_report_changed_migration_source(tmp_path: Path):
    tmp_path.mkdir(exist_ok=True)
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("v1", encoding="utf-8")
    create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    source.write_text("v2", encoding="utf-8")

    result = run_checks(tmp_path)

    assert not any(issue["code"] == "invalid_project_stage" for issue in result.issues)
    assert any(issue["code"] == "migration_source_changed" for issue in result.issues)


def test_checks_report_approved_target_conflict(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "docs" / "coding" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("v1", encoding="utf-8")
    create_migration_plan(tmp_path, scan_project(tmp_path, scan_roots=["docs/coding"]), migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    target = tmp_path / "docs" / "requirements" / "REQ-MIG-001-001-prd.md"
    target.write_text("manual", encoding="utf-8")

    result = run_checks(tmp_path)

    assert any(issue["code"] == "migration_target_conflict" for issue in result.issues)
