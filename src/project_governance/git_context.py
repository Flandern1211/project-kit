from dataclasses import dataclass
from pathlib import Path
import subprocess

@dataclass(frozen=True)
class GitContext:
    branch: str
    head: str
    dirty: bool
    recent_commits: tuple[str, ...]
    worktrees: tuple[dict[str, str], ...] = ()

def _git(root: Path, *args: str) -> str:
    p = subprocess.run(['git', *args], cwd=root, text=True, capture_output=True, check=True)
    return p.stdout.strip()

def inspect_git(root: str | Path, limit: int = 5) -> GitContext:
    root = Path(root)
    try:
        # Check repository existence independently from whether it has commits.
        _git(root, 'rev-parse', '--git-dir')
        # Git otherwise walks up parent directories. The inspected project must
        # itself be the worktree root, not merely a child of another checkout.
        git_root = Path(_git(root, 'rev-parse', '--show-toplevel')).resolve()
        if git_root != root.resolve():
            raise ValueError(f'not a readable Git repository: {root}')
        branch = _git(root, 'branch', '--show-current') or 'HEAD'
        try:
            head = _git(root, 'rev-parse', 'HEAD')
        except subprocess.CalledProcessError:
            # A freshly initialized repository has an unborn branch and no HEAD.
            head = 'unborn'
        status = _git(root, 'status', '--porcelain')
        try:
            log = _git(root, 'log', f'-{limit}', '--format=%H') if limit else ''
        except subprocess.CalledProcessError:
            log = ''
        worktrees: list[dict[str, str]] = []
        try:
            porcelain = _git(root, 'worktree', 'list', '--porcelain')
            current: dict[str, str] = {}
            for line in porcelain.splitlines():
                if not line.strip():
                    if current:
                        worktrees.append(current)
                        current = {}
                    continue
                key, _, value = line.partition(' ')
                if key == 'worktree':
                    if current:
                        worktrees.append(current)
                        current = {}
                    current['path'] = value
                elif key == 'HEAD':
                    current['head'] = value
                elif key == 'branch':
                    current['branch'] = value.removeprefix('refs/heads/')
                elif key == 'detached':
                    current['branch'] = 'DETACHED'
                elif key == 'bare':
                    current['branch'] = 'BARE'
            if current:
                worktrees.append(current)
            for item in worktrees:
                path = item.get('path')
                if path:
                    try:
                        item['dirty'] = 'true' if _git(Path(path), 'status', '--porcelain') else 'false'
                    except (OSError, subprocess.CalledProcessError):
                        item['dirty'] = 'unknown'
        except subprocess.CalledProcessError:
            worktrees = []
        worktrees.sort(key=lambda item: (item.get('path', ''), item.get('head', ''), item.get('branch', '')))
        return GitContext(branch, head, bool(status), tuple(x for x in log.splitlines() if x), tuple(dict(item) for item in worktrees))
    except (subprocess.CalledProcessError, OSError) as exc:
        raise ValueError(f'not a readable Git repository: {root}') from exc
