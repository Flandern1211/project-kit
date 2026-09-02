from dataclasses import dataclass, field
from pathlib import Path
import tomllib

@dataclass(slots=True)
class ProjectConfig:
    profile: str = "standard"
    docs_dir: str = "docs"
    records_dir: str = "docs/work"
    template_dir: str | None = None
    extra: dict[str, object] = field(default_factory=dict)

def load_config(path: Path) -> ProjectConfig:
    if not path.exists(): return ProjectConfig()
    with path.open("rb") as handle: data = tomllib.load(handle)
    return ProjectConfig(profile=data.get("profile", "standard"), docs_dir=data.get("docs_dir", "docs"),
        records_dir=data.get("records_dir", "docs/work"), template_dir=data.get("template_dir"),
        extra={k:v for k,v in data.items() if k not in {"profile","docs_dir","records_dir","template_dir"}})
