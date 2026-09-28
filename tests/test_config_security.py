from pathlib import Path

import pytest

from project_governance.checks import run_checks
from project_governance.config import load_config
from project_governance.records import create_record
from project_governance.scaffold import init_project


@pytest.mark.parametrize(
    "field,value",
    [
        ("governance_dir", "../escape"),
        ("governance_dir", "D:/escape"),
        ("governance_dir", "."),
        ("governance_dir", ""),
        ("governance_dir", "nested/../escape"),
        ("public_docs_dir", "../public-escape"),
        ("public_docs_dir", "D:/public-escape"),
        ("public_docs_dir", "."),
        ("public_docs_dir", ""),
    ],
)
def test_invalid_configured_directory_is_rejected_and_reported(
    tmp_path: Path, field: str, value: str
):
    init_project(tmp_path)
    config = tmp_path / ".project-governance.toml"
    text = config.read_text(encoding="utf-8")
    line = f'{field} = "{value}"'
    import re

    text = re.sub(rf"^{field} = .*?$", line, text, flags=re.MULTILINE)
    config.write_text(text, encoding="utf-8")

    with pytest.raises(ValueError, match=field):
        load_config(config)
    result = run_checks(tmp_path)
    assert any(issue["code"] == "invalid_config" for issue in result.issues)


def test_invalid_governance_directory_blocks_record_write_outside_root(tmp_path: Path):
    init_project(tmp_path)
    config = tmp_path / ".project-governance.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace(
            'governance_dir = "docs"', 'governance_dir = "../escape"'
        ),
        encoding="utf-8",
    )
    outside = tmp_path.parent / "escape"

    with pytest.raises(ValueError, match="governance_dir"):
        create_record(tmp_path, "requirement", "REQ-001", "Escaped")

    assert not (outside / "requirements/REQ-001-escaped.md").exists()
