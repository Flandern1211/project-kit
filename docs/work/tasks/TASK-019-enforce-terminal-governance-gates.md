---
id: TASK-019
type: task
status: verified
created: 2026-09-22
updated: 2026-09-22
related:
  - REQ-001-ZH
  - DES-002-ZH
---
# Enforce terminal governance gates

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose

Close the deterministic gaps that allowed structurally valid but incomplete
tasks and stale generated views to pass `pgk check`, while keeping PGK a
standard-library, file-based toolkit.

## Owner
Codex

## Scope

- Put the governed-task execution and closure protocol in generated `AGENTS.md`.
- Add type-aware lifecycle rules and an atomic `pgk transition` command.
- Enforce terminal task/bug chain, evidence, file, Git-reference, and generated-view checks.
- Resolve single-commit finalization with a stable `record-commit` Git sentinel.
- Add a conflict-safe governed-project Kit upgrade preview/apply path.
- Add focused regressions and update the accepted design, usage, workflow, and conventions.
- Do not add business-semantic inference, a database, a daemon, network access, or model calls.

## Files

- `src/project_governance/{models,records,checks,cli,scaffold}.py`
- `src/project_governance/upgrade.py`
- `src/project_governance/templates/{task,bug,verification}.md`
- `skills/project-governance-kit/SKILL.md`
- `docs/{WORKFLOW,project-conventions,usage}.md`
- `docs/design/2026-09-04-project-governance-kit-v0.1-design.zh-CN.md`
- task, status, generated views, verification, and focused tests.

## Acceptance

- AC-1: Generated `AGENTS.md` requires task-by-task acceptance review and states that batch authorization does not waive acceptance.
- AC-2: `pgk transition` rejects illegal transitions and refuses terminal task/bug status when deterministic gates fail.
- AC-3: Terminal task/bug records require declared fields, accepted upstream records, a reciprocal terminal verification, valid literal file paths, and a traceable head commit.
- AC-4: Verification evidence with stable `AC-*` IDs must cover every matching task acceptance ID; legacy free-form records remain readable.
- AC-5: `pgk check` detects stale generated indexes/BOARD and uses the correct path in marker errors.
- AC-6: `record-commit` supports one-commit finalization without stale `pending-*` placeholders.
- AC-7: Existing behavior remains standard-library only and focused plus full regression tests pass.
- AC-8: `pgk upgrade` previews every managed change, preserves project-owned content,
  refuses conflicting or unsupported upgrades without partial writes, and updates
  `kit_version` only after the governed contract upgrade succeeds.

## Evidence

VER-006 completed all eight acceptance checks.
- AC-1: VER-006 confirms the generated Agent closure protocol.
- AC-2: VER-006 confirms illegal and blocked transitions.
- AC-3: VER-006 confirms terminal chain, files, and Git reference gates.
- AC-4: VER-006 confirms stable AC outcome/evidence mapping and legacy compatibility.
- AC-5: VER-006 confirms stale generated-view and marker-path checks.
- AC-6: VER-006 confirms record-commit behavior.
- AC-7: VER-006 confirms standard-library boundaries and full regression evidence.
- AC-8: VER-006 confirms the governed-project upgrade preview/apply path, conflict refusal, custom-section preservation, rollback, team-private paths, and FundAgent dry-run behavior.

## Changes

Terminal gates and governed-project upgrade support are implemented. The
upgrade path is local, versioned, conflict-safe, and does not modify the
FundAgent trial.

## Blockers

None.

## Next action

Review the AC-8 evidence and decide whether to authorize the repository commit.

## Git
branch: codex/task-019-terminal-gates
worktree: C:/Users/31800/.codex/worktrees/task-019-terminal-gates/project-kit
base_commit: 12c2714
head_commit: record-commit

## Handoff

<!-- PGK_HANDOFF_START -->
<!-- PGK_HANDOFF_END -->
