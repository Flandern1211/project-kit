# Project status

```yaml
status: verified
project_stage: maintenance
version: 0.1.0.dev0
active_task: none
current_requirement: REQ-001-ZH
current_design: DES-002-ZH
current_task: none
owner: root
blocker: existing dirty worktrees and user-owned unregistered task/TASK-006-v02-migration are not part of this task; protected Git actions still require user approval
next_action: review TASK-007/TASK-008 updates; create a new task for further scope
git_state: git_initialized
updated: 2026-09-07
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

## Next action

TASK-007 profile implementation and TASK-008 bilingual README synchronization are verified. Parallel coordination, automatic
profile assessment, and external integrations remain deferred.
