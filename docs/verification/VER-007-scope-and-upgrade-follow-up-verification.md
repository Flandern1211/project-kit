---
id: VER-007
type: verification
status: in_review
created: 2026-09-23
updated: 2026-09-24
related:
  - TASK-020
---
# Scope and upgrade follow-up verification

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Independently verify the TASK-020 checker and upgrade corrections against fixtures and FundAgent.
## Owner
Codex
## Scope
Local tests and read-only inspection of FundAgent; no commit, remote action, or real portfolio access.
## Acceptance
- AC-1: Sequential file reuse is not a conflict; parallel active overlap remains detected.
- AC-2: Current dirty checkout has a single diagnostic.
- AC-3: Same-version view repair and AGENTS final newline are idempotent.
- AC-4: Regression suite and FundAgent checks report precise remaining blockers.
## Evidence
- AC-1: `test_checks_ignore_sequential_file_scope_overlap` and `test_checks_report_dirty_git_and_overlapping_file_scopes` cover single/sequential versus parallel active/blocked work; FundAgent `overlapping_file_scope` falls from 55 to 0 without changing task states.
- AC-2: `test_checks_report_dirty_git_and_overlapping_file_scopes` reports one local dirty issue; `test_checks_distinguish_current_and_other_dirty_worktrees` reports both distinct dirty checkouts.
- AC-3: `test_same_version_generated_view_drift_does_not_create_upgrade_activity` and `test_upgrade_repairs_extra_blank_line_after_last_managed_section` pass. FundAgent same-version preview after apply has `changed=[]` and `conflicts=[]`; BOARD and AGENTS are stable.
- AC-4: `py -3 -m pytest -q -p no:cacheprovider -o 'addopts=' --basetemp D:\pgk-followup-final-20260923`: 187 passed; `py -3 -m compileall -q src tests` and `git diff --check`: exit 0; `pgk index --dry-run --json`: changed=[]. Current-source PGK check exits 1 with one expected dirty_worktree. FundAgent full suite: 78 passed; check/doctor exit 1 with one dirty_worktree, zero other governance issues. No clean-tree or external source acceptance is claimed.
## Changes
All local criteria have test or inspection evidence; terminal review remains pending.
## Blockers
None for local checks; external business acceptance is outside this verification.
## Next action
Review TASK-020 and decide its terminal status.
