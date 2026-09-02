# Project Governance Kit v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a small, language-independent CLI that initializes,
creates, validates, and hands off repository governance records.

**Architecture:** Use a Python standard-library package with focused modules
for configuration, frontmatter, templates, checks, Git inspection, and CLI
dispatch. Generated project records remain ordinary Markdown and TOML files;
the CLI has no hidden database or network dependency.

**Tech Stack:** Python 3.11+, `argparse`, `tomllib`, standard-library
filesystem/subprocess utilities, pytest for tests.

**Spec:** `docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.md`
and `docs/design/2026-09-02-project-governance-kit-v0.1-design.md`

## Global Constraints

- Runtime dependencies are standard-library only.
- Generated files must not overwrite existing files.
- Read-only checks must not modify repositories.
- Git operations are read-only in v0.1.
- GitHub and model-provider APIs are out of scope.
- Human-readable and `--json` output are both required.
- The toolkit repository must run its own checks and tests.

---

### Task 1: Core records, templates, and configuration

**Files:**
- Create: `src/project_governance/models.py`
- Create: `src/project_governance/frontmatter.py`
- Create: `src/project_governance/config.py`
- Create: `src/project_governance/templates.py`
- Create: `src/project_governance/templates/`
- Test: `tests/test_records.py`

**Interfaces:**
- Produces record metadata parsing/rendering, profile configuration, and safe
  template paths for later CLI commands.

- [ ] Write tests for frontmatter parsing, duplicate/missing fields, and record
  rendering.
- [ ] Implement the minimum metadata parser and template loader.
- [ ] Run focused tests and record the result in `TASK-000`.
- [ ] Commit the focused implementation and tests.

### Task 2: Read-only checks and Git context

**Files:**
- Create: `src/project_governance/checks.py`
- Create: `src/project_governance/git_context.py`
- Test: `tests/test_checks.py`
- Test: `tests/test_git_context.py`

**Interfaces:**
- Produces deterministic check results and safe Git context for `doctor`,
  `check`, and `handoff`.

- [ ] Write tests for broken links, duplicate IDs, invalid statuses, required
  files, and clean/dirty Git fixtures.
- [ ] Implement read-only validation and JSON-serializable results.
- [ ] Run focused tests and update the task evidence.
- [ ] Commit the focused implementation and tests.

### Task 3: Scaffold and record commands

**Files:**
- Create: `src/project_governance/scaffold.py`
- Create: `src/project_governance/records.py`
- Create: `tests/test_scaffold.py`
- Create: `tests/test_records_commands.py`

**Interfaces:**
- Produces safe `init`, `adopt`, `new`, and `index` operations using the core
  models and templates.

- [ ] Write fixture-repository tests for missing-file creation and no-overwrite
  behavior.
- [ ] Implement standard-profile scaffolding and record creation.
- [ ] Implement read-only adoption reporting and index generation.
- [ ] Run focused tests and update the task evidence.
- [ ] Commit the focused implementation and tests.

### Task 4: CLI and handoff

**Files:**
- Create: `src/project_governance/cli.py`
- Create: `src/project_governance/handoff.py`
- Create: `src/project_governance/__main__.py`
- Modify: `pyproject.toml`
- Test: `tests/test_cli.py`
- Test: `tests/test_handoff.py`

**Interfaces:**
- Produces the `pgk` console script and `python -m project_governance` entry
  point with human and JSON output.

- [ ] Write command tests for help, `doctor`, `check`, `new`, and `handoff`.
- [ ] Implement argparse dispatch, stable exit codes, and dry-run handling.
- [ ] Implement task-section handoff updates without capturing full terminal
  output.
- [ ] Run the full test suite and update `VER-000`.
- [ ] Commit the CLI and tests.

### Task 5: Self-validation and external trial preparation

**Files:**
- Modify: `docs/STATUS.md`
- Modify: `docs/work/tasks/TASK-000-bootstrap.md`
- Modify: `docs/verification/VER-000-bootstrap.md`
- Test: `tests/fixtures/`

**Interfaces:**
- Produces evidence that the kit validates itself and can inspect TouzhiAgent
  without importing project-specific requirements.

- [ ] Run `pgk check --json` against the toolkit repository.
- [ ] Run the complete pytest suite and compile check.
- [ ] Run the project governance validator against this repository.
- [ ] Inspect TouzhiAgent in read-only adoption/doctor mode.
- [ ] Record all results, unresolved gaps, and next action.
- [ ] Commit the self-validation records.

