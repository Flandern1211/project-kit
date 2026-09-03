import subprocess
from project_governance.git_context import inspect_git

def test_inspect_git_reports_branch_head_status_and_commits(tmp_path):
    subprocess.run(['git','init','-q'], cwd=tmp_path, check=True)
    subprocess.run(['git','config','user.email','a@b.test'], cwd=tmp_path, check=True)
    subprocess.run(['git','config','user.name','Test'], cwd=tmp_path, check=True)
    (tmp_path/'a').write_text('x')
    subprocess.run(['git','add','.'], cwd=tmp_path, check=True); subprocess.run(['git','commit','-qm','first'], cwd=tmp_path, check=True)
    (tmp_path/'a').write_text('y')
    c = inspect_git(tmp_path)
    assert c.branch in ('main','master') and len(c.head) == 40 and c.dirty and c.recent_commits
