from pathlib import Path

from project_governance.scaffold import adopt_project, init_project


def test_init_creates_standard_profile_and_never_overwrites_existing_files(tmp_path: Path):
    existing = tmp_path / "AGENTS.md"
    existing.write_text("project-owned instructions\n", encoding="utf-8")

    first = init_project(tmp_path, project_name="Example")

    assert "AGENTS.md" in first.skipped
    assert "CONTRIBUTING.md" in first.created
    assert (tmp_path / "docs" / "INDEX.md").is_file()
    assert existing.read_text(encoding="utf-8") == "project-owned instructions\n"

    second = init_project(tmp_path, project_name="Changed")

    assert not second.created
    assert "AGENTS.md" in second.skipped
    assert (tmp_path / "README.md").exists() is False


def test_adopt_is_read_only_and_reports_existing_mappings(tmp_path: Path):
    legacy = tmp_path / "docs" / "coding" / "PRD.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_text("legacy requirements", encoding="utf-8")
    before = legacy.read_bytes()

    report = adopt_project(tmp_path)

    assert report.missing
    assert any(item["path"] == "docs/coding/PRD.md" for item in report.mappings)
    assert legacy.read_bytes() == before

