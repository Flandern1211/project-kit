import json
from pathlib import Path

import pytest

from project_governance.cli import main
from project_governance.records import create_record
from project_governance.scaffold import init_project


def test_cli_init_doctor_and_check_support_json_without_mutating_doctor(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path), "--project-name", "Example", "--json"]) == 0
    capsys.readouterr()

    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert main(["doctor", "--root", str(tmp_path), "--json"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    assert doctor["checks"]["ok"] is True
    assert doctor["git"]["branch"]
    assert before == after
    assert main(["check", "--root", str(tmp_path), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True


def test_cli_new_creates_record_and_reports_errors_as_exit_codes(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path)]) == 0
    capsys.readouterr()

    assert main([
        "new", "task", "TASK-101", "CLI task", "--root", str(tmp_path),
        "--status", "in_progress", "--related", "REQ-001", "--json",
    ]) == 0
    created = json.loads(capsys.readouterr().out)
    assert created["path"].endswith("TASK-101-cli-task.md")

    assert main([
        "new", "task", "TASK-101", "duplicate", "--root", str(tmp_path), "--json",
    ]) == 2
    assert "already exists" in capsys.readouterr().err


def test_record_id_cannot_escape_governance_directory(tmp_path: Path):
    init_project(tmp_path)

    with pytest.raises(ValueError, match="record id"):
        create_record(tmp_path, "task", "../outside", "Unsafe")


def test_check_does_not_report_generated_cache_documents(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path), "--json"]) == 0
    capsys.readouterr()
    cache_doc = tmp_path / ".pytest_cache" / "README.md"
    cache_doc.parent.mkdir()
    cache_doc.write_text("[broken](missing.md)", encoding="utf-8")
    temp_doc = tmp_path / ".pytest-tmp-worker" / "README.md"
    temp_doc.parent.mkdir()
    temp_doc.write_text("[broken](missing.md)", encoding="utf-8")

    assert main(["check", "--root", str(tmp_path), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert not any(path.startswith(".pytest_cache/") for path in result["checked_files"])
    assert not any(path.startswith(".pytest-tmp-worker/") for path in result["checked_files"])
