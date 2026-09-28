---
id: VER-009
type: verification
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - TASK-022
---
# Custom governance-directory routing verification

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Verify configured governance roots are honored across visibility and migration
flows.

## Owner
Codex

## Scope
Custom public governance roots, migration plan/approve/apply, generated views,
verification records, and dirty-target protection.

## Acceptance
- AC-1: Custom-root migration plan creation, loading, approval, application,
  indexing, and verification use the configured root.
- AC-2: Public initialization honors an explicit custom governance root while
  default public initialization remains under `docs/`.
- AC-3: Tests and checks provide reproducible evidence without default-path
  regressions.

## Evidence
- AC-1: `tests/test_migration_custom_governance.py::test_migration_uses_custom_governance_directory_end_to_end` passed; the complete flow used `governance/internal` and created no `docs/migrations` plan.
- AC-2: `tests/test_visibility.py::test_public_visibility_honors_explicit_custom_governance_directory`, the default public-layout test, and the configured-root adoption-report cases passed; `pgk doctor` consumes this same report.
- AC-3: Migration/visibility/transition/views focused suite passed 45 tests; full PGK regression passed 212 tests; `compileall` and `git diff --check` exited 0; `pgk index --dry-run --json` reported `changed: []`; `pgk check --json` reported only the expected dirty worktree.

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
