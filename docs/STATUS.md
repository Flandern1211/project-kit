# Project status

```yaml
status: active_development
project_stage: active_development
version: 0.2.0.dev1
active_task: TASK-025
current_requirement: REQ-001-ZH
current_design: DES-002-ZH
current_task: TASK-025
owner: Codex
blocker: None known for verified TASK-021 through TASK-025 work
next_action: review external integration evidence and downstream adoption readiness
git_state: git_initialized
updated: 2026-09-28
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
and full verification. TASK-020 follows the FundAgent upgrade audit: it narrows
file-scope diagnostics to active parallel work, removes duplicate local Git
warnings, and makes same-version view repair and final-section formatting
idempotent. FundAgent's own business remediation is not a PGK verification.

TASK-021 makes formal lifecycle transitions atomic across the record file,
generated indexes/BOARD, and ACTIVITY log. Failure-injection and successful-path
tests pass; Git finalization evidence belongs in the external handoff.

TASK-022 fixes custom governance-directory routing across migration and public
visibility flows, including dirty-target protection. TASK-023 validates configured
governance paths before use so malformed configuration cannot escape the project
root. Both are verified by VER-009 and VER-010.

TASK-024 extends the transaction boundary to record creation, generated-view
refresh, and handoff updates; VER-011 covers failure-injection rollback.

TASK-025 synchronizes the bilingual READMEs, usage guide, changelog, and
current status with TASK-021–024. It documents the remaining filesystem
recovery limitations without changing the `0.2.0.dev1` Kit version.

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
- TASK-020: 187-test full regression, compileall, diff check, and index preview
  passed. The pre-commit current-source check had only a dirty-worktree issue.
  FundAgent check/doctor likewise have only one dirty-worktree issue; see
  [VER-007](verification/VER-007-scope-and-upgrade-follow-up-verification.md).
- TASK-021: focused transition tests and the 212-test full regression passed;
  compileall, diff check, generated-view preview, and governance checks passed
  apart from the expected uncommitted dirty worktree; see
  [VER-008](verification/VER-008-formal-transition-atomicity.md).
- TASK-022/TASK-023: custom-root migration, visibility, dirty-target, and
  configuration-boundary tests passed; see [VER-009](verification/VER-009-custom-governance-directory-routing.md)
  and [VER-010](verification/VER-010-configured-governance-path-validation.md).
- TASK-024: record/index/handoff failure-injection tests passed; see
  [VER-011](verification/VER-011-record-view-handoff-atomicity.md).
- TASK-025: bilingual documentation review, 212-test full regression,
  compilation, diff and view checks passed; see
  [VER-012](verification/VER-012-verify-pgk-reliability-documentation.md).

## Next action

Review external integration evidence and downstream adoption readiness. The
existing Skill PR remains unrelated.
