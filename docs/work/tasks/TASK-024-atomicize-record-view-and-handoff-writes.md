---
id: TASK-024
type: task
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - REQ-001-ZH
  - DES-002-ZH
  - TASK-021
---
# Atomicize record, view, and handoff writes

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Prevent ordinary record creation, index refresh, and handoff updates from
leaving a partially written governance state when a later filesystem operation
fails.

## Owner
Codex

## Scope
- Reuse the staged multi-file transaction for record creation, generated-view
  refresh, and handoff updates.
- Preserve project-owned view guards and dry-run behavior.
- Add failure-injection tests for each write boundary.

## Files
- `src/project_governance/records.py`
- `src/project_governance/handoff.py`
- `tests/test_records_atomicity.py`
- `docs/work/tasks/TASK-024-atomicize-record-view-and-handoff-writes.md`
- `docs/verification/VER-011-record-view-handoff-atomicity.md`
- `docs/STATUS.md`

## Acceptance
- AC-1: Failed record creation leaves the record, generated views, and
  activity log byte-identical to their pre-call contents.
- AC-2: Failed index refresh or handoff update leaves all affected targets
  byte-identical and leaves no temporary/backup residue.
- AC-3: Successful default and custom-root operations retain existing behavior;
  focused/full tests and repository checks provide evidence.

## Evidence
VER-011 records failure-injection rollback and residue-cleanup evidence.

## Changes
Record creation, generated-view refresh, and handoff updates now stage all
targets through the shared transaction helper.

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
