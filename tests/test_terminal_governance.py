import json
from pathlib import Path
import subprocess

import pytest

from project_governance.checks import run_checks
from project_governance.contracts import literal_file_references
from project_governance.cli import main
from project_governance.records import create_record, transition_record
from project_governance.scaffold import init_project


def _replace(path: Path, replacements: dict[str, str]) -> None:
    content = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        assert old in content
        content = content.replace(old, new)
    path.write_text(content, encoding="utf-8")


def _init_git(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "pgk@example.test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "PGK Test"], cwd=root, check=True)


def _v2_chain(root: Path, *, initialize_git: bool = True) -> tuple[Path, Path]:
    if initialize_git:
        _init_git(root)
    (root / "src").mkdir(exist_ok=True)
    (root / "src/app.py").write_text("value = 1\n", encoding="utf-8")
    create_record(root, "requirement", "REQ-001", "Requirement", status="accepted")
    create_record(root, "design", "DES-001", "Design", status="accepted", related=["REQ-001"])
    task = create_record(
        root, "task", "TASK-001", "Task", status="in_progress", related=["REQ-001", "DES-001"]
    )
    _replace(
        task,
        {
            "## Owner\nN/A": "## Owner\nagent",
            "## Scope\nN/A": "## Scope\nImplement the accepted behavior.",
            "## Files\nN/A": "## Files\n- `src/app.py`",
            "- AC-1: replace with one observable acceptance criterion": "- AC-1: the behavior is observable",
            "## Evidence\n- AC-1: pending": "## Evidence\n- AC-1: See VER-001.",
            "branch: N/A": "branch: task/TASK-001-terminal",
            "worktree: N/A": "worktree: .",
            "base_commit: N/A": "base_commit: HEAD",
            "head_commit: N/A": "head_commit: record-commit",
        },
    )
    verification = create_record(
        root, "verification", "VER-001", "Verification", related=["TASK-001"]
    )
    _replace(
        verification,
        {
            "## Owner\nN/A": "## Owner\nagent",
            "## Scope\n": "## Scope\nVerify TASK-001.\n",
            "## Acceptance\n- AC-1: pending": "## Acceptance\n- AC-1: passed",
            "## Evidence\n- AC-1: pending": "## Evidence\n- AC-1: `pytest tests/test_app.py` passed",
            "## Blockers\n": "## Blockers\nnone\n",
            "## Next action\n": "## Next action\ntransition TASK-001\n",
        },
    )
    return task, verification


def test_transition_rejects_illegal_direct_draft_to_done(tmp_path: Path):
    init_project(tmp_path)
    create_record(tmp_path, "task", "TASK-001", "Task")

    with pytest.raises(ValueError, match="illegal task transition: draft -> done"):
        transition_record(tmp_path, "TASK-001", "done")


def test_terminal_transition_requires_reciprocal_verified_verification(tmp_path: Path):
    init_project(tmp_path)
    task, _verification = _v2_chain(tmp_path)
    transition_record(tmp_path, "TASK-001", "in_review")

    with pytest.raises(ValueError, match="missing_terminal_verification"):
        transition_record(tmp_path, "TASK-001", "verified")

    assert "status: in_review" in task.read_text(encoding="utf-8")


def test_transition_closes_complete_v2_chain_and_refreshes_views(tmp_path: Path):
    init_project(tmp_path)
    task, verification = _v2_chain(tmp_path)

    transition_record(tmp_path, "VER-001", "verified")
    transition_record(tmp_path, "TASK-001", "in_review")
    transition_record(tmp_path, "TASK-001", "verified")

    assert "status: verified" in task.read_text(encoding="utf-8")
    assert "status: verified" in verification.read_text(encoding="utf-8")
    assert "[TASK-001]" in (tmp_path / "docs/work/INDEX.md").read_text(encoding="utf-8")
    assert "TASK-001 | task | verified" in (tmp_path / "docs/work/BOARD.md").read_text(encoding="utf-8")
    assert any(" | transition | TASK-001 | " in line for line in (tmp_path / "docs/activity/ACTIVITY.md").read_text(encoding="utf-8").splitlines())


def test_record_commit_requires_git_and_resolves_after_commit(tmp_path: Path):
    without_git = tmp_path / "without-git"
    without_git.mkdir()
    init_project(without_git)
    task, verification = _v2_chain(without_git, initialize_git=False)
    transition_record(without_git, "VER-001", "verified")
    transition_record(without_git, "TASK-001", "in_review")

    with pytest.raises(ValueError, match="untraceable_head_commit"):
        transition_record(without_git, "TASK-001", "verified")
    assert "status: in_review" in task.read_text(encoding="utf-8")

    with_git = tmp_path / "with-git"
    with_git.mkdir()
    init_project(with_git)
    _task, _verification = _v2_chain(with_git)
    transition_record(with_git, "VER-001", "verified")
    transition_record(with_git, "TASK-001", "in_review")
    transition_record(with_git, "TASK-001", "verified")
    subprocess.run(["git", "add", "."], cwd=with_git, check=True)
    subprocess.run(["git", "commit", "-qm", "close task"], cwd=with_git, check=True)

    assert not any(issue["code"] == "untraceable_head_commit" for issue in run_checks(with_git).issues)


def test_terminal_transition_rejects_unknown_commit_id(tmp_path: Path):
    init_project(tmp_path)
    task, _verification = _v2_chain(tmp_path)
    task.write_text(
        task.read_text(encoding="utf-8").replace(
            "head_commit: record-commit",
            "head_commit: 0123456789abcdef0123456789abcdef01234567",
        ),
        encoding="utf-8",
    )
    transition_record(tmp_path, "VER-001", "verified")
    transition_record(tmp_path, "TASK-001", "in_review")

    with pytest.raises(ValueError, match="untraceable_head_commit"):
        transition_record(tmp_path, "TASK-001", "verified")


def test_strict_terminal_task_requires_verified_review(tmp_path: Path):
    init_project(tmp_path, profile="strict")
    _task, _verification = _v2_chain(tmp_path)
    transition_record(tmp_path, "VER-001", "verified")
    transition_record(tmp_path, "TASK-001", "in_review")

    with pytest.raises(ValueError, match="missing_terminal_review"):
        transition_record(tmp_path, "TASK-001", "verified")

    review = create_record(
        tmp_path,
        "review",
        "REVIEW-001",
        "Review",
        status="in_review",
        related=["TASK-001"],
    )
    _replace(
        review,
        {
            "## Owner\nN/A": "## Owner\nreviewer",
            "## Scope\n": "## Scope\nReview TASK-001.\n",
            "## Acceptance\n": "## Acceptance\nThe task contract is satisfied.\n",
            "## Evidence\n": "## Evidence\nInspected the task diff and VER-001.\n",
            "## Base commit\n": "## Base commit\nHEAD\n",
            "## Head commit\n": "## Head commit\nHEAD\n",
            "## Findings\n": "## Findings\nNo unresolved findings.\n",
            "## Verdict\n": "## Verdict\napproved\n",
        },
    )
    transition_record(tmp_path, "REVIEW-001", "verified")
    transition_record(tmp_path, "TASK-001", "verified")


def test_terminal_verification_requires_acceptance_evidence_mapping(tmp_path: Path):
    init_project(tmp_path)
    _task, verification = _v2_chain(tmp_path)
    content = verification.read_text(encoding="utf-8").replace(
        "- AC-1: `pytest tests/test_app.py` passed", "- AC-1: pending"
    )
    verification.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="unverified_acceptance"):
        transition_record(tmp_path, "VER-001", "verified")


def test_file_contract_ignores_external_and_directory_descriptions():
    body = """## Files
- `src/app.py`
- `docs/optional/`
- external repository `Flandern1211/skills` and `README.zh-CN.md`
"""
    assert literal_file_references(body) == ("src/app.py",)

def test_check_reports_missing_declared_file_and_stale_generated_view(tmp_path: Path):
    init_project(tmp_path)
    task = create_record(tmp_path, "task", "TASK-001", "Task")
    _replace(
        task,
        {
            "## Owner\nN/A": "## Owner\nagent",
            "## Files\nN/A": "## Files\n- `src/missing.py`",
        },
    )

    result = run_checks(tmp_path)
    codes = {issue["code"] for issue in result.issues}

    assert "missing_declared_file" in codes
    assert "stale_generated_view" in codes


def test_check_reports_record_index_marker_at_actual_path(tmp_path: Path):
    init_project(tmp_path)
    index = tmp_path / "docs/work/tasks/INDEX.md"
    index.write_text(index.read_text(encoding="utf-8").replace("<!-- PGK_GENERATED: task-index -->", ""), encoding="utf-8")

    result = run_checks(tmp_path)
    issue = next(issue for issue in result.issues if issue["code"] == "invalid_view_marker")

    assert issue["path"] == "docs/work/tasks/INDEX.md"


def test_create_and_check_reject_status_not_supported_by_record_type(tmp_path: Path):
    init_project(tmp_path)
    with pytest.raises(ValueError, match="requirement does not support status done"):
        create_record(tmp_path, "requirement", "REQ-001", "Requirement", status="done")

    requirement = create_record(tmp_path, "requirement", "REQ-001", "Requirement")
    requirement.write_text(
        requirement.read_text(encoding="utf-8").replace("status: draft", "status: done"),
        encoding="utf-8",
    )

    result = run_checks(tmp_path)

    assert any(issue["code"] == "invalid_status_for_type" for issue in result.issues)


def test_cli_transition_dry_run_success_and_terminal_block(tmp_path: Path, capsys):
    init_project(tmp_path)
    task = create_record(tmp_path, "task", "TASK-001", "Task", status="in_progress")
    tracked = [
        task,
        tmp_path / "docs/work/INDEX.md",
        tmp_path / "docs/work/BOARD.md",
        tmp_path / "docs/activity/ACTIVITY.md",
    ]
    before = {path: path.read_text(encoding="utf-8") for path in tracked}

    assert main([
        "transition", "TASK-001", "in_review", "--root", str(tmp_path), "--dry-run", "--json",
    ]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview == {
        "dry_run": True,
        "id": "TASK-001",
        "path": "docs/work/tasks/TASK-001-task.md",
        "previous_status": "in_progress",
        "status": "in_review",
    }
    assert all(path.read_text(encoding="utf-8") == content for path, content in before.items())

    assert main([
        "transition", "TASK-001", "in_review", "--root", str(tmp_path), "--json",
    ]) == 0
    applied = json.loads(capsys.readouterr().out)
    assert applied["previous_status"] == "in_progress"
    assert applied["status"] == "in_review"
    assert applied["dry_run"] is False
    assert "status: in_review" in task.read_text(encoding="utf-8")

    assert main([
        "transition", "TASK-001", "verified", "--root", str(tmp_path), "--json",
    ]) == 2
    assert "terminal transition blocked" in capsys.readouterr().err
    assert "status: in_review" in task.read_text(encoding="utf-8")


def test_cli_index_dry_run_json_reports_changed_views_without_writing(tmp_path: Path, capsys):
    init_project(tmp_path)
    task = create_record(tmp_path, "task", "TASK-001", "Task")
    _replace(task, {"## Owner\nN/A": "## Owner\nagent"})
    board = tmp_path / "docs/work/BOARD.md"
    before = board.read_text(encoding="utf-8")

    assert main(["index", "--root", str(tmp_path), "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["changed"] == ["docs/work/BOARD.md"]
    assert result["dry_run"] is True
    assert board.read_text(encoding="utf-8") == before
