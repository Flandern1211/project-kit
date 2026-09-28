---
id: TASK-023
type: task
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - REQ-001-ZH
  - DES-002-ZH
  - TASK-010
  - TASK-022
---
# Validate configured governance paths

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Prevent malformed governance-directory configuration from escaping the project
root or causing writes to an unintended location.

## Owner
Codex

## Scope
- Validate `governance_dir` and `public_docs_dir` when loading project config.
- Preserve normalized validated paths in the runtime configuration.
- Report invalid configuration through read-only checks and reject all write
  operations before they resolve paths outside the project root.
- Add regression coverage for traversal, absolute, empty, and overlapping paths.

## Files
- `src/project_governance/config.py`
- `tests/test_config_security.py`
- `docs/work/tasks/TASK-023-validate-configured-governance-paths.md`
- `docs/verification/VER-010-configured-governance-path-validation.md`
- `docs/STATUS.md`

## Acceptance
- AC-1: Invalid configured governance/public paths are rejected by `load_config`
  and reported by `pgk check` without writing outside the project root.
- AC-2: Valid configured paths are normalized and continue to support records,
  views, migration, and visibility behavior.
- AC-3: Focused/full tests, compilation, generated-view preview, and `pgk check`
  provide reproducible evidence for the security boundary.

## Evidence
VER-010 records invalid-path rejection, root-boundary, and valid custom-root tests.

## Changes
`load_config` now validates configured governance and public documentation paths
before any runtime component can resolve them.

## Blockers
None known.

## Next action
Review the external clean-tree verification handoff and decide whether to
integrate the task branch.

## Git
branch: codex/atomic-transition
worktree: C:/Users/31800/.codex/worktrees/atomic-transition/project-kit
base_commit: 2804df6
head_commit: record-commit

## Handoff

<!-- PGK_HANDOFF_START -->
<!-- PGK_HANDOFF_END -->
