from dataclasses import dataclass
from pathlib import Path
import subprocess

@dataclass(frozen=True)
class GitContext:
    branch: str
    head: str
    dirty: bool
    recent_commits: tuple[str, ...]

def _git(root: Path, *args: str) -> str:
    p = subprocess.run(['git', *args], cwd=root, text=True, capture_output=True, check=True)
    return p.stdout.strip()

def inspect_git(root: str | Path, limit: int = 5) -> GitContext:
    root = Path(root)
    try:
        branch = _git(root, 'branch', '--show-current') or 'HEAD'
        head = _git(root, 'rev-parse', 'HEAD')
        status = _git(root, 'status', '--porcelain')
        log = _git(root, 'log', f'-{limit}', '--format=%H') if limit else ''
        return GitContext(branch, head, bool(status), tuple(x for x in log.splitlines() if x))
    except (subprocess.CalledProcessError, OSError) as exc:
        raise ValueError(f'not a readable Git repository: {root}') from exc
