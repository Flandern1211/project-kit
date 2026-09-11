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
blocker: none
next_action: create a new task before changing behavior or current-state documentation
git_state: git_initialized
updated: 2026-09-11
```

## Current scope

The v0.1 requirements and DES-002-ZH technical design baselines remain accepted,
with the 2026-09-07 governance profile and scope revision recorded by ADR-0002.
The revision makes single-Agent and sequential handoff the v0.1 collaboration
core; parallel Agent coordination and external integrations are deferred.
Lite/Standard/Strict profile behavior, single/sequential collaboration-mode
configuration, and team-private/hybrid/public visibility are implemented and
verified. Parallel Agent coordination and external integrations remain deferred.
Protected Git and remote actions still require explicit user approval.

REQ-002-ZH and DES-003-ZH define the v0.2 existing-project migration MVP.
TASK-011 implements supplement mode and migration plan/approve/apply. TASK-012
preserves resolvable Markdown relative links in migrated copies. Both are
merged into `main` and covered by VER-002 and VER-003. TASK-014 started from
`main` at `3c56b49`, which already included the Strict Agent guidance,
control-document boundary, Git diagnostics, and environment preflight work.

TASK-014 closes current-state documentation drift and adds an automated Kit
version consistency check so package metadata, configuration, STATUS, and both
README files cannot silently disagree at handoff.

## Known constraints

- v0.1 uses Python 3.11+ and the standard library at runtime;
- core CLI remote operations are disabled; protected actions require explicit user authorization;
- no automatic commit, push, merge, deletion, or model-provider call;
- TouzhiAgent is an external trial, not a source of business rules for this kit.

## Verification snapshot

- clean fresh-project fixture `pgk check --root <fixture-copy> --json`: `ok=true`, no issues;
- `main` verification before TASK-014: 150 tests passed; focused guidance and
  diagnostic tests, compileall, and diff checks passed at `3c56b49`;
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
  migration produced no broken-link issues;
- TASK-014 full suite: 161 tests passed; compileall and diff-check passed;
  `uv build --wheel` produced version `0.2.0.dev0`; current-source `pgk check`
  reported only the expected pre-commit dirty worktree state.

## Next action

Create a new task before changing behavior or current-state documentation.
Protected Git and remote actions continue to require explicit authorization.
