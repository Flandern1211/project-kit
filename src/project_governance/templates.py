from pathlib import Path
from string import Template
from .frontmatter import render_frontmatter
from .models import RecordMetadata

TYPES = ("requirement", "design", "decision", "task", "bug", "review", "verification", "migration")
def template_path(kind: str, directory: Path | None = None) -> Path:
    if kind not in TYPES: raise ValueError(f"unsupported record type: {kind}")
    base = directory or Path(__file__).with_name("templates")
    candidate = (base / f"{kind}.md").resolve()
    if candidate.parent != base.resolve(): raise ValueError("unsafe template path")
    return candidate

def render_record(metadata: RecordMetadata, body: str = "") -> str:
    return render_frontmatter(metadata) + body.rstrip() + "\n"

def load_template(kind: str, directory: Path | None = None) -> str:
    return template_path(kind, directory).read_text(encoding="utf-8")

def render_template(kind: str, metadata: RecordMetadata, values: dict[str, str] | None = None, directory: Path | None = None) -> str:
    try:
        content = Template(load_template(kind, directory)).substitute(values or {})
    except KeyError as exc:
        raise ValueError(f"missing template variable: {exc.args[0]}") from exc
    return render_record(metadata, content)
