from datetime import date
import re
from .models import RecordMetadata, RecordType, Status

class FrontmatterError(ValueError):
    pass

REQUIRED = ("id", "type", "status", "created", "updated")

def parse_frontmatter(text: str) -> tuple[RecordMetadata, str]:
    opening = re.match(r"^---\r?\n", text)
    if not opening:
        raise FrontmatterError("frontmatter must start with ---")
    closing = re.search(r"^---\r?$", text[opening.end():], re.MULTILINE)
    if not closing:
        raise FrontmatterError("frontmatter closing marker is missing")
    content_end = opening.end() + closing.start()
    body_start = opening.end() + closing.end()
    if text[body_start:body_start + 2] == "\r\n": body_start += 2
    elif text[body_start:body_start + 1] == "\n": body_start += 1
    raw = text[opening.end():content_end].splitlines()
    values: dict[str, object] = {}
    related: list[str] = []
    in_related = False
    for line in raw:
        if not line.strip(): continue
        if line.startswith("  - "):
            if not in_related: raise FrontmatterError("list item outside related")
            related.append(line[4:].strip()); continue
        if ":" not in line: raise FrontmatterError(f"invalid frontmatter line: {line}")
        key, val = line.split(":", 1); key, val = key.strip(), val.strip()
        if key in values or (key == "related" and in_related):
            raise FrontmatterError(f"duplicate field: {key}")
        if key == "related":
            if val: raise FrontmatterError("related must be a YAML list")
            in_related = True; continue
        in_related = False; values[key] = val.strip('"\'')
    missing = [k for k in REQUIRED if k not in values]
    if missing: raise FrontmatterError("missing required fields: " + ", ".join(missing))
    try:
        metadata = RecordMetadata(str(values["id"]), RecordType(str(values["type"])),
            Status(str(values["status"])), date.fromisoformat(str(values["created"])),
            date.fromisoformat(str(values["updated"])), related)
    except (ValueError, TypeError) as exc:
        raise FrontmatterError(str(exc)) from exc
    return metadata, text[body_start:]

def render_frontmatter(metadata: RecordMetadata) -> str:
    lines = ["---"] + [f"{k}: {v}" for k, v in metadata.as_dict().items() if k != "related"]
    lines.append("related:")
    lines.extend(f"  - {item}" for item in metadata.related)
    return "\n".join(lines) + "\n---\n"
