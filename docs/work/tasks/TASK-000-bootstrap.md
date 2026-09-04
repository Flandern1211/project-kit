---
id: TASK-000
type: task
status: verified
owner: root
created: 2026-09-02
updated: 2026-09-03
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

## Owner

root

## Files

- repository governance documents;
- `src/project_governance/`;
- `tests/`.

## Evidence

See [VER-000](../../verification/VER-000-bootstrap.md) for the bootstrap
evidence and its unverified boundaries.

## Blockers

none

## Next action

review the current v0.1 baseline evidence

## Git

branch: codex/bootstrap-v0.1
worktree: repository checkout
base_commit: N/A
head_commit: 799a3eaba69f5080940d28c3106fb61726288e50

## Task 5 self-validation

- `pgk check --root . --json` returned `ok=true` with no issues;
- editable package installation and `pgk --help` succeeded;
- empty-project initialization, check, and record dry-run succeeded;
- TouzhiAgent was inspected with read-only `pgk adopt`; its files were not changed;
- the verification record [VER-000](../../verification/VER-000-bootstrap.md)
  contains the command results and unverified boundaries.

## Handoff

<!-- PGK_HANDOFF_START -->
Status: verified
Branch: codex/bootstrap-v0.1
HEAD: 799a3eaba69f5080940d28c3106fb61726288e50
Worktree: dirty
Dirty: true
Uncommitted: present
Verification: 20 tests passed; pgk check ok; document validator 0 errors
Blockers: none
Next action: review and approve the first TouzhiAgent external trial
<!-- PGK_HANDOFF_END -->

