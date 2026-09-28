---
id: VER-010
type: verification
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - TASK-023
---
# Configured governance-path validation verification

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Verify malformed governance-directory configuration cannot escape the project
root or cause unintended writes.

## Owner
Codex

## Scope
Configuration loading, read-only checks, record creation, and invalid path
fixtures.

## Acceptance
- AC-1: Invalid governance/public paths are rejected and reported without
  writing outside the project root.
- AC-2: Valid configured paths continue to support existing governance behavior.
- AC-3: Focused/full tests and repository checks provide reproducible evidence.

## Evidence
- AC-1: `tests/test_config_security.py` passed 10 cases covering traversal, absolute, dot, empty, and nested traversal values; the write-boundary test confirmed no record appeared outside the fixture root.
- AC-2: `tests/test_migration_custom_governance.py` and `tests/test_visibility.py` passed for valid custom roots.
- AC-3: Full PGK regression passed 212 tests; `compileall` and `git diff --check` exited 0; `pgk index --dry-run --json` reported `changed: []`; `pgk check --json` reported only the expected dirty worktree.

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
