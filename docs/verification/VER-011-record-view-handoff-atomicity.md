---
id: VER-011
type: verification
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - TASK-024
---
# Record, view, and handoff atomicity verification

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Verify ordinary governance writes use the same all-or-nothing filesystem
boundary as formal transitions.

## Owner
Codex

## Scope
Record creation, generated-view refresh, handoff update, rollback injection,
and temporary/backup cleanup.

## Acceptance
- AC-1: Failed record creation restores the record, views, and activity log
  byte-for-byte.
- AC-2: Failed index refresh and handoff update restore all affected files and
  leave no temporary or backup residue.
- AC-3: Successful behavior and repository-wide regression remain passing.

## Evidence
- AC-1: `tests/test_records_atomicity.py::test_create_record_failure_is_all_or_nothing` passed with a second-replacement failure and byte-level snapshot comparison.
- AC-2: `test_index_refresh_failure_is_all_or_nothing` and `test_handoff_failure_is_all_or_nothing` passed with residue checks.
- AC-3: The 212-test full regression passed; compileall and `git diff --check` exited 0; `pgk index --dry-run --json` reported `changed: []`; `pgk check --json` reported only the expected dirty worktree.

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
