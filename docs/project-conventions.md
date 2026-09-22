# Project conventions

## Records

Use stable IDs such as `REQ-`, `DES-`, `ADR-`, `TASK-`, `BUG-`, `REV-`, `VER-`,
and `MIG-`. The supported lifecycle RecordTypes are `requirement`, `design`,
`decision`, `task`, `bug`, `review`, `verification`, and `migration`. Records
use YAML frontmatter with `id`, `type`, `status`, `created`, and `updated`.

The lifecycle statuses are `draft`, `accepted`, `in_progress`, `in_review`,
`blocked`, `verified`, `done`, `rejected`, and `superseded`. Record types have
different legal transitions; use `pgk transition` rather than editing formal
status by hand. A task or bug may move to a terminal state only when its
terminal-v2 contract and reciprocal verification pass deterministic checks. Legacy records without the marker remain readable and are upgraded only before a new formal terminal transition.

The index links to records but does not duplicate their bodies. Meaningful
updates append a short timeline entry to the existing record. Do not create a
separate implementation log for every progress message.

Strict risk, security, release, runbook, incident, and postmortem documents are
ordinary Markdown. Do not add lifecycle frontmatter or invent a RecordType for
them. Unknown governance directories, records, statuses, and business modules
require an accepted design and task.

## Git

`main` is an integration branch. A non-trivial task uses one short-lived
branch and one worktree when parallel work is active. A reviewer does not
silently modify the implementer's branch.

## Verification

Verification must name the command or inspection evidence used. A passing test
suite does not by itself prove external services, deployment, performance, or
long-running behavior.
New task, bug, and verification records use stable `AC-*` identifiers. Every
terminal acceptance ID must have both an outcome and evidence in the reciprocal
verification record. Lite and Standard require verification; Strict also
requires a terminal review.

## Documentation consistency

Behavior and version changes must update the authoritative requirement/design
chain, task or bug record, `docs/STATUS.md`, user-facing documentation, and
version configuration in the same change chain. Historical verification keeps
the evidence captured at that time; current-state documents must not repeat an
obsolete branch, version, blocker, or implementation status.

For Project Governance Kit itself, `pgk check` compares the package version
with `.project-governance.toml`, `docs/STATUS.md`, `README.md`, and
`README.en.md`. A mismatch is a release and handoff blocker.

## Kit upgrades

For an already governed project, run `pgk upgrade --dry-run --json` before
adopting a newer Kit contract. Review every file and conflict, then use
`pgk upgrade --apply`; never change only `kit_version`. The upgrade preserves
historical records and project-owned sections, and advances configuration only
after all managed contract files are written successfully.

## Two-phase finalization

Complete records and code, run semantic checks, fill evidence, use
`head_commit: record-commit`, commit once, then run read-only clean-tree checks.
Do not put predicted commit or push state in current-state documents. Exact
post-commit output belongs in the external experiment report or handoff.

## Security

Secrets, private data, complete model payloads, and unredacted runtime logs do
not belong in repository documents. The core toolkit performs local checks and
does not call external services in v0.1.
