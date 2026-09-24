---
id: TASK-020
type: task
status: in_review
created: 2026-09-23
updated: 2026-09-24
related:
  - REQ-001-ZH
  - DES-002-ZH
---
# Correct sequential scope checks and upgrade idempotence

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Remove false governance conflicts observed during the FundAgent follow-up audit without weakening terminal evidence gates.
## Owner
Codex
## Scope
- Limit file-scope conflict diagnostics to concurrently actionable parallel work.
- Deduplicate dirty-worktree diagnostics for the current checkout.
- Keep a same-version generated-view refresh out of the upgrade activity log and normalize the last managed section newline.
- Preserve conflict-safe upgrade behavior, historical records, and all other check gates.
## Files
- `src/project_governance/checks.py`
- `src/project_governance/upgrade.py`
- `tests/test_governance_checks.py`
- `tests/test_upgrade.py`
- `tests/test_new_project_acceptance.py`
- `docs/work/tasks/TASK-020-correct-sequential-scope-checks-and-upgrade-idempotence.md`
- `docs/verification/VER-007-scope-and-upgrade-follow-up-verification.md`
- `docs/STATUS.md`
- `docs/usage.md`
- `docs/project-conventions.md`
- `README.md`
- `docs/INDEX.md`
## Acceptance
- AC-1: Single and sequential Agent tasks may share files without `overlapping_file_scope`; parallel actionable tasks still conflict, blocked work does not.
- AC-2: The current dirty worktree appears once; other linked dirty worktrees remain reportable.
- AC-3: Same-version preview/apply repairs stale generated views without inventing an upgrade activity event; the last managed AGENTS section has one final newline and repeat preview is empty.
- AC-4: Focused and full tests, compile, index preview, and PGK checks record actual outcomes; FundAgent business blockers remain separate.
## Evidence
- AC-1: VER-007 confirms single/sequential reuse, parallel overlap, and blocked-task exclusion.
- AC-2: VER-007 confirms one diagnostic for the current checkout and a second for a different dirty linked worktree.
- AC-3: VER-007 confirms same-version view repair without an activity event and a stable AGENTS final newline.
- AC-4: VER-007 records 187 full tests, compile/diff/index checks, and the exact FundAgent audit result.
## Changes
Scoped checker and upgrade corrections are implemented and under review. The unrelated subprocess acceptance fixture now tolerates an existing PYTHONPATH.
## Blockers
No code blocker; terminal review remains pending.
## Next action
Review the verification evidence and decide the terminal status.

## Git
branch: codex/task-019-terminal-gates
worktree: C:/Users/31800/.codex/worktrees/task-019-terminal-gates/project-kit
base_commit: fcfe9ff
head_commit: N/A

## Handoff

<!-- PGK_HANDOFF_START -->
<!-- PGK_HANDOFF_END -->
