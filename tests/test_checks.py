import json
from pathlib import Path
from project_governance.checks import run_checks

def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding='utf-8')

def test_checks_find_duplicate_invalid_status_broken_link_and_missing_baseline(tmp_path):
    write(tmp_path/'docs'/'a.md', '---\nid: X\ntype: task\nstatus: nope\ncreated: 2026-09-02\nupdated: 2026-09-02\n---\n[bad](missing.md)')
    write(tmp_path/'docs'/'b.md', '---\nid: X\ntype: task\nstatus: draft\ncreated: 2026-09-02\nupdated: 2026-09-02\n---\n')
    result = run_checks(tmp_path)
    assert not result.ok
    codes = {x['code'] for x in result.issues}
    assert {'duplicate_id', 'invalid_status', 'broken_link', 'missing_baseline'} <= codes
    json.dumps(result.as_dict(), sort_keys=True)

def test_checks_clean_fixture(tmp_path):
    from project_governance.scaffold import init_project
    init_project(tmp_path)
    write(tmp_path/'docs'/'a.md', '[ok](../AGENTS.md)')
    assert run_checks(tmp_path).ok


def test_checks_report_project_version_drift(tmp_path):
    from project_governance.scaffold import init_project

    init_project(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "project-governance-kit"\nversion = "0.2.0.dev0"\n',
        encoding="utf-8",
    )
    (tmp_path / ".project-governance.toml").write_text(
        'kit_version = "0.1.0.dev0"\nprofile = "standard"\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "Current version is `0.1.0.dev0`.\n",
        encoding="utf-8",
    )

    result = run_checks(tmp_path)

    assert not result.ok
    assert any(issue["code"] == "version_drift" for issue in result.issues)


def test_checks_do_not_compare_business_version_with_kit_version(tmp_path):
    from project_governance.scaffold import init_project

    init_project(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "business-app"\nversion = "9.4.1"\n',
        encoding="utf-8",
    )
    config = tmp_path / ".project-governance.toml"
    config.write_text(config.read_text(encoding="utf-8") + 'plugin_option = "enabled"\n', encoding="utf-8")

    assert run_checks(tmp_path).ok


def test_checks_report_unknown_project_kit_config_fields(tmp_path):
    from project_governance.scaffold import init_project

    init_project(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "project-governance-kit"\ndynamic = ["version"]\n'
        '[tool.setuptools.dynamic]\nversion = {attr = "project_governance.version.__version__"}\n',
        encoding="utf-8",
    )
    config = tmp_path / ".project-governance.toml"
    config.write_text(config.read_text(encoding="utf-8") + 'docs_root = "docs"\n', encoding="utf-8")

    result = run_checks(tmp_path)

    assert any(issue["code"] == "unknown_config_field" for issue in result.issues)

def test_checks_find_broken_links_in_plain_markdown_and_ignores_git_and_temp(tmp_path):
    for name in ('AGENTS.md','README.md','.gitignore','.project-governance.toml','CONTRIBUTING.md','CHANGELOG.md','docs/INDEX.md','docs/STATUS.md'):
        write(tmp_path/name, '[bad](missing.md)')
    write(tmp_path/'.git'/'hidden.md', '[bad](missing.md)')
    write(tmp_path/'.pytest-tmp'/'hidden.md', '[bad](missing.md)')
    result = run_checks(tmp_path)
    assert sum(i['code'] == 'broken_link' for i in result.issues) == 6


def test_strict_control_document_rejects_lifecycle_frontmatter(tmp_path):
    from project_governance.scaffold import init_project

    init_project(tmp_path, profile="strict")
    write(
        tmp_path / "docs" / "risk" / "RISK-001.md",
        "---\nid: RISK-001\ntype: risk\nstatus: draft\ncreated: 2026-09-10\nupdated: 2026-09-10\nrelated:\n---\n# Risk\n",
    )

    result = run_checks(tmp_path)

    assert not result.ok
    issues = [issue for issue in result.issues if issue["path"] == "docs/risk/RISK-001.md"]
    assert [issue["code"] for issue in issues] == ["unsupported_control_record_type"]
    assert "ordinary Markdown" in issues[0]["message"]
    assert "do not add a new RecordType" in issues[0]["message"]


def test_checks_distinguish_unreadable_git_from_uninitialized_git(tmp_path, monkeypatch):
    from project_governance.git_context import GitInspectionError
    from project_governance.scaffold import init_project

    init_project(tmp_path)
    write(
        tmp_path / "docs" / "work" / "tasks" / "TASK-001.md",
        "---\nid: TASK-001\ntype: task\nstatus: in_progress\ncreated: 2026-09-10\nupdated: 2026-09-10\nrelated:\n---\n# Task\n",
    )
    monkeypatch.setattr(
        "project_governance.checks.inspect_git",
        lambda root: (_ for _ in ()).throw(GitInspectionError("git_unreadable", "Git is unreadable")),
    )

    result = run_checks(tmp_path)
    codes = {issue["code"] for issue in result.issues}

    assert "git_unreadable" in codes
    assert "git_not_initialized" not in codes
    assert "git_state_mismatch" not in codes
