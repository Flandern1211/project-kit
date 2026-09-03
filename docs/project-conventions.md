# Project conventions

## Records

Use stable IDs such as `REQ-`, `DES-`, `ADR-`, `PLAN-`, `TASK-`, `BUG-`,
`VER-`, and `INC-`. Records use YAML frontmatter with `id`, `type`, `status`,
`created`, and `updated`.

The v0.1 lifecycle statuses are `draft`, `accepted`, `in_progress`, `blocked`,
`verified`, `done`, and `rejected`. A record may move to `verified` only when
its verification section names the evidence used.

The index links to records but does not duplicate their bodies. Meaningful
updates append a short timeline entry to the existing record. Do not create a
separate implementation log for every progress message.

## Git

`main` is an integration branch. A non-trivial task uses one short-lived
branch and one worktree when parallel work is active. A reviewer does not
silently modify the implementer's branch.

## Verification

Verification must name the command or inspection evidence used. A passing test
suite does not by itself prove external services, deployment, performance, or
long-running behavior.

## Security

Secrets, private data, complete model payloads, and unredacted runtime logs do
not belong in repository documents. The core toolkit performs local checks and
does not call external services in v0.1.
