from datetime import date
import pytest
from project_governance.frontmatter import FrontmatterError, parse_frontmatter, render_frontmatter
from project_governance.models import RecordMetadata, RecordType, Status
from project_governance.templates import render_record, template_path

def metadata(): return RecordMetadata("TASK-001", RecordType.TASK, Status.IN_PROGRESS, date(2026,9,2), date(2026,9,2), ["REQ-001"])
def test_frontmatter_roundtrip():
    parsed, body = parse_frontmatter(render_frontmatter(metadata()) + "\nhello")
    assert parsed == metadata() and body == "\nhello"
def test_missing_and_duplicate_fields():
    with pytest.raises(FrontmatterError, match="missing"): parse_frontmatter("---\nid: X\n---\n")
    with pytest.raises(FrontmatterError, match="duplicate"): parse_frontmatter("---\nid: X\nid: Y\ntype: task\nstatus: draft\ncreated: 2026-09-02\nupdated: 2026-09-02\n---\n")
def test_render_record(): assert "id: TASK-001" in render_record(metadata(), "# Goal")
def test_template_path_rejects_unknown():
    with pytest.raises(ValueError): template_path("../../secret")
