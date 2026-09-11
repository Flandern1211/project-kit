import os
import subprocess
from pathlib import Path
import pytest

from project_governance.git_context import inspect_git
from project_governance.scaffold import adopt_project, init_project


def test_init_creates_standard_profile_and_never_overwrites_existing_files(tmp_path: Path):
    existing = tmp_path / "AGENTS.md"
    existing.write_text("project-owned instructions\n", encoding="utf-8")

    first = init_project(tmp_path, project_name="Example")

    assert "AGENTS.md" in first.skipped
    assert "CONTRIBUTING.md" in first.created
    assert (tmp_path / "docs" / "INDEX.md").is_file()
    assert (tmp_path / "README.md").is_file()
    assert first.project_stage == "requirements_discussion"
    assert first.git_state == "git_not_initialized"
    assert existing.read_text(encoding="utf-8") == "project-owned instructions\n"

    second = init_project(tmp_path, project_name="Changed")

    assert not second.created
    assert "AGENTS.md" in second.skipped
    assert (tmp_path / "README.md").exists()


def test_init_creates_complete_tree_and_dry_run_is_non_mutating(tmp_path: Path):
    preview = init_project(tmp_path, dry_run=True)
    assert preview.created
    assert not list(tmp_path.iterdir())
    result = init_project(tmp_path)
    required = [
        "README.md", "AGENTS.md", "CONTRIBUTING.md", "CHANGELOG.md", ".gitignore",
        ".project-governance.toml", "docs/INDEX.md", "docs/STATUS.md", "docs/WORKFLOW.md",
        "docs/templates/INDEX.md", "docs/templates/review.md", "docs/requirements/INDEX.md",
        "docs/design/INDEX.md", "docs/decisions/INDEX.md", "docs/work/BOARD.md",
        "docs/work/tasks/INDEX.md", "docs/work/bugs/INDEX.md", "docs/reviews/INDEX.md",
        "docs/verification/INDEX.md", "docs/activity/ACTIVITY.md",
        "docs/operations/runbooks/INDEX.md", "docs/operations/incidents/INDEX.md",
        "docs/operations/postmortems/INDEX.md",
    ]
    assert all((tmp_path / item).is_file() for item in required)
    assert "project_stage: requirements_discussion" in (tmp_path / "docs/STATUS.md").read_text(encoding="utf-8")
    assert not list((tmp_path / "docs/requirements").glob("REQ-*.md"))


def test_adopt_is_read_only_and_reports_existing_mappings(tmp_path: Path):
    legacy = tmp_path / "docs" / "coding" / "PRD.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_text("legacy requirements", encoding="utf-8")
    before = legacy.read_bytes()

    report = adopt_project(tmp_path)

    assert report.missing
    assert any(item["path"] == "docs/coding/PRD.md" for item in report.mappings)
    assert legacy.read_bytes() == before


def test_adopt_reports_document_candidates_sensitive_items_and_git_state(tmp_path: Path):
    docs = tmp_path / "docs" / "coding"
    docs.mkdir(parents=True)
    (docs / "PRD.md").write_text("requirements", encoding="utf-8")
    (docs / "api-token.txt").write_text("TOKEN=redacted", encoding="utf-8")

    report = adopt_project(tmp_path)
    payload = report.as_dict()

    assert any(item["source_path"] == "docs/coding/PRD.md" for item in payload["candidates"])
    sensitive = next(item for item in payload["candidates"] if item["source_path"] == "docs/coding/api-token.txt")
    assert sensitive["sensitive"] is True
    assert "redacted" not in str(payload)
    assert "exclude_patterns" in payload
    assert payload["git"]["available"] is False


def test_init_reports_real_no_git_when_path_is_nested_in_this_checkout(tmp_path: Path, monkeypatch):
    # Prevent Git's parent discovery from treating pytest's fixture as this repo.
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    result = init_project(tmp_path)
    assert result.git_state == "git_not_initialized"


def test_git_init_without_commit_is_initialized_and_unborn(tmp_path: Path):
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    context = inspect_git(tmp_path)
    assert context.head == "unborn"
    result = init_project(tmp_path)
    assert result.git_state == "git_initialized"
    assert "project_stage: requirements_discussion" in (tmp_path / "docs/STATUS.md").read_text(encoding="utf-8")


def test_generated_status_and_views_include_required_contract(tmp_path: Path):
    init_project(tmp_path)
    status = (tmp_path / "docs/STATUS.md").read_text(encoding="utf-8")
    for field in ("project_stage", "current_requirement", "current_design", "current_task", "owner", "blocker", "next_action", "updated", "git_state"):
        assert f"{field}:" in status
    workflow = (tmp_path / "docs/WORKFLOW.md").read_text(encoding="utf-8")
    assert "initialized" in workflow and "maintenance" in workflow and "blocked" in workflow
    board = (tmp_path / "docs/work/BOARD.md").read_text(encoding="utf-8")
    assert "ID | type | status | owner | related | branch/worktree | verification | blocker | next" in board
    activity = (tmp_path / "docs/activity/ACTIVITY.md").read_text(encoding="utf-8")
    assert "initialize | N/A | N/A | initialized -> requirements_discussion" in activity


def test_strict_generation_includes_agent_and_document_map(tmp_path: Path):
    init_project(tmp_path, profile="strict")

    guidance = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    for record_type in (
        "requirement",
        "design",
        "decision",
        "task",
        "bug",
        "review",
        "verification",
        "migration",
    ):
        assert record_type in guidance
    for path in (
        "docs/requirements/",
        "docs/design/",
        "docs/decisions/",
        "docs/work/tasks/",
        "docs/work/bugs/",
        "docs/reviews/",
        "docs/verification/",
        "docs/migrations/",
        "docs/activity/",
        "docs/operations/runbooks/",
        "docs/operations/incidents/",
        "docs/operations/postmortems/",
        "docs/risk/",
        "docs/security/",
        "docs/releases/",
        "docs/templates/",
    ):
        assert path in guidance
    assert "risk/security/release/runbook" in guidance
    assert "Do not create" in guidance

    structure = tmp_path / "docs/project-structure.md"
    assert structure.is_file()
    index = (tmp_path / "docs/INDEX.md").read_text(encoding="utf-8")
    assert "[Project structure](project-structure.md)" in index


def test_lite_generation_keeps_references_and_finalization_guidance_consistent(tmp_path: Path):
    init_project(tmp_path, profile="lite")

    for relative in (
        "AGENTS.md",
        "docs/INDEX.md",
        "docs/project-structure.md",
        "docs/project-conventions.md",
        "docs/WORKFLOW.md",
        "docs/templates/INDEX.md",
    ):
        assert (tmp_path / relative).is_file()

    guidance = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "`requirement`, `task`, `bug`, and `verification`" in guidance
    assert "docs/project-structure.md" in guidance
    assert "docs/project-conventions.md" in guidance
    assert "Do not edit the repository after the clean-tree check" in guidance

    index = (tmp_path / "docs/INDEX.md").read_text(encoding="utf-8")
    assert "project-structure.md" in index
    assert "project-conventions.md" in index

    templates = (tmp_path / "docs/templates/INDEX.md").read_text(encoding="utf-8")
    assert "migration" not in templates.lower()

    for relative in ("docs/WORKFLOW.md", "docs/project-conventions.md"):
        content = (tmp_path / relative).read_text(encoding="utf-8")
        normalized = " ".join(content.split())
        assert "run semantic checks" in normalized.lower()
        assert "clean-tree" in content
        assert "post-commit output" in normalized.lower()


def test_generated_record_templates_include_task_git_contract(tmp_path: Path):
    init_project(tmp_path)
    task_template = (tmp_path / "docs/templates/task.md").read_text(encoding="utf-8")
    bug_template = (tmp_path / "docs/templates/bug.md").read_text(encoding="utf-8")
    for template in (task_template, bug_template):
        assert "## Owner" in template
        assert "## Files" in template
        assert "## Git" in template
        assert "base_commit: N/A" in template
        assert "head_commit: N/A" in template


def test_generated_work_index_is_valid_markdown(tmp_path: Path):
    init_project(tmp_path)
    content = (tmp_path / "docs/work/INDEX.md").read_text(encoding="utf-8")
    assert "\\n" not in content
    assert content.startswith("<!-- PGK_GENERATED: work-index -->\n# Work index\n")


def test_generated_record_templates_include_governance_fields(tmp_path: Path):
    init_project(tmp_path)
    task = (tmp_path / "docs/templates/task.md").read_text(encoding="utf-8")
    bug = (tmp_path / "docs/templates/bug.md").read_text(encoding="utf-8")
    verification = (tmp_path / "docs/templates/verification.md").read_text(encoding="utf-8")
    for content in (task, bug):
        assert "## Owner" in content
        assert "## Files" in content
        assert "## Git" in content
        assert "branch: N/A" in content
        assert "base_commit: N/A" in content
        assert "head_commit: N/A" in content
    assert "## Owner" in verification


def test_init_preflights_path_type_conflicts_without_partial_writes(tmp_path: Path):
    (tmp_path / "README.md").mkdir()
    with __import__("pytest").raises(ValueError, match="README.md"):
        init_project(tmp_path)
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")) == ["README.md"]


def test_init_reports_path_type_conflict_instead_of_skipping(tmp_path: Path):
    (tmp_path / "README.md").mkdir()
    with pytest.raises(ValueError, match="README.md"):
        init_project(tmp_path)


def test_init_preflights_path_conflict_before_creating_any_governance_paths(tmp_path: Path):
    (tmp_path / "README.md").mkdir()
    with pytest.raises(ValueError, match="README.md"):
        init_project(tmp_path)
    assert not (tmp_path / "docs").exists()


def test_init_reports_partial_write_errors(tmp_path: Path, monkeypatch):
    from project_governance import scaffold

    original = Path.write_text
    def fail_status(self, data, *args, **kwargs):
        if self.as_posix().endswith("docs/STATUS.md"):
            raise OSError("simulated write failure")
        return original(self, data, *args, **kwargs)
    monkeypatch.setattr(Path, "write_text", fail_status)
    result = init_project(tmp_path)
    assert "docs/STATUS.md" in result.errors
    assert result.errors["docs/STATUS.md"] == "simulated write failure"


def test_init_reports_directory_creation_errors(tmp_path: Path, monkeypatch):
    original = Path.mkdir
    def fail_docs(self, *args, **kwargs):
        if self.as_posix().endswith("docs"):
            raise OSError("simulated mkdir failure")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, "mkdir", fail_docs)
    result = init_project(tmp_path)
    assert result.errors.get("docs") == "simulated mkdir failure"

