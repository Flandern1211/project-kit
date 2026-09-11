# Project conventions

## Records

Use stable IDs such as `REQ-`, `DES-`, `ADR-`, `TASK-`, `BUG-`, `REV-`, `VER-`,
and `MIG-`. The supported lifecycle RecordTypes are `requirement`, `design`,
`decision`, `task`, `bug`, `review`, `verification`, and `migration`. Records
use YAML frontmatter with `id`, `type`, `status`, `created`, and `updated`.

The v0.1 lifecycle statuses are `draft`, `accepted`, `in_progress`, `blocked`,
`verified`, `done`, and `rejected`. A record may move to `verified` only when
its verification section names the evidence used.

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

## Two-phase finalization

Complete records and code, run semantic checks, fill evidence, commit once, run
read-only clean-tree checks, and do not edit the repository after the clean-tree
check. Post-commit output belongs in the external experiment report or handoff.

## Security

Secrets, private data, complete model payloads, and unredacted runtime logs do
not belong in repository documents. The core toolkit performs local checks and
does not call external services in v0.1.
