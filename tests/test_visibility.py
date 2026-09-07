from pathlib import Path

import pytest

from project_governance.checks import run_checks
from project_governance.config import load_config
from project_governance.records import create_record
from project_governance.scaffold import init_project


def test_team_private_initializes_governance_in_pgk_for_private_repo(tmp_path: Path):
    result = init_project(tmp_path, visibility="team-private")

    assert result.visibility == "team-private"
    assert result.governance_dir == ".pgk"
    assert (tmp_path / ".pgk/INDEX.md").is_file()
    assert (tmp_path / ".pgk/requirements/INDEX.md").is_file()
    assert not (tmp_path / "docs/INDEX.md").exists()
    assert ".pgk/" not in (tmp_path / ".gitignore").read_text(encoding="utf-8")
    config = load_config(tmp_path / ".project-governance.toml")
    assert config.visibility == "team-private"
    assert config.governance_dir == ".pgk"


def test_hybrid_initializes_private_governance_and_public_docs_surface(tmp_path: Path):
    result = init_project(tmp_path, visibility="hybrid")

    assert result.governance_dir == ".pgk"
    assert result.public_docs_dir == "docs/public"
    assert (tmp_path / ".pgk/STATUS.md").is_file()
    assert (tmp_path / "docs/public/INDEX.md").is_file()
    assert not (tmp_path / "docs/requirements/INDEX.md").exists()
    assert ".pgk/" in (tmp_path / ".gitignore").read_text(encoding="utf-8")


def test_private_record_creation_uses_governance_directory(tmp_path: Path):
    init_project(tmp_path, visibility="team-private")

    path = create_record(tmp_path, "requirement", "REQ-001", "Private requirement")

    assert path == tmp_path / ".pgk/requirements/REQ-001-private-requirement.md"
    assert not (tmp_path / "docs/requirements/REQ-001-private-requirement.md").exists()


def test_private_visibility_reports_governance_record_in_public_docs(tmp_path: Path):
    init_project(tmp_path, visibility="team-private")
    leaked = tmp_path / "docs/public/REQ-LEAK.md"
    leaked.parent.mkdir(parents=True)
    leaked.write_text(
        "---\nid: REQ-LEAK\ntype: requirement\nstatus: draft\ncreated: 2026-09-07\nupdated: 2026-09-07\nrelated:\n---\n",
        encoding="utf-8",
    )

    result = run_checks(tmp_path)

    assert any(issue["code"] == "public_governance_path" for issue in result.issues)


def test_public_visibility_keeps_backward_compatible_docs_layout(tmp_path: Path):
    result = init_project(tmp_path, visibility="public")

    assert result.governance_dir == "docs"
    assert (tmp_path / "docs/INDEX.md").is_file()
    assert ".pgk/" not in (tmp_path / ".gitignore").read_text(encoding="utf-8")


def test_invalid_visibility_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="visibility"):
        init_project(tmp_path, visibility="internal-only")


def test_hybrid_visibility_reports_missing_ignore_rule(tmp_path: Path):
    init_project(tmp_path, visibility="hybrid")
    ignore = tmp_path / ".gitignore"
    ignore.write_text("", encoding="utf-8")

    result = run_checks(tmp_path)

    assert any(issue["code"] == "missing_visibility_ignore" for issue in result.issues)


def test_check_reports_invalid_visibility_config(tmp_path: Path):
    init_project(tmp_path)
    config = tmp_path / ".project-governance.toml"
    config.write_text(config.read_text(encoding="utf-8").replace('visibility = "public"', 'visibility = "internal-only"'), encoding="utf-8")

    result = run_checks(tmp_path)

    assert any(issue["code"] == "invalid_visibility" for issue in result.issues)


@pytest.mark.parametrize("governance_dir", ("../private", "D:/private"))
def test_visibility_rejects_unsafe_governance_directory(tmp_path: Path, governance_dir: str):
    with pytest.raises(ValueError, match="governance_dir"):
        init_project(tmp_path, visibility="hybrid", governance_dir=governance_dir)


def test_hybrid_rejects_overlapping_private_and_public_directories(tmp_path: Path):
    with pytest.raises(ValueError, match="must not overlap"):
        init_project(
            tmp_path,
            visibility="hybrid",
            governance_dir="docs",
            public_docs_dir="docs/public",
        )
