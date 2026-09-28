---
id: TASK-025
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
# Document PGK reliability fixes

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Synchronize user-facing documentation with the verified PGK reliability fixes
before integrating the task branch. This task changes no runtime behavior or
Kit version.
## Owner
Codex
## Scope
- Explain configured governance-root routing, path validation, and dirty
  migration-target protection in Chinese and English.
- Explain staged governance writes, rollback, and the limits of recovery.
- Update the unreleased changelog and project STATUS without claiming a new
  release or a remote Git result in advance.
## Files
- `README.md`
- `README.en.md`
- `CHANGELOG.md`
- `docs/usage.md`
- `docs/STATUS.md`
- `docs/work/tasks/TASK-025-document-pgk-reliability-fixes.md`
- `docs/verification/VER-012-verify-pgk-reliability-documentation.md`
## Acceptance
- AC-1: Both READMEs and the usage guide accurately document default and
  configured governance roots, invalid path rejection, and dirty-target
  migration conflicts without claiming a changed default layout.
- AC-2: The docs and unreleased changelog describe staged updates and recovery
  limits without promising global transactions or a new Kit version.
- AC-3: Full regression, compilation, generated-view preview, link/governance
  checks, and diff checks pass, except the expected pre-commit dirty worktree.
## Evidence
- AC-1 through AC-3: reciprocal outcomes and commands are recorded in VER-012.
## Changes
Updated the two READMEs, changelog, usage guide, and STATUS for TASK-021–024.
## Blockers
None known for documentation; integration evidence belongs in the external
handoff.
## Next action
Review the verification handoff and downstream adoption readiness.

## Git
branch: codex/atomic-transition
worktree: C:/Users/31800/.codex/worktrees/atomic-transition/project-kit
base_commit: 9ec63a7
head_commit: record-commit

## Handoff

<!-- PGK_HANDOFF_START -->
<!-- PGK_HANDOFF_END -->
