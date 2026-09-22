# Project status

```yaml
status: verified
project_stage: active_development
version: 0.2.0.dev1
active_task: none
current_requirement: REQ-001-ZH
current_design: DES-002-ZH
current_task: none
owner: root
blocker: none
next_action: none; new work requires an accepted requirement and task
git_state: git_initialized
updated: 2026-09-22
```

## Current scope

The v0.1 requirements and DES-002-ZH technical design baselines remain accepted,
with the 2026-09-07 governance profile and scope revision recorded by ADR-0002.
The revision makes single-Agent and sequential handoff the v0.1 collaboration
core.
Lite/Standard/Strict profile behavior, single/sequential collaboration-mode
configuration, and team-private/hybrid/public visibility are implemented and
verified. ADR-0004 retains only safe parallel-Agent/worktree coordination and
task-authorized local automatic commits as planned extensions; external
integrations are product non-goals.
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

ADR-0004 narrows the future roadmap to two extensions only: safe parallel-Agent
and worktree coordination, and task-authorized local automatic commits. Web or
hosted administration, model calls, complex-format conversion, semantic
rewriting, Git-history cleanup, remote-permission management, generic external
platform integration, automatic public-copy export, and automatic remote Git
actions are product non-goals rather than deferred work.

REQ-003-ZH and DES-004-ZH add an Agent-first conversational entry over the existing
local CLI. TASK-016 implements the repository Skill and its new/existing/governed
project evaluations; VER-004 records the accepted 100% versus 80% comparison.
The Skill is also installed in the current user's Codex skills directory. It adds
no remote integration or new CLI subsystem.

TASK-017 makes the Skill's trigger, input, workflow, output, and acceptance
contracts explicit at runtime without changing its verified project flows.
The runtime instructions, concise discovery description, and Codex UI prompt
are localized for Chinese. VER-005 confirms the repository and installed copies
are identical and valid.

TASK-019 adds deterministic lifecycle transitions and terminal record gates. New
task, bug, and verification records use stable acceptance IDs and reciprocal
verification evidence; historical records remain readable without repository-wide
migration. Generated-view drift and invalid Git evidence are now checkable facts.

TASK-019 terminal gates and the governed-project upgrade path passed focused
and full verification. The FundAgent audit remains read-only; its upgrade
proposal was generated but not applied.

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
- TASK-014 full suite: 161 tests passed; compileall, diff-check, and package
  build passed; current-source `pgk check` reported only the expected
  pre-commit dirty worktree state.
- TASK-016: Codex Skill quick validation passed; with-skill behavior scored
  15/15 versus baseline 12/15; Python 3.14 full regression passed 164 tests;
  see [VER-004](verification/VER-004-agent-first-project-entry.md).
- TASK-017: the five-element runtime contract and installed copy passed Codex
  Skill validation; checker regression passed 31 tests; see
  [VER-005](verification/VER-005-skill-five-element-contract.md).
- TASK-019: 184-test full regression, 7 focused upgrade tests, compileall, and
  diff checks passed; FundAgent upgrade preview proposed 10 changes and wrote
  nothing; see [VER-006](verification/VER-006-terminal-gate-verification.md).

## Next action

No active task. TASK-019 is verified and its evidence is recorded in
[VER-006](verification/VER-006-terminal-gate-verification.md). Review of
[Flandern1211/skills PR #1](https://github.com/Flandern1211/skills/pull/1)
remains a separate protected remote action.
