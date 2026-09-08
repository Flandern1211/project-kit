from pathlib import Path

from project_governance.migration import scan_project
from project_governance.scaffold import init_project


def test_scan_classifies_supported_files_and_excludes_generated_or_sensitive_files(tmp_path: Path):
    (tmp_path / "docs" / "coding").mkdir(parents=True)
    (tmp_path / "docs" / "coding" / "PRD.md").write_text("requirements", encoding="utf-8")
    (tmp_path / "docs" / "notes.txt").write_text("notes", encoding="utf-8")
    (tmp_path / "docs" / "secret.env").write_text("TOKEN=do-not-report", encoding="utf-8")
    (tmp_path / "docs" / "requirements").mkdir(parents=True)
    (tmp_path / "docs" / "requirements" / "REQ-001.md").write_text("generated", encoding="utf-8")

    candidates = scan_project(tmp_path, scan_roots=["docs/coding", "docs/notes.txt", "docs/secret.env"])
    by_path = {item.source_path: item for item in candidates}

    assert by_path["docs/coding/PRD.md"].suggested_type == "requirement"
    assert by_path["docs/coding/PRD.md"].confidence == "high"
    assert by_path["docs/notes.txt"].suggested_type is None
    assert by_path["docs/secret.env"].sensitive is True
    assert by_path["docs/secret.env"].status == "needs_review"
    assert not any(item.source_path.endswith("REQ-001.md") for item in candidates)


def test_scan_is_deterministic_and_hashes_source_bytes(tmp_path: Path):
    document = tmp_path / "README.md"
    document.write_text("hello", encoding="utf-8")

    first = scan_project(tmp_path, scan_roots=["README.md"])
    second = scan_project(tmp_path, scan_roots=["README.md"])

    assert first == second
    assert len(first[0].source_hash) == 64


def test_scan_rejects_paths_outside_project_root(tmp_path: Path):
    outside = tmp_path.parent / "outside.md"
    outside.write_text("outside", encoding="utf-8")

    try:
        scan_project(tmp_path, scan_roots=[str(outside)])
    except ValueError as exc:
        assert "inside project root" in str(exc)
    else:
        raise AssertionError("scan must reject paths outside the project root")


def test_scan_excludes_generated_governance_documents_after_init(tmp_path: Path):
    init_project(tmp_path)
    candidates = scan_project(tmp_path)

    assert not any(item.source_path.startswith("docs/requirements/") for item in candidates)
    assert not any(item.source_path.startswith("docs/migrations/") for item in candidates)


def test_scan_reports_sensitive_files_without_exposing_content(tmp_path: Path):
    secret = tmp_path / "docs" / "api-token.txt"
    secret.parent.mkdir(parents=True)
    secret.write_text("TOKEN=must-not-be-copied", encoding="utf-8")

    candidates = scan_project(tmp_path, scan_roots=["docs"])

    item = next(item for item in candidates if item.source_path == "docs/api-token.txt")
    assert item.sensitive is True
    assert item.status == "needs_review"
    assert item.suggested_type is None
    assert "must-not-be-copied" not in str(item.as_dict())


def test_scan_does_not_exclude_project_because_ancestor_is_named_temp(tmp_path: Path):
    project = tmp_path / "Temp" / "existing-project"
    project.mkdir(parents=True)
    (project / "README.md").write_text("read me", encoding="utf-8")

    candidates = scan_project(project)

    assert any(item.source_path == "README.md" for item in candidates)
