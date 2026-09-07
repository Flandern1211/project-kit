from dataclasses import dataclass, field
from pathlib import Path
import tomllib

PROFILES = ("lite", "standard", "strict")
COLLABORATION_MODES = ("single-agent", "sequential-agents", "parallel-agents")
V01_COLLABORATION_MODES = ("single-agent", "sequential-agents")
PROFILE_RECORD_TYPES = {
    "lite": frozenset({"requirement", "task", "bug", "verification"}),
    "standard": frozenset({"requirement", "design", "decision", "task", "bug", "review", "verification"}),
    "strict": frozenset({"requirement", "design", "decision", "task", "bug", "review", "verification"}),
}


def validate_profile(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized not in PROFILES:
        raise ValueError(f"unsupported profile: {value}")
    return normalized


def validate_collaboration_mode(value: str, *, v01: bool = False) -> str:
    normalized = str(value).strip().lower()
    allowed = V01_COLLABORATION_MODES if v01 else COLLABORATION_MODES
    if normalized not in allowed:
        raise ValueError(f"unsupported collaboration mode: {value}")
    return normalized


def record_type_enabled(profile: str, record_type: str) -> bool:
    return str(record_type).strip().lower() in PROFILE_RECORD_TYPES[validate_profile(profile)]


@dataclass(slots=True)
class ProjectConfig:
    profile: str = "standard"
    collaboration_mode: str = "single-agent"
    docs_dir: str = "docs"
    records_dir: str = "docs/work"
    template_dir: str | None = None
    extra: dict[str, object] = field(default_factory=dict)

def load_config(path: Path) -> ProjectConfig:
    if not path.exists(): return ProjectConfig()
    with path.open("rb") as handle: data = tomllib.load(handle)
    profile = validate_profile(data.get("profile", "standard"))
    collaboration_mode = validate_collaboration_mode(data.get("collaboration_mode", "single-agent"))
    return ProjectConfig(profile=profile, collaboration_mode=collaboration_mode,
        docs_dir=data.get("docs_dir", "docs"),
        records_dir=data.get("records_dir", "docs/work"), template_dir=data.get("template_dir"),
        extra={k:v for k,v in data.items() if k not in {"profile","collaboration_mode","docs_dir","records_dir","template_dir"}})


__all__ = [
    "COLLABORATION_MODES", "PROFILE_RECORD_TYPES", "PROFILES", "ProjectConfig",
    "V01_COLLABORATION_MODES", "load_config", "record_type_enabled",
    "validate_collaboration_mode", "validate_profile",
]
