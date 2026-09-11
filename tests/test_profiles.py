from pathlib import Path

import pytest

from project_governance.config import load_config
from project_governance.records import create_record
from project_governance.scaffold import init_project
from project_governance.checks import run_checks


def test_lite_profile_creates_only_core_governance_tree(tmp_path: Path):
    result = init_project(tmp_path, profile="lite")

    assert result.profile == "lite"
    assert result.collaboration_mode == "single-agent"
    assert (tmp_path / "docs/requirements/INDEX.md").is_file()
    assert (tmp_path / "docs/work/tasks/INDEX.md").is_file()
    assert (tmp_path / "docs/verification/INDEX.md").is_file()
    assert not (tmp_path / "docs/design/INDEX.md").exists()
    assert not (tmp_path / "docs/operations/runbooks/INDEX.md").exists()
    config = load_config(tmp_path / ".project-governance.toml")
    assert config.profile == "lite"
    assert config.collaboration_mode == "single-agent"


def test_strict_profile_adds_risk_security_and_release_entries(tmp_path: Path):
    result = init_project(tmp_path, profile="strict")

    assert result.profile == "strict"
    for relative in (
        "docs/risk/INDEX.md",
        "docs/security/INDEX.md",
        "docs/releases/INDEX.md",
        "docs/operations/incidents/INDEX.md",
    ):
        assert (tmp_path / relative).is_file()


def test_sequential_collaboration_mode_is_recorded(tmp_path: Path):
    result = init_project(tmp_path, collaboration_mode="sequential-agents")

    assert result.collaboration_mode == "sequential-agents"
    config_text = (tmp_path / ".project-governance.toml").read_text(encoding="utf-8")
    assert 'collaboration_mode = "sequential-agents"' in config_text


def test_parallel_collaboration_mode_is_rejected_in_v01(tmp_path: Path):
    with pytest.raises(ValueError, match="parallel-agents"):
        init_project(tmp_path, collaboration_mode="parallel-agents")


def test_check_uses_strict_profile_required_entries(tmp_path: Path):
    init_project(tmp_path, profile="strict")
    (tmp_path / "docs/security/INDEX.md").unlink()

    result = run_checks(tmp_path)

    assert any(
        issue["code"] == "missing_profile_artifact"
        and issue["path"] == "docs/security/INDEX.md"
        for issue in result.issues
    )


def test_strict_plain_control_markdown_remains_accepted(tmp_path: Path):
    init_project(tmp_path, profile="strict")
    control_path = tmp_path / "docs/risk/RISK-001.md"
    control_path.write_text("# Risk\n\nReview the payment limit.\n", encoding="utf-8")

    result = run_checks(tmp_path)

    assert result.ok


def test_lite_profile_rejects_records_that_are_not_enabled(tmp_path: Path):
    init_project(tmp_path, profile="lite")

    with pytest.raises(ValueError, match="lite profile does not enable design"):
        create_record(tmp_path, "design", "DES-001", "Architecture")
