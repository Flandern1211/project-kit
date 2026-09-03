from dataclasses import dataclass
from pathlib import Path
import re
from .frontmatter import parse_frontmatter, FrontmatterError

BASELINE = ('AGENTS.md', 'CONTRIBUTING.md', 'CHANGELOG.md', 'docs/INDEX.md', 'docs/STATUS.md')
@dataclass(frozen=True)
class CheckResult:
    ok: bool
    issues: tuple[dict[str, str], ...]
    checked_files: tuple[str, ...]
    def as_dict(self):
        return {'ok': self.ok, 'issues': [dict(x) for x in self.issues], 'checked_files': list(self.checked_files)}

def run_checks(root: str | Path) -> CheckResult:
    root = Path(root); issues = []; ids = {}
    files = sorted(p for p in root.rglob('*.md') if '.git' not in p.parts)
    for path in files:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding='utf-8')
        if text.startswith('---'):
            id_match = re.search(r'^id:\s*(\S+)', text, re.MULTILINE)
            candidate_id = id_match.group(1) if id_match else None
            try:
                meta, _ = parse_frontmatter(text)
                candidate_id = meta.id
            except FrontmatterError as exc:
                msg = str(exc)
                code = 'invalid_status' if 'is not a valid' in msg or 'status' in msg and 'invalid' in msg else 'invalid_frontmatter'
                issues.append({'code':code,'path':rel,'message':msg})
            if candidate_id:
                if candidate_id in ids: issues.append({'code':'duplicate_id','path':rel,'message':f'duplicate id: {candidate_id}'})
                ids[candidate_id] = rel
            for target in re.findall(r'\[[^]]*\]\(([^)]+)\)', text):
                target = target.split('#',1)[0]
                if target and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                    if not (path.parent / target).exists(): issues.append({'code':'broken_link','path':rel,'message':f'broken link: {target}'})
    for item in BASELINE:
        if not (root/item).exists(): issues.append({'code':'missing_baseline','path':item,'message':f'missing required file: {item}'})
    return CheckResult(not issues, tuple(sorted(issues, key=lambda x:(x['code'],x['path'],x['message']))), tuple(p.relative_to(root).as_posix() for p in files))
