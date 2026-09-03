---
id: TASK-001
type: task
status: verified
created: 2026-09-03
updated: 2026-09-03
related:
---
# Add CLI usage documentation

## Purpose

Make the package usable by a new person or Agent without requiring them to
infer CLI arguments from source code.

## Scope

- add practical usage steps to both README files;
- add a detailed bilingual command reference;
- link the reference from the documentation index;
- verify all new local links with `pgk check`.

## Acceptance

- README files show installation, initialization, adoption, record creation,
  validation, and handoff examples;
- the detailed usage guide documents every v0.1 command and its safety behavior;
- Chinese and English README language links work;
- the toolkit's own checks remain clean.

## Evidence

- `pgk check --root . --json` returned `ok=true` with no issues;
- `D:\skills\bootstrap-project-governance\scripts\validate_project_docs.py .`
  returned 0 errors and 0 warnings;
- new-project flow executed in an isolated fixture: `pgk init` created the
  governance files, `pgk check` returned `ok=true`, `pgk new --dry-run` returned
  the planned record path, and real `pgk new` plus `pgk handoff` completed;
- README language links and all usage-guide links are present.

## Changes

- `README.md` and `README.en.md` now contain copyable usage examples;
- `docs/usage.md` documents installation, all v0.1 commands, JSON/dry-run,
  exit codes, safety boundaries, and the Agent handoff flow;
- `docs/INDEX.md` links the usage guide.

## Blockers

None.

## Next action

Review the usage guide and begin the first external TouzhiAgent trial.

## Handoff

<!-- PGK_HANDOFF_START -->
Status: verified
Branch: codex/bootstrap-v0.1
HEAD: d823f19ed660e95fbb946045bfc2fe836fd43caf
Worktree: dirty
Verification: 20 tests passed; pgk check ok; document validator 0 errors
Blockers: none
Next action: review the usage guide and begin the TouzhiAgent trial
<!-- PGK_HANDOFF_END -->
