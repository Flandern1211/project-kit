---
id: TASK-000
type: task
status: in_progress
owner: root
created: 2026-09-02
updated: 2026-09-02
related:
  - REQ-001
  - DES-001
---

# Bootstrap the self-governed toolkit

## Goal

Create the initial Project Governance Kit repository using the same governance
architecture that it will later provide to other projects.

## Scope

- initialize Git and the repository governance structure;
- record the v0.1 requirements and design;
- implement the smallest tested CLI surface;
- validate the kit against itself;
- prepare TouzhiAgent as the first external trial.

## Non-scope

- GitHub API mutation;
- model-provider integration;
- business-specific templates;
- hosted dashboards or runtime log storage.

## Acceptance

- the repository has a valid self-governance structure;
- the v0.1 CLI has unit and fixture tests;
- `pgk check` and the project test suite pass;
- a verification record cites the commands and results;
- no secrets or project-specific business rules are included.

## Handoff

<!-- PGK_HANDOFF_START -->
Status: bootstrap in progress.

Next action: implement the v0.1 CLI core and its fixture tests after the
requirements and design records are reviewed.

## Task 1 focused verification

- `py -3 -m pytest -q` — 6 passed.
- `py -3 -m compileall -q src tests` — passed.
- `git diff --check` — passed.

## Task 2 focused verification

- `py -3 -m pytest -q --basetemp .pytest-tmp tests/test_checks.py tests/test_git_context.py` — 3 passed.
- `py -3 -m pytest -q --basetemp .pytest-tmp` — 9 passed.
- `git diff --check` — passed.
- Environment note: default pytest temp root was denied by Windows permissions; workspace-local `--basetemp .pytest-tmp` was used.
<!-- PGK_HANDOFF_END -->

