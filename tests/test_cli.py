import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from project_governance.cli import _parser, main
from project_governance.records import create_record
from project_governance.scaffold import init_project
from project_governance.cli import _check_payload


def test_cli_init_doctor_and_check_support_json_without_mutating_doctor(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path), "--project-name", "Example", "--json"]) == 0
    capsys.readouterr()

    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert main(["doctor", "--root", str(tmp_path), "--json"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    assert doctor["checks"]["ok"] is True
    assert doctor["git"]["branch"]
    assert "worktrees" in doctor["git"]
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


def test_cli_new_supports_review_record(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path)]) == 0
    capsys.readouterr()
    assert main(["new", "review", "REVIEW-001", "Baseline review", "--root", str(tmp_path), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["id"] == "REVIEW-001"
    assert result["path"] == "docs/reviews/REVIEW-001-baseline-review.md"


def test_cli_index_json_refreshes_all_generated_views(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path)]) == 0
    capsys.readouterr()
    assert main(["index", "--root", str(tmp_path), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert set(result["paths"]) == {
        "docs/requirements/INDEX.md", "docs/design/INDEX.md", "docs/decisions/INDEX.md",
        "docs/work/tasks/INDEX.md", "docs/work/bugs/INDEX.md", "docs/reviews/INDEX.md",
        "docs/verification/INDEX.md", "docs/migrations/INDEX.md", "docs/work/BOARD.md", "docs/work/INDEX.md",
    }


def test_cli_check_and_doctor_json_include_governance_and_authorization(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path)]) == 0
    capsys.readouterr()
    assert main(["check", "--root", str(tmp_path), "--json"]) == 0
    checked = json.loads(capsys.readouterr().out)
    assert checked["governance"]["ok"] is True
    assert "authorization" in checked
    assert main(["doctor", "--root", str(tmp_path), "--json"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["governance"]["ok"] is True
    assert "authorization" in doctor


def test_cli_check_reports_version_drift_in_json(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path)]) == 0
    capsys.readouterr()
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "project-governance-kit"\ndynamic = ["version"]\n'
        '[tool.setuptools.dynamic]\nversion = {attr = "project_governance.version.__version__"}\n',
        encoding="utf-8",
    )
    (tmp_path / ".project-governance.toml").write_text(
        (tmp_path / ".project-governance.toml").read_text(encoding="utf-8").replace(
            'kit_version = "0.2.0.dev0"', 'kit_version = "0.1.0.dev0"'
        ),
        encoding="utf-8",
    )

    assert main(["check", "--root", str(tmp_path), "--json"]) == 1
    result = json.loads(capsys.readouterr().out)
    assert any(issue["code"] == "version_drift" for issue in result["issues"])


def test_usage_capability_matrix_lists_every_cli_command():
    parser = _parser()
    choices = next(action.choices for action in parser._actions if action.dest == "command")
    usage = (Path(__file__).parents[1] / "docs/usage.md").read_text(encoding="utf-8")

    for command in choices:
        assert f"`pgk {command}`" in usage


def test_cli_handoff_dry_run_reports_preview_without_writing(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path)]) == 0
    capsys.readouterr()
    assert main(["new", "task", "TASK-301", "Preview", "--root", str(tmp_path)]) == 0
    capsys.readouterr()
    record = next((tmp_path / "docs/work/tasks").glob("TASK-301-*.md"))
    before = record.read_text(encoding="utf-8")
    assert main(["handoff", "TASK-301", "--root", str(tmp_path), "--next-action", "review", "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["dry_run"] is True
    assert "Current work:" in result["preview"]
    assert record.read_text(encoding="utf-8") == before


def test_cli_doctor_json_keeps_git_available_shape(tmp_path: Path, capsys):
    assert main(["init", "--root", str(tmp_path), "--json"]) == 0
    capsys.readouterr()
    assert main(["doctor", "--root", str(tmp_path), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["git"]["available"] is False
    assert {"branch", "head", "dirty", "recent_commits"} <= set(result["git"])


def test_cli_doctor_reports_unreadable_git_and_read_only_preflight(tmp_path: Path, capsys, monkeypatch):
    from project_governance.git_context import GitInspectionError

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "a@b.test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    assert main(["init", "--root", str(tmp_path), "--json"]) == 0
    capsys.readouterr()
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=tmp_path, check=True)

    def unreadable(root):
        raise GitInspectionError("git_unreadable", "Git is unreadable")

    monkeypatch.setattr("project_governance.cli.inspect_git", unreadable)
    monkeypatch.setattr("project_governance.checks.inspect_git", unreadable)

    assert main(["doctor", "--root", str(tmp_path), "--json"]) == 1
    result = json.loads(capsys.readouterr().out)

    assert result["git"]["available"] is False
    assert result["git"]["error_code"] == "git_unreadable"
    codes = {issue["code"] for issue in result["checks"]["issues"]}
    assert "git_unreadable" in codes
    assert "git_not_initialized" not in codes
    assert result["preflight"]["python"]["executable"]
    assert result["preflight"]["pytest"]["available"] is True
    assert result["preflight"]["git"]["readable"] is False
    assert result["preflight"]["git"]["worktree_state"] == "unreadable"
    assert result["preflight"]["repository"]["writable"] is True
    assert result["preflight"]["temporary"]["writable"] is True


def test_cli_doctor_reports_clean_initialized_worktree_preflight(tmp_path: Path, capsys):
    import sys

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "a@b.test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    assert main(["init", "--root", str(tmp_path), "--json"]) == 0
    capsys.readouterr()
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=tmp_path, check=True)

    assert main(["doctor", "--root", str(tmp_path), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["git"]["available"] is True
    assert result["preflight"]["python"]["executable"] == sys.executable
    assert result["preflight"]["pytest"]["available"] is True
    assert result["preflight"]["git"] == {"readable": True, "worktree_state": "clean"}
    assert result["preflight"]["repository"]["writable"] is True
    assert result["preflight"]["temporary"]["writable"] is True


def test_check_payload_does_not_classify_unrelated_code_as_authorization():
    result = SimpleNamespace(
        as_dict=lambda: {
            "ok": False,
            "issues": [{"code": "not_authorization", "path": "x", "message": "x"}],
            "checked_files": [],
        }
    )
    payload = _check_payload(result)
    assert payload["authorization"]["issues"] == []
    assert payload["governance"]["issues"][0]["code"] == "not_authorization"
