---
id: VER-008
type: verification
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - TASK-021
---
# formal transition atomicity

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Independently verify that formal lifecycle transitions are atomic across the
record file, generated views, and activity log.
## Owner
Codex
## Scope
- Focused transition regression and injected filesystem replacement failure.
- Full PGK regression, compile, diff, generated-view, and governance checks.
- No remote action or business-project changes.
## Acceptance
- AC-1: Injected replacement failure leaves every transition target byte-identical
  and leaves no temporary or backup files.
- AC-2: Successful legal transition updates the record, INDEX, BOARD, and ACTIVITY
  consistently without temporary or backup residue.
- AC-3: The implementation passes the full regression and repository governance
  checks, with actual command evidence recorded below.
## Evidence
- AC-1: `tests/test_terminal_governance.py::test_transition_rolls_back_when_replacement_fails`
  passed; it injects an `OSError` on the second replacement and compares all
  non-Git files byte-for-byte before and after, including residue checks.
- AC-2: `tests/test_terminal_governance.py::test_transition_success_updates_all_transaction_targets`
  passed; the task, work INDEX, BOARD, and ACTIVITY receive the expected status
  and transition event, with no residue.
- AC-3: `py -3 -m pytest -q -p no:cacheprovider -o "addopts=" --basetemp <external-temp>`
  passed: 212 tests; `py -3 -m compileall -q src tests` and `git diff --check`
  exited 0; `pgk index --dry-run --json` reports no changes after indexing;
  `pgk check --json` reports no governance issues apart from the expected dirty
  worktree while this change is uncommitted.
## Changes
- Added staged multi-file transition replacement with rollback, newline
  preservation, symlink refusal, and backup-copy recovery fallback.
- Added prospective view rendering and failure-injection regression coverage,
  including final ACTIVITY failure and rollback-replace failure.
## Blockers
None known for implementation; post-commit clean-tree evidence belongs in the
external handoff.
## Next action
Review the external clean-tree verification handoff and decide whether to
integrate the task branch.
