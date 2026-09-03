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

## Task 5 self-validation

- `pgk check --root . --json` returned `ok=true` with no issues;
- editable package installation and `pgk --help` succeeded;
- empty-project initialization, check, and record dry-run succeeded;
- TouzhiAgent was inspected with read-only `pgk adopt`; its files were not changed;
- the verification record [VER-000](../../verification/VER-000-bootstrap.md)
  contains the command results and unverified boundaries.

## Handoff

<!-- PGK_HANDOFF_START -->
Status: in_progress
Branch: codex/bootstrap-v0.1
HEAD: fc3c390e99d55af0bf3ccc0c34b6c857449bf2b5
Worktree: clean
Verification: pgk check --json: ok; project validator: 0 errors
Blockers: none
Next action: review v0.1 self-validation results
<!-- PGK_HANDOFF_END -->

