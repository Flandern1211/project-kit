---
id: VER-012
type: verification
status: verified
created: 2026-09-28
updated: 2026-09-28
related:
  - TASK-025
---
# Verify PGK reliability documentation

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
Verify the documentation accurately describes the tested PGK behavior and
does not overstate transactional guarantees or release status.
## Owner
Codex
## Scope
- Bilingual README, usage guide, changelog, and STATUS consistency.
- Link, generated-view, governance, syntax, and full regression checks.
## Acceptance
- AC-1: Default and custom governance roots, invalid path rejection, and dirty
  migration targets are documented consistently with TASK-022/023 tests.
- AC-2: Staged writes, rollback failure recovery, and remaining limitations
  are documented without a version bump or release claim.
- AC-3: Full regression, compilation, generated-view preview, link/governance
  checks, and diff checks provide repeatable evidence.
## Evidence
- AC-1: Inspected both README status sections and `docs/usage.md` against
  `tests/test_visibility.py`, `tests/test_migration_custom_governance.py`,
  `tests/test_config_security.py`, and their implementations. The docs preserve
  default `docs/`/`.pgk/` locations, explain explicit custom roots, invalid
  configuration, and the dirty-target conflict before idempotence.
- AC-2: Inspected the staged-write and rollback behavior in
  `src/project_governance/records.py` and its failure-injection tests against
  both READMEs, the usage guide, and the Unreleased changelog. They disclose
  preserved recovery backups, possible empty directories/metadata changes,
  and lack of a global transaction. README, STATUS, configuration, and package
  version all remain `0.2.0.dev1`; no release is claimed.
- AC-3: `py -3 -m pytest -q -p no:cacheprovider -o "addopts=" --basetemp <external-temp>`
  passed 212 tests. `py -3 -m compileall -q src tests` and `git diff --check`
  exited 0. `pgk index --dry-run --json` reported `changed: []`, and
  `pgk check --json` reported only the expected pre-commit `dirty_worktree`.
## Changes
Documentation-only verification for TASK-025.
## Blockers
None known.
## Next action
Review external clean-tree integration evidence and downstream adoption
readiness.

## Git
branch: codex/atomic-transition
worktree: C:/Users/31800/.codex/worktrees/atomic-transition/project-kit
base_commit: 9ec63a7
head_commit: record-commit

## Handoff

<!-- PGK_HANDOFF_START -->
<!-- PGK_HANDOFF_END -->
