# Project Governance Kit Agent Instructions

## Project boundary

Project Governance Kit provides reusable project-governance documents,
templates, safe repository checks, and agent handoff support. It does not
implement business functionality, replace Git, replace an issue tracker, or
provide a runtime logging service.

## Mandatory workflow

- Read `docs/INDEX.md` and `docs/STATUS.md` before starting work.
- Read the linked requirement and design record before changing behavior.
- Use one task record for every non-trivial change and keep its status current.
- Keep code, tests, and required documentation in the same change chain.
- Keep `docs/STATUS.md`, user-facing documentation, version configuration,
  and implemented behavior synchronized in that change chain.
- Run `pgk check` (or the equivalent Python module command) before handoff or
  pull request review.
- Do not mark work verified without test or inspection evidence.
- Do not overwrite existing project documents during adoption; show a proposal
  first.
- Do not commit credentials, API keys, private data, model payloads, or full
  chain-of-thought content.
- Do not commit directly to `main`; use a task branch and an isolated worktree
  when parallel work is active.

## Source of truth

Use this order when records disagree:

1. user and repository instructions;
2. accepted requirements;
3. accepted design and decision records;
4. code and test behavior as evidence;
5. plans, task notes, handoffs, and chat as coordination material.

If an implementation contradicts an accepted requirement, record the conflict
and stop the affected change until the requirement or design is resolved.

## Model-provider traffic

The core toolkit does not call model providers. If an Agent integration adds
model-provider traffic while working in this repository, it must follow the
active environment instruction and route it through
`http://127.0.0.1:7897`; it must not fall back to a direct provider connection.

## Read before acting

Read `AGENTS.md`, `docs/INDEX.md`, `docs/project-structure.md`, and
`docs/STATUS.md` before changing files. Then read the linked requirement,
design or decision, task or bug, review, and verification records that govern
the change.

## Architecture limits

Supported lifecycle RecordTypes are `requirement`, `design`, `decision`,
`task`, `bug`, `review`, `verification`, and `migration`.

Strict risk/security/release/runbook/incident/postmortem paths contain ordinary
control Markdown, not new RecordTypes. Do not add lifecycle frontmatter types
for them. Do not create new governance directories, records, statuses, or
business modules unless an accepted design and task authorize them. Unknown
business directories require an accepted design and task before use.

## Repository map

- `docs/requirements/`: product intent and acceptance criteria.
- `docs/design/`: accepted architecture and implementation design.
- `docs/decisions/`: durable decisions, alternatives, and consequences.
- `docs/work/tasks/`: scoped implementation tasks with owner, files, and evidence.
- `docs/work/bugs/`: reproducible defects and fix scope.
- `docs/reviews/`: review findings and verdicts.
- `docs/verification/`: evidence-backed validation.
- `docs/migrations/`: migration plans and outcomes; source files stay in place.
- `docs/activity/`: concise activity timeline, not a replacement for records.
- `docs/operations/runbooks/`, `docs/operations/incidents/`, `docs/operations/postmortems/`: operational control Markdown without lifecycle frontmatter.
- `docs/risk/`, `docs/security/`, `docs/releases/`: Strict control Markdown without lifecycle frontmatter.
- `docs/templates/`: supported record templates only.
- `docs/INDEX.md`, `docs/project-structure.md`, `docs/WORKFLOW.md`, `docs/project-conventions.md`, and `docs/STATUS.md`: navigation, structure, workflow, conventions, and current state.
- `docs/work/INDEX.md` and `docs/work/BOARD.md`: generated task and bug views.

See `docs/project-structure.md` for the detailed map, including root files,
`.agent/`, and optional plan directories. Plans, specs, handoffs, indexes,
boards, and activity are coordination material; lifecycle records are the
source of truth.

## Two-phase finalization

Complete records and code, run semantic checks, fill evidence, commit once, run
read-only clean-tree checks, and do not edit the repository after the clean-tree
check. Put post-commit output in the external experiment report or handoff.

