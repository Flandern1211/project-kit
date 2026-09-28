---
id: TASK-022
type: task
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - REQ-001-ZH
  - DES-002-ZH
  - REQ-002-ZH
  - DES-003-ZH
---
# Fix custom governance-directory routing

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Ensure every supported visibility and migration operation uses the configured
governance directory instead of silently falling back to `docs/`.

## Owner
Codex

## Scope
- Route migration plan discovery, creation, auto-numbering, and verification
  records through the configured governance root.
- Make public visibility initialization honor an explicitly configured
  `governance_dir` while preserving the default public `docs/` layout.
- Add regression coverage for custom governance roots and the complete migration
  plan/approve/apply path.

## Files
- `src/project_governance/migration.py`
- `src/project_governance/scaffold.py`
- `tests/test_migration_custom_governance.py`
- `tests/test_visibility.py`
- `docs/work/tasks/TASK-022-fix-custom-governance-directory-routing.md`
- `docs/verification/VER-009-custom-governance-directory-routing.md`
- `docs/STATUS.md`

## Acceptance
- AC-1: With a non-default `governance_dir`, migration plan creation, loading,
  approval, application, indexing, and verification all use that configured
  root and never require `docs/migrations`.
- AC-2: Public visibility keeps the default `docs/` layout, but an explicit
  custom `governance_dir` creates and checks the complete governance tree at
  that root.
- AC-3: Focused and full tests, compilation, generated-view preview, and
  `pgk check` provide reproducible evidence with no regression in default paths.

## Evidence
VER-009 records the custom-root end-to-end and default-path regression tests.

## Changes
Migration paths, generated-document exclusion, public custom-root scaffolding,
and dirty-target protection now use the configured governance directory.

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
