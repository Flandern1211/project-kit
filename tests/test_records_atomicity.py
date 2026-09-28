from pathlib import Path

import pytest

import project_governance.records as records_module
from project_governance.handoff import update_handoff
from project_governance.records import create_record, update_indexes
from project_governance.scaffold import init_project


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def _fail_on_second_replace(monkeypatch: pytest.MonkeyPatch):
    original = records_module._replace_path
    calls = {"count": 0}

    def replace(source: Path, target: Path) -> None:
        calls["count"] += 1
        if calls["count"] == 2:
            raise OSError("injected replacement failure")
        original(source, target)

    monkeypatch.setattr(records_module, "_replace_path", replace)


def test_create_record_failure_is_all_or_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    init_project(tmp_path)
    before = _snapshot(tmp_path)
    _fail_on_second_replace(monkeypatch)

    with pytest.raises(OSError, match="injected replacement failure"):
        create_record(tmp_path, "requirement", "REQ-001", "Requirement")

    assert _snapshot(tmp_path) == before
    assert not list(tmp_path.rglob("*.pgk-tmp"))
    assert not list(tmp_path.rglob("*.pgk-backup"))


def test_index_refresh_failure_is_all_or_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    init_project(tmp_path)
    record = create_record(tmp_path, "requirement", "REQ-001", "Requirement")
    record.write_text(record.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
    before = _snapshot(tmp_path)
    _fail_on_second_replace(monkeypatch)

    with pytest.raises(OSError, match="injected replacement failure"):
        update_indexes(tmp_path)

    assert _snapshot(tmp_path) == before
    assert not list(tmp_path.rglob("*.pgk-tmp"))
    assert not list(tmp_path.rglob("*.pgk-backup"))


def test_handoff_failure_is_all_or_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    init_project(tmp_path)
    create_record(tmp_path, "task", "TASK-001", "Task")
    before = _snapshot(tmp_path)
    _fail_on_second_replace(monkeypatch)

    with pytest.raises(OSError, match="injected replacement failure"):
        update_handoff(tmp_path, "TASK-001", next_action="continue work")

    assert _snapshot(tmp_path) == before
    assert not list(tmp_path.rglob("*.pgk-tmp"))
    assert not list(tmp_path.rglob("*.pgk-backup"))
