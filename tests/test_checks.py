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

def test_checks_find_broken_links_in_plain_markdown_and_ignores_git_and_temp(tmp_path):
    for name in ('AGENTS.md','README.md','.gitignore','.project-governance.toml','CONTRIBUTING.md','CHANGELOG.md','docs/INDEX.md','docs/STATUS.md'):
        write(tmp_path/name, '[bad](missing.md)')
    write(tmp_path/'.git'/'hidden.md', '[bad](missing.md)')
    write(tmp_path/'.pytest-tmp'/'hidden.md', '[bad](missing.md)')
    result = run_checks(tmp_path)
    assert sum(i['code'] == 'broken_link' for i in result.issues) == 6
