import json
from pathlib import Path

import pytest

from project_governance import upgrade as upgrade_module
from project_governance.cli import main
from project_governance.scaffold import init_project


def _legacy_project(root: Path, *, visibility: str = "public") -> None:
    init_project(root, profile="standard", visibility=visibility)
    config = root / ".project-governance.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace("0.2.0.dev1", "0.2.0.dev0"),
        encoding="utf-8",
    )
    rendered = upgrade_module._render_targets(root)
    for path, target in rendered.items():
        if not path.exists():
            continue
        if path.name == "WORKFLOW.md":
            path.write_text(upgrade_module._legacy_workflow(target), encoding="utf-8")
        elif path.name == "project-conventions.md":
            path.write_text(upgrade_module._legacy_conventions(target), encoding="utf-8")
        elif path.parent.name == "templates" and path.name in {"task.md", "bug.md", "verification.md"}:
            path.write_text(upgrade_module._legacy_template(target, path.stem), encoding="utf-8")
    agents = root / "AGENTS.md"
    agents.write_text(
        upgrade_module._legacy_agents(rendered[agents])
        + "\n## 文档语言\n\n项目自定义章节必须保留。\n",
        encoding="utf-8",
    )


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def test_upgrade_preview_is_read_only_and_reports_diffs(tmp_path: Path):
    _legacy_project(tmp_path)
    before = _snapshot(tmp_path)

    result = upgrade_module.upgrade_project(tmp_path)

    assert result.ok
    assert result.dry_run is True
    assert result.applied is False
    assert ".project-governance.toml" in result.changed
    assert any(item["path"] == "AGENTS.md" for item in result.changes)
    assert all("before_hash" in item and "after_hash" in item and "diff" in item for item in result.changes)
    assert _snapshot(tmp_path) == before


def test_upgrade_apply_preserves_custom_sections_history_and_writes_version_last(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _legacy_project(tmp_path)
    workflow = tmp_path / "docs/WORKFLOW.md"
    workflow.write_text(workflow.read_text(encoding="utf-8") + "\n## Local workflow\n\nKeep this policy.\n", encoding="utf-8")
    conventions = tmp_path / "docs/project-conventions.md"
    conventions.write_text(conventions.read_text(encoding="utf-8") + "\n## Local convention\n\nKeep this convention.\n", encoding="utf-8")
    history = tmp_path / "docs/requirements/REQ-OLD.md"
    history.write_text(
        "---\nid: REQ-OLD\ntype: requirement\nstatus: accepted\ncreated: 2026-01-01\nupdated: 2026-01-01\nrelated:\n---\n# Historical\n",
        encoding="utf-8",
    )
    history_before = history.read_bytes()
    original_write = upgrade_module._atomic_write
    write_order: list[str] = []

    def track_write(path: Path, text: str) -> None:
        write_order.append(path.relative_to(tmp_path).as_posix())
        original_write(path, text)

    monkeypatch.setattr(upgrade_module, "_atomic_write", track_write)

    result = upgrade_module.upgrade_project(tmp_path, apply=True)

    assert result.ok
    assert result.applied is True
    assert (tmp_path / ".project-governance.toml").read_text(encoding="utf-8").startswith('kit_version = "0.2.0.dev1"')
    assert "## Task execution and closure" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "## 文档语言" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "## Local workflow" in workflow.read_text(encoding="utf-8")
    assert "## Local convention" in conventions.read_text(encoding="utf-8")
    assert history.read_bytes() == history_before
    assert "| pgk | upgrade |" in (tmp_path / "docs/activity/ACTIVITY.md").read_text(encoding="utf-8")
    assert write_order[-1] == ".project-governance.toml"

    second = upgrade_module.upgrade_project(tmp_path)
    assert second.ok
    assert second.changed == ()


def test_customized_template_causes_zero_writes(tmp_path: Path):
    _legacy_project(tmp_path)
    template = tmp_path / "docs/templates/task.md"
    template.write_text(template.read_text(encoding="utf-8") + "\nProject customization\n", encoding="utf-8")
    before = _snapshot(tmp_path)

    result = upgrade_module.upgrade_project(tmp_path, apply=True)

    assert not result.ok
    assert any(item["path"] == "docs/templates/task.md" for item in result.conflicts)
    assert _snapshot(tmp_path) == before


def test_unsupported_version_is_rejected_without_writes(tmp_path: Path):
    _legacy_project(tmp_path)
    config = tmp_path / ".project-governance.toml"
    config.write_text(config.read_text(encoding="utf-8").replace("0.2.0.dev0", "9.9.9"), encoding="utf-8")
    before = _snapshot(tmp_path)

    with pytest.raises(upgrade_module.UnsupportedUpgradeError):
        upgrade_module.upgrade_project(tmp_path, apply=True)

    assert _snapshot(tmp_path) == before


def test_upgrade_rolls_back_when_a_later_atomic_write_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _legacy_project(tmp_path)
    before = _snapshot(tmp_path)
    original = upgrade_module._atomic_write
    failed = {"done": False}

    def fail_on_templates(path: Path, text: str) -> None:
        if path.name == "task.md" and not failed["done"]:
            failed["done"] = True
            raise OSError("injected write failure")
        original(path, text)

    monkeypatch.setattr(upgrade_module, "_atomic_write", fail_on_templates)
    result = upgrade_module.upgrade_project(tmp_path, apply=True)

    assert not result.ok
    assert any(item["path"] == "apply" for item in result.conflicts)
    assert _snapshot(tmp_path) == before


def test_team_private_upgrade_uses_governance_directory(tmp_path: Path):
    _legacy_project(tmp_path, visibility="team-private")

    result = upgrade_module.upgrade_project(tmp_path, apply=True)

    assert result.ok
    assert (tmp_path / ".pgk/WORKFLOW.md").exists()
    assert (tmp_path / ".pgk/templates/task.md").read_text(encoding="utf-8").find("terminal-v2") >= 0
    assert ".pgk/WORKFLOW.md" in result.changed


def test_cli_upgrade_json_and_conflict_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    _legacy_project(tmp_path)
    assert main(["upgrade", "--root", str(tmp_path), "--dry-run", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["dry_run"] is True
    assert payload["applied"] is False
    assert "changes" in payload

    (tmp_path / "docs/templates/task.md").write_text(
        (tmp_path / "docs/templates/task.md").read_text(encoding="utf-8") + "\ncustom\n",
        encoding="utf-8",
    )
    assert main(["upgrade", "--root", str(tmp_path), "--apply", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["conflicts"]
