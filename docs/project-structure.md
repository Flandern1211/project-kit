<!-- PGK_GENERATED: project-structure -->
# Project structure

The project is a Python package that treats governance documents as a first-
class product surface. The generated map below distinguishes Kit-owned
governance documents from project business content.

## Source package

`src/project_governance/` contains the standard-library Kit implementation.
The `templates/` package data is copied into target projects by `pgk init` and
`pgk new`; the CLI never becomes a runtime dependency of business code.

## Root files

- `AGENTS.md`: Agent contract and architecture limits; read it before acting.
- `README.md`: project entry point; link to documentation rather than copying records.
- `CONTRIBUTING.md`: contribution guidance; link non-trivial work to a task or bug.
- `CHANGELOG.md`: release-facing change summary, not a release record or verification record.
- `.project-governance.toml`: Kit profile and path configuration.
- `.gitignore`: local/generated exclusions; never use it to hide evidence.

## Governance documents

- `docs/INDEX.md`: navigation only; it does not replace record bodies.
- `docs/STATUS.md`: current stage, ownership, blocker, and next action.
- `docs/WORKFLOW.md`: lifecycle states and the two-phase finalization sequence.
- `docs/project-structure.md`: this detailed Kit-owned directory map.
- `docs/project-conventions.md`: record, Git, verification, and security conventions.
- `docs/requirements/`: product intent and acceptance criteria; use `requirement` records.
- `docs/design/`: architecture and implementation design; use `design` records.
- `docs/decisions/`: durable decisions, alternatives, and consequences; use `decision` records.
- `docs/work/tasks/`: scoped implementation tasks; use `task` records.
- `docs/work/bugs/`: reproducible defects and fix scope; use `bug` records.
- `docs/work/INDEX.md`: generated task and bug navigation.
- `docs/work/BOARD.md`: generated work status view.
- `docs/reviews/`: review findings and verdicts; use `review` records.
- `docs/verification/`: validation and acceptance evidence; use `verification` records.
- `docs/migrations/`: migration plans and outcomes; use `migration` records without moving source files.
- `docs/activity/`: concise activity timeline; it is coordination material.
- `docs/templates/`: templates for supported lifecycle records, not records themselves.

## Strict control documents

Strict `risk`, `security`, `release`, `runbook`, `incident`, and `postmortem`
documents are ordinary Markdown under their respective directories. They do
not use lifecycle frontmatter and do not add RecordTypes:

`pgk check` reports `unsupported_control_record_type` for a frontmatter-bearing
file in one of these Strict paths. Remove the lifecycle frontmatter and keep
the document as ordinary Markdown.

- `docs/risk/`: risk register and risk-control evidence.
- `docs/security/`: security controls, findings, and review evidence.
- `docs/releases/`: release notes and release evidence.
- `docs/operations/runbooks/`: repeatable operational procedures.
- `docs/operations/incidents/`: incident records and response timelines.
- `docs/operations/postmortems/`: learning and follow-up after incidents.

## Optional coordination paths

`docs/plans/`, `docs/superpowers/plans/`, and `docs/superpowers/specs/` may hold
plans or proposals. They do not become accepted lifecycle records until the
content is captured in the supported source-of-truth locations. `.agent/`
contains local session and handoff projections when used; it is not a
governance record and is ignored by default.

## Source of truth and boundaries

The supported lifecycle RecordTypes are `requirement`, `design`, `decision`,
`task`, `bug`, `review`, `verification`, and `migration`. Requirements,
designs, decisions, tasks, bugs, reviews, verification records, and migrations
are source of truth. Indexes, boards, activity, plans, specs, handoffs, and
chat are coordination material. Unknown business directories are not
pre-approved and require an accepted design and task.
