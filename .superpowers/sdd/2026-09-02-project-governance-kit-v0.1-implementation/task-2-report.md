# Task 2 report: read-only checks and Git context

## Implemented

- `project_governance.checks.run_checks` validates Markdown frontmatter,
  duplicate IDs (including records with another invalid field), allowed enum
  statuses, relative local Markdown links, and required baseline files.
- Results are frozen, deterministically ordered, and JSON serializable through
  `CheckResult.as_dict()`.
- `project_governance.git_context.inspect_git` reads branch, HEAD, porcelain
  worktree state, and recent commit hashes using Git subprocesses only.

## Evidence

- Focused tests: 3 passed.
- Full suite: 9 passed.
- `git diff --check`: passed.
- Pytest required workspace-local `--basetemp .pytest-tmp` because the default
  Windows temp directory was inaccessible; this is an environment limitation,
  not a product failure.
