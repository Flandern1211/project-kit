from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from project_governance.checks import run_checks
from project_governance.scaffold import init_project


FIXTURE = Path(__file__).parent / "fixtures" / "new-project"


def test_fresh_project_fixture_initializes_without_business_requirements(tmp_path: Path, monkeypatch):
    target = tmp_path / "sample-project"
    shutil.copytree(FIXTURE, target)
    existing = (target / "README.txt").read_bytes()
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))

    result = init_project(target, project_name="Sample Project")

    assert result.project_stage == "requirements_discussion"
    assert result.git_state == "git_not_initialized"
    assert (target / "AGENTS.md").is_file()
    assert (target / ".project-governance.toml").is_file()
    assert (target / "README.txt").read_bytes() == existing
    assert not list((target / "docs" / "requirements").glob("REQ-*.md"))
    assert run_checks(target).ok


def test_fresh_project_cli_creates_and_indexes_complete_record_chain(tmp_path: Path, monkeypatch):
    target = tmp_path / "sample-project"
    shutil.copytree(FIXTURE, target)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    env = dict(**__import__("os").environ, PYTHONPATH=str(Path(__file__).parents[1] / "src"))

    init = subprocess.run(
        [sys.executable, "-m", "project_governance", "init", "--root", str(target), "--json"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert init.returncode == 0, init.stderr
    assert json.loads(init.stdout)["project_stage"] == "requirements_discussion"

    records = (
        ("requirement", "REQ-001", "Discuss project requirements", ()),
        ("design", "DES-001", "Record accepted design", ("REQ-001",)),
        ("decision", "ADR-001", "Record governance decision", ("DES-001",)),
        ("task", "TASK-001", "Implement accepted work", ("REQ-001", "DES-001")),
        ("bug", "BUG-001", "Track observed issue", ("TASK-001",)),
        ("review", "REVIEW-001", "Review implementation", ("TASK-001",)),
        ("verification", "VER-001", "Verify baseline", ("TASK-001", "REVIEW-001")),
    )
    for kind, record_id, title, related in records:
        command = [sys.executable, "-m", "project_governance", "new", kind, record_id, title, "--root", str(target)]
        for relation in related:
            command.extend(("--related", relation))
        created = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
        assert created.returncode == 0, created.stderr

    handoff = subprocess.run(
        [
            sys.executable,
            "-m",
            "project_governance",
            "handoff",
            "TASK-001",
            "--root",
            str(target),
            "--status",
            "in_progress",
            "--verification",
            "acceptance fixture",
            "--next-action",
            "run pgk check",
            "--json",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert handoff.returncode == 0, handoff.stderr
    assert json.loads(handoff.stdout)["task_id"] == "TASK-001"

    bug_handoff = subprocess.run(
        [
            sys.executable,
            "-m",
            "project_governance",
            "handoff",
            "BUG-001",
            "--root",
            str(target),
            "--verification",
            "reproduction captured",
            "--next-action",
            "review the fix",
            "--json",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert bug_handoff.returncode == 0, bug_handoff.stderr

    checked = subprocess.run(
        [sys.executable, "-m", "project_governance", "check", "--root", str(target), "--json"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert checked.returncode == 0, checked.stderr
    payload = json.loads(checked.stdout)
    assert payload["ok"] is True
    assert payload["governance"]["ok"] is True
    for _kind, record_id, _title, _related in records:
        record_dir = {
            "REQ": "docs/requirements",
            "DES": "docs/design",
            "ADR": "docs/decisions",
            "TASK": "docs/work/tasks",
            "BUG": "docs/work/bugs",
            "REVIEW": "docs/reviews",
            "VER": "docs/verification",
        }[record_id.split("-", 1)[0]]
        assert list((target / record_dir).glob(f"{record_id}-*.md")), record_id
    assert "[TASK-001]" in (target / "docs/work/tasks/INDEX.md").read_text(encoding="utf-8")
    assert "[VER-001]" in (target / "docs/verification/INDEX.md").read_text(encoding="utf-8")
    task = next((target / "docs/work/tasks").glob("TASK-001-*.md"))
    assert "Next action: run pgk check" in task.read_text(encoding="utf-8")
    bug = next((target / "docs/work/bugs").glob("BUG-001-*.md"))
    bug_text = bug.read_text(encoding="utf-8")
    assert "Next action: review the fix" in bug_text
    assert "Branch:" in bug_text and "HEAD:" in bug_text and "Uncommitted:" in bug_text
