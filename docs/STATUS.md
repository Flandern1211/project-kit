# Project status

```yaml
status: verified
project_stage: active_development
version: 0.2.0.dev0
active_task: none
current_requirement: REQ-002-ZH
current_design: DES-003-ZH
current_task: none
owner: root
blocker: none; push remains user-controlled
next_action: review local main at 7ebef4c and decide whether to push
git_state: git_initialized
updated: 2026-09-08
```

## Current scope

The v0.1 requirements and DES-002-ZH technical design baselines remain accepted,
with the 2026-09-07 governance profile and scope revision recorded by ADR-0002.
The revision makes single-Agent and sequential handoff the v0.1 collaboration
core; parallel Agent coordination and external integrations are deferred.
The existing implementation baseline is unchanged by this documentation task.
The newly accepted Lite/Standard/Strict profile behavior and collaboration-mode
configuration are documented scope, not yet claimed as implemented runtime behavior.
Protected Git and remote actions still require explicit user approval.

REQ-002-ZH and DES-003-ZH define the v0.2 existing-project migration MVP.
TASK-011 was locally verified before synchronizing with `origin/main`; the
combined profile, visibility and migration implementation passed merged-result
verification on `main` at 8d57cd7.
TASK-012 fixes relative links in migrated Markdown copies and passed an
isolated TouzhiAgent clone validation. The fix is merged into local `main` at
7ebef4c.

## Known constraints

- v0.1 uses Python 3.11+ and the standard library at runtime;
- core CLI remote operations are disabled; protected actions require explicit user authorization;
- no automatic commit, push, merge, deletion, or model-provider call;
- TouzhiAgent is an external trial, not a source of business rules for this kit.

## Verification snapshot

- clean fresh-project fixture `pgk check --root <fixture-copy> --json`: `ok=true`, no issues;
- current working checkout `pgk check` reports only existing dirty-worktree and
  user-owned unregistered-branch state;
- editable package installation and `pgk --help`: passed;
- empty-project `pgk init`, `pgk check`, and `pgk new --dry-run`: passed;
- TouzhiAgent `pgk adopt`: read-only mapping report produced, no files changed;
- 86-test suite, compile check, project-document validator, and fresh-project
  acceptance fixture: passed; see [VER-001](verification/VER-001-v0-1-new-project-baseline.md).
- current profile implementation regression suite: 92 tests passed; compileall and
  diff-check passed. `pgk check` still reports only existing Git-state issues.
- visibility implementation regression suite: 101 tests passed; real-project
  team-private/hybrid/public initialization and checks passed.
- merged profile, visibility and migration suite on `main`: 120 tests passed;
  compileall and diff-check passed; worktree-local pgk check returned `ok=true`.
- TASK-012 link-rewrite suite: 139 tests passed; real TouzhiAgent clone
  migration produced no broken-link issues.

## Next action

TASK-007 profile implementation and TASK-008 bilingual README synchronization are verified.
TASK-009 visibility design, TASK-010 implementation, TASK-011 migration
implementation, and TASK-012 relative-link repair are verified in the merged
result. Review local main at 7ebef4c before authorizing push.
