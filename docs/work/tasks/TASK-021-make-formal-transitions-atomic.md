---
id: TASK-021
type: task
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - REQ-001-ZH
  - DES-002-ZH
  - TASK-020
---
# Make formal transitions atomic

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Make `pgk transition` an all-or-nothing update across the record, generated views,
and activity log, so a filesystem failure cannot leave governance state inconsistent.
## Owner
Codex
## Scope
- Stage every transition output before replacing any destination.
- Restore all already-replaced files when a later replacement fails.
- Preserve existing generated-view ownership guards, newline conventions, and
  dry-run behavior.
## Files
- `src/project_governance/records.py`
- `tests/test_terminal_governance.py`
- `docs/work/tasks/TASK-021-make-formal-transitions-atomic.md`
- `docs/verification/VER-008-formal-transition-atomicity.md`
- `docs/STATUS.md`
- generated work indexes and activity view
## Acceptance
- AC-1: If any destination replacement fails during a non-dry-run transition, the
  record, every generated view, and ACTIVITY remain byte-identical to their
  pre-transition contents, with no temporary or backup files left behind.
- AC-2: A successful legal transition updates the record, generated views, and
  ACTIVITY consistently, and existing transition regression tests remain passing.
- AC-3: Focused/full tests, compilation, generated-view preview, and `pgk check`
  provide reproducible evidence for the implementation.
## Evidence
- AC-1: VER-008 confirms byte-identical rollback and residue cleanup.
- AC-2: VER-008 confirms consistent successful updates and residue cleanup.
- AC-3: VER-008 records the 189-test regression and repository checks.
## Changes
- Added staged multi-file replacement with rollback and prospective view rendering.
- Added newline preservation, symlink refusal, backup-copy rollback fallback,
  and failure-injection coverage for replacement and residual cleanup.
## Blockers
None known for implementation.
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
