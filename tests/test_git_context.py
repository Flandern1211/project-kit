import subprocess
from pathlib import Path
import pytest
from project_governance.git_context import GitInspectionError, inspect_git

def test_inspect_git_reports_branch_head_status_and_commits(tmp_path):
    subprocess.run(['git','init','-q'], cwd=tmp_path, check=True)
    subprocess.run(['git','config','user.email','a@b.test'], cwd=tmp_path, check=True)
    subprocess.run(['git','config','user.name','Test'], cwd=tmp_path, check=True)
    (tmp_path/'a').write_text('x')
    subprocess.run(['git','add','.'], cwd=tmp_path, check=True); subprocess.run(['git','commit','-qm','first'], cwd=tmp_path, check=True)
    (tmp_path/'a').write_text('y')
    c = inspect_git(tmp_path)
    assert c.branch in ('main','master') and len(c.head) == 40 and c.dirty and c.recent_commits


def test_inspect_git_does_not_inherit_parent_repository(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    with pytest.raises(GitInspectionError) as error:
        inspect_git(nested)
    assert error.value.code == "git_not_initialized"


def test_inspect_git_classifies_dubious_ownership_as_unreadable(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(
            128,
            args,
            stderr="fatal: detected dubious ownership in repository at 'project'",
        )

    monkeypatch.setattr("project_governance.git_context.subprocess.run", fail)

    with pytest.raises(GitInspectionError) as error:
        inspect_git(tmp_path)

    assert error.value.code == "git_unreadable"


def test_inspect_git_reports_dirty_linked_worktree(tmp_path):
    subprocess.run(['git', 'init', '-q'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'config', 'user.email', 'a@b.test'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp_path, check=True)
    (tmp_path / 'a').write_text('x')
    subprocess.run(['git', 'add', '.'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'commit', '-qm', 'first'], cwd=tmp_path, check=True)
    linked = tmp_path.parent / (tmp_path.name + '-linked')
    subprocess.run(['git', 'worktree', 'add', '-q', '-b', 'task/linked', str(linked)], cwd=tmp_path, check=True)
    (linked / 'dirty').write_text('changed')

    context = inspect_git(tmp_path)

    linked_entries = [item for item in context.worktrees if Path(item['path']).resolve() == linked.resolve()]
    assert linked_entries and linked_entries[0]['dirty'] == 'true'
