from dataclasses import dataclass, field
from pathlib import Path
import tomllib

PROFILES = ("lite", "standard", "strict")
COLLABORATION_MODES = ("single-agent", "sequential-agents", "parallel-agents")
V01_COLLABORATION_MODES = ("single-agent", "sequential-agents")
VISIBILITIES = ("team-private", "hybrid", "public")
PROFILE_RECORD_TYPES = {
    "lite": frozenset({"requirement", "task", "bug", "verification"}),
    "standard": frozenset({"requirement", "design", "decision", "task", "bug", "review", "verification", "migration"}),
    "strict": frozenset({"requirement", "design", "decision", "task", "bug", "review", "verification", "migration"}),
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


def validate_visibility(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized not in VISIBILITIES:
        raise ValueError(f"unsupported visibility: {value}")
    return normalized


def default_visibility_dirs(visibility: str) -> tuple[str, str]:
    visibility = validate_visibility(visibility)
    if visibility == "public":
        return "docs", "docs"
    return ".pgk", "docs/public"


def validate_relative_dir(value: str, *, field: str) -> str:
    normalized = str(value).replace("\\", "/").strip().strip("/")
    if not normalized or normalized in {".", ".."} or normalized.startswith("/") or ":" in normalized or ".." in normalized.split("/"):
        raise ValueError(f"invalid {field}: must be a non-empty relative directory")
    return normalized


def validate_visibility_dirs(visibility: str, governance_dir: str, public_docs_dir: str) -> tuple[str, str]:
    governance_dir = validate_relative_dir(governance_dir, field="governance_dir")
    public_docs_dir = validate_relative_dir(public_docs_dir, field="public_docs_dir")
    if visibility != "public" and (governance_dir == public_docs_dir or governance_dir.startswith(public_docs_dir + "/") or public_docs_dir.startswith(governance_dir + "/")):
        raise ValueError("governance_dir and public_docs_dir must not overlap")
    return governance_dir, public_docs_dir


def record_type_enabled(profile: str, record_type: str) -> bool:
    return str(record_type).strip().lower() in PROFILE_RECORD_TYPES[validate_profile(profile)]


@dataclass(slots=True)
class ProjectConfig:
    profile: str = "standard"
    collaboration_mode: str = "single-agent"
    visibility: str = "public"
    docs_dir: str = "docs"
    records_dir: str = "docs/work"
    template_dir: str | None = None
    governance_dir: str = "docs"
    public_docs_dir: str = "docs"
    scan_roots: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    extra: dict[str, object] = field(default_factory=dict)


def load_config(path: Path) -> ProjectConfig:
    if not path.exists():
        return ProjectConfig()
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    profile = validate_profile(data.get("profile", "standard"))
    collaboration_mode = validate_collaboration_mode(data.get("collaboration_mode", "single-agent"))
    visibility = validate_visibility(data.get("visibility", "public"))
    default_governance, default_public = default_visibility_dirs(visibility)
    scan_roots = data.get("scan_roots", ())
    exclude_patterns = data.get("exclude_patterns", ())
    if isinstance(scan_roots, str):
        scan_roots = (scan_roots,)
    if isinstance(exclude_patterns, str):
        exclude_patterns = (exclude_patterns,)
    known = {"kit_version", "schema_version", "profile", "collaboration_mode", "visibility", "docs_dir", "records_dir", "template_dir", "governance_dir", "public_docs_dir", "scan_roots", "exclude_patterns"}
    return ProjectConfig(
        profile=profile,
        collaboration_mode=collaboration_mode,
        visibility=visibility,
        docs_dir=data.get("docs_dir", "docs"),
        records_dir=data.get("records_dir", "docs/work"),
        template_dir=data.get("template_dir"),
        governance_dir=data.get("governance_dir", default_governance),
        public_docs_dir=data.get("public_docs_dir", default_public),
        scan_roots=tuple(str(item) for item in scan_roots),
        exclude_patterns=tuple(str(item) for item in exclude_patterns),
        extra={k: v for k, v in data.items() if k not in known},
    )


__all__ = [
    "COLLABORATION_MODES", "PROFILE_RECORD_TYPES", "PROFILES", "ProjectConfig", "VISIBILITIES",
    "V01_COLLABORATION_MODES", "load_config", "record_type_enabled", "default_visibility_dirs",
    "validate_collaboration_mode", "validate_profile", "validate_relative_dir", "validate_visibility",
    "validate_visibility_dirs",
]
