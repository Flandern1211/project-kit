# Strict Agent Guidance and Closure Design

## Goal

Make a newly initialized Project Governance Kit project explain its complete
governance directory model to Agents, constrain them to the existing Kit
schema, and make environment failures and final evidence distinguishable during
future multi-Agent experiments.

## Context

The Strict gate experiment showed that the requirement gate worked across all
runs, while later outcomes diverged for governance reasons. One run created
unsupported `risk`, `security`, `release`, and `runbook` record types because
Strict initialized those directories without explaining that they are not
core lifecycle RecordTypes. Other runs reached a valid implementation but
needed controller-assisted document finalization. Some Agent environments also
could not execute Python, write test temporary directories, or read Git.

## Scope

### Included

- Expand the generated `AGENTS.md` with a concise but complete map of Kit-owned
  files and directories.
- Expand the repository documentation map with purpose, lifecycle, and allowed
  use for each Kit-owned documentation area.
- Explicitly state the current supported RecordTypes and forbid Agents from
  inventing new RecordTypes, directories, statuses, or governance artifacts.
- Define Strict risk, security, release, runbook, incident, and postmortem
  documents as ordinary control Markdown under the current schema. They must
  not use unsupported `type` values.
- Add regression checks for the generated guidance and the unsupported-type
  boundary.
- Improve read-only Git diagnostics so an unreadable repository is not reported
  as an uninitialized repository.
- Add an environment preflight result that can classify an experiment as
  blocked by its runtime or permissions before implementation evidence is
  evaluated.
- Document a two-phase finalization protocol: semantic validation before
  commit, then clean-tree validation after commit without further repository
  edits.
- Repeat the same Strict, isolated, three-model fund-risk experiment in a new
  experiment directory after the Kit changes are verified.

### Excluded

- Adding new lifecycle RecordTypes for risk, security, release, runbook,
  incident, or postmortem documents.
- Automatically creating commits, pushing, merging, opening pull requests,
  publishing releases, or deleting user data.
- Standardizing the business formulas, fields, or thresholds across Agents.
- Ranking models by quality or architecture adherence.
- Calling any model provider from the core Kit.

## Design

### Layered Agent guidance

The generated `AGENTS.md` is the first-level contract. It contains project
boundary, non-negotiable gates, supported RecordTypes, a one-line map of every
Kit-owned directory, the Strict control-document rule, and links to the full
documentation map. It does not duplicate every record field or business rule.

`docs/project-structure.md` is the detailed map. Each Kit-owned directory is
described by purpose, authoritative content, lifecycle behavior, creation
condition, and forbidden substitutions. `docs/INDEX.md` remains navigation;
it does not become a second copy of record bodies.

Business-specific directories are not enumerated as pre-approved locations.
They must be introduced by an accepted design and task. This makes the map
complete for Kit-owned structure without allowing an Agent to treat an unknown
directory as automatically authorized.

### Existing schema boundary

The implementation continues to use the current lifecycle RecordTypes:
`requirement`, `design`, `decision`, `task`, `bug`, `review`, `verification`,
and `migration`. Strict control directories remain ordinary Markdown and are
validated by their directory documentation and links, not by invented
frontmatter types.

The Agent instructions must say that a perceived need for a new record type or
directory is a blocker requiring a requirements/design decision. The Agent may
propose the extension in a record, but may not implement it as part of the
current task.

### Environment and Git diagnostics

The read-only health output distinguishes these states:

- Git is not initialized;
- Git exists but cannot be read because of permissions or safe-directory
  policy;
- Git is readable and the worktree is dirty;
- Git is readable and the worktree is clean.

The preflight result also reports the executable paths and writable locations
used for Python, pytest, pgk, the repository, and test temporary data. A
failed preflight is an environment-blocked result, not a failed governance
implementation.

### Finalization protocol

Agents finish in this order:

1. Complete all records, source files, tests, and documentation.
2. Run semantic checks while changes are uncommitted.
3. Fill final evidence and terminal statuses.
4. Commit the complete task branch.
5. Run read-only clean-tree `pgk check` and `pgk doctor`.
6. Store post-commit command output in the external experiment report or
   handoff; do not edit the committed repository after the clean-tree check.

Terminal records cannot claim evidence that was collected before their last
document edit. If final clean-tree verification fails, the task remains
`in_progress` or `blocked`.

### Experiment attribution

The next experiment records both repository outcome and ownership of the
closure:

- `PASS`: the Agent completed the full chain and clean commit independently;
- `PASS_CONTROLLER_ASSISTED`: the final repository is valid but the controller
  changed records or committed on the Agent's behalf;
- `FAIL_GOVERNANCE`: the Agent left a resolvable governance defect;
- `BLOCKED_ENVIRONMENT`: the required runtime or permissions were unavailable.

These are classifications, not model rankings.

## Acceptance criteria

- A fresh Strict project gives an Agent an understandable map of all
  Kit-owned directories and document roles in `AGENTS.md`.
- The guidance explicitly prevents unsupported frontmatter types and
  unauthorized directory expansion.
- Existing project behavior and RecordTypes remain compatible.
- Regression tests cover guidance generation, schema boundaries, Git error
  classification, and environment preflight output.
- The new three-model experiment uses the same Strict profile, collaboration
  mode, visibility, phase gates, and no-remote-action boundary.
- Business choices may differ per run, but every run is evaluated against the
  same governance invariants.
- The final report distinguishes Agent-owned completion, controller assistance,
  governance failure, and environment blocking.

## Verification plan

- Run the existing focused and full Kit test suites in the isolated worktree.
- Run compile and diff checks.
- Run the new guidance/schema/diagnostic tests.
- Initialize three fresh experiment projects with the same Strict setup.
- Run Phase 1 requirement-gate tests before any implementation.
- Run Phase 2 implementation and evidence closure independently for each model.
- Perform a read-only audit against the same invariant checklist.
- Confirm the main checkout remains unchanged and no provider traffic bypasses
  `http://127.0.0.1:7897`.
