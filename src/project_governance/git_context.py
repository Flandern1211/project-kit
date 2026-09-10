from dataclasses import dataclass
import os
from pathlib import Path
import subprocess


class GitInspectionError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


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


def _filesystem_entry_state(path: Path) -> str:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "unreadable"
    return "present"


def _git_inspection_error(root: Path, exc: subprocess.CalledProcessError | OSError) -> GitInspectionError:
    details = " ".join(
        value.strip()
        for value in (getattr(exc, "stdout", ""), getattr(exc, "stderr", ""), str(exc))
        if value and value.strip()
    )
    if isinstance(exc, OSError):
        return GitInspectionError("git_unreadable", f"Git repository is unreadable: {root}; {details or 'inspection failed'}")
    git_metadata = root / ".git"
    if _filesystem_entry_state(root) == "missing" or _filesystem_entry_state(git_metadata) == "missing":
        return GitInspectionError("git_not_initialized", f"Git repository is not initialized: {root}")
    return GitInspectionError("git_unreadable", f"Git repository is unreadable: {root}; {details or 'inspection failed'}")


def inspect_git(root: str | Path, limit: int = 5) -> GitContext:
    root = Path(root)
    try:
        # Check repository existence independently from whether it has commits.
        _git(root, 'rev-parse', '--git-dir')
        # Git otherwise walks up parent directories. The inspected project must
        # itself be the worktree root, not merely a child of another checkout.
        git_root = Path(_git(root, 'rev-parse', '--show-toplevel')).resolve()
        if git_root != root.resolve():
            raise GitInspectionError("git_not_initialized", f"Git repository is not initialized at project root: {root}")
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
    except GitInspectionError:
        raise
    except (subprocess.CalledProcessError, OSError) as exc:
        raise _git_inspection_error(root, exc) from exc


__all__ = ["GitContext", "GitInspectionError", "inspect_git"]
