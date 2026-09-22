---
id: VER-006
type: verification
status: verified
created: 2026-09-22
updated: 2026-09-22
related:
  - TASK-019
---
# Terminal gate verification

<!-- PGK_CONTRACT: terminal-v2 -->

## Purpose
## Owner
Codex
## Scope
Validate every TASK-019 acceptance criterion against the current PGK source and documentation.
## Acceptance
- AC-1: Generated AGENTS.md contains task-by-task closure and batch-authorization limits.
- AC-2: Lifecycle and pgk transition reject illegal or incomplete terminal moves.
- AC-3: Terminal task/bug contracts validate upstream records, literal files, and Git references.
- AC-4: Reciprocal VER evidence covers every task AC ID, while legacy records remain readable.
- AC-5: pgk check reports generated-view drift and the correct marker path.
- AC-6: record-commit supports the single closing commit protocol.
- AC-7: The implementation remains standard-library only and passes the full regression suite.
- AC-8: Governed-project upgrade preview/apply is conflict-safe and preserves project-owned content.
## Evidence
- AC-1: `AGENTS.md`, generated scaffold text, and Skill guidance inspected; generated guidance states the closure protocol.
- AC-2: `tests/test_terminal_governance.py` covers illegal transitions, dry-run behavior, and terminal blocking.
- AC-3: Contract tests cover accepted upstream records, declared files, real commit IDs, and record-commit.
- AC-4: AC mapping tests cover missing outcomes/evidence; legacy records remain readable in the full check.
- AC-5: Stale BOARD/index and invalid marker-path tests pass.
- AC-6: Pre-commit dirty and post-commit record-commit tests pass.
- AC-7: Full pytest suite passes; compileall and `git diff --check` pass; no provider/network/database code was added.
- AC-8: `tests/test_upgrade.py` passes 7 focused tests covering read-only preview, apply, preserved `AGENTS.md` custom sections and history, customized-template zero-write refusal, unsupported versions, injected-write rollback, team-private paths, and CLI JSON/exit codes. `pgk upgrade --root D:\Project\FundAgent --dry-run --json` exits 0 with `from_version=0.2.0.dev0`, `to_version=0.2.0.dev1`, no conflicts, and 10 proposed changed paths; FundAgent files remain unchanged. Repository and installed Skill copies have identical SHA-256 hashes and both pass Codex `quick_validate.py`.
## Changes
## Blockers
None.
## Next action
Verification complete; the remaining protected action is the repository commit decision.
