# Governance Visibility Modes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add validated `team-private`, `hybrid`, and `public` visibility modes without remote platform operations or history rewriting.

**Architecture:** Keep the existing Standard/Lite/Strict profile model and add an independent visibility configuration. The core implementation uses a configurable governance root (default `docs` for backward compatibility) and a public docs root for hybrid projects; checks validate configuration, ignore rules, and public-path leakage. Existing files are never moved or deleted automatically.

**Tech Stack:** Python 3.11+, standard library, argparse, TOML, pytest.

**Spec:** `docs/superpowers/specs/2026-09-07-governance-visibility-design.md`

## Global Constraints

- Visibility values are `team-private`, `hybrid`, and `public`.
- Visibility is independent of profile and collaboration mode.
- Core commands remain local/offline and never call GitHub/GitLab APIs.
- Existing files are not overwritten, moved, or deleted automatically.
- Protected Git actions remain user-authorized.

---

### Task 1: Configuration and path contract

**Files:**
- Modify: `src/project_governance/config.py`
- Test: `tests/test_visibility.py`

**Interfaces:**
- `ProjectConfig.visibility: str`
- `ProjectConfig.governance_dir: str`
- `ProjectConfig.public_docs_dir: str`
- `validate_visibility(value: str) -> str`

- [ ] Add failing tests for valid modes, invalid modes, and default backward-compatible values.
- [ ] Implement validation and TOML parsing for visibility fields.
- [ ] Run `pytest tests/test_visibility.py` and confirm the new tests pass.

### Task 2: Visibility-aware scaffolding

**Files:**
- Modify: `src/project_governance/scaffold.py`
- Modify: `src/project_governance/cli.py`
- Test: `tests/test_visibility.py`

**Interfaces:**
- `init_project(..., visibility="public", governance_dir=None, public_docs_dir=None)`
- `ScaffoldResult.visibility`
- `ScaffoldResult.governance_dir`

- [ ] Add failing tests for public, team-private, and hybrid initialization output.
- [ ] Implement configuration rendering and ignore-rule insertion without overwriting `.gitignore`.
- [ ] Add CLI flags `--visibility`, `--governance-dir`, and `--public-docs-dir`.
- [ ] Run the visibility tests and existing scaffold tests.

### Task 3: Visibility-aware records and checks

**Files:**
- Modify: `src/project_governance/records.py`
- Modify: `src/project_governance/handoff.py`
- Modify: `src/project_governance/checks.py`
- Test: `tests/test_visibility.py`

**Interfaces:**
- Records and handoff paths resolve from the configured governance directory.
- `pgk check` reports `invalid_visibility`, `missing_visibility_ignore`, and `public_governance_path`.

- [ ] Add failing tests for record creation and handoff in a configured governance directory.
- [ ] Implement root/path helpers using the project configuration.
- [ ] Make checks validate visibility and scan configured public paths for governance records.
- [ ] Run focused tests and the full suite.

### Task 4: Documentation and acceptance evidence

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `docs/usage.md`
- Modify: `docs/STATUS.md`
- Modify: `docs/work/BOARD.md`
- Modify: `docs/activity/ACTIVITY.md`
- Modify: `docs/work/tasks/TASK-009-visibility-modes-design.md`
- Create: `docs/work/tasks/TASK-010-implement-visibility-modes.md`

- [ ] Document the three modes, private Git repository requirement, and historical privacy warning.
- [ ] Record test commands and real-project verification.
- [ ] Run compileall, diff-check, full tests, and the real-project fixture.
- [ ] Update indexes and status with evidence; do not perform remote operations without approval.
