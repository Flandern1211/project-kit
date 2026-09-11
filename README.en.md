# Project Governance Kit

[中文](README.md) | English

Project Governance Kit (`pgk`) is an agent-first, human-readable toolkit for
preserving project context across requirements, design, tasks, bugs,
verification, Git history, and cross-session handoffs.

The toolkit is independent of a project's programming language, framework,
issue tracker, or model provider. It generates ordinary Markdown/TOML files
and provides offline validation.

## v0.1 scope

- initialize or inspect a project governance structure;
- create requirement, design, decision, task, bug, and verification records;
- validate document metadata, IDs, statuses, and local links;
- provide human-readable and JSON output for people and agents;
- inspect Git branches, commits, and worktree state;
- update a task's cross-session handoff section.

Governance profiles are `lite`, `standard`, and `strict`; they control the
depth of documentation and checks. Collaboration mode is independent of the
profile. v0.1 supports `single-agent` and `sequential-agents`; parallel Agent
coordination is deferred.

Governance visibility is independent and can be `team-private`, `hybrid`, or
`public`. Teams should keep complete governance records in a private Git
repository; public releases should use a reviewed sanitized copy or a separate
public repository. The Kit does not change GitHub permissions or rewrite
existing history.

GitHub Issues and pull requests remain discussion, review, and merge entry
points. Repository Markdown is the durable source of truth.

## Development

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python -m project_governance --help
```

## Usage

From a new project root, initialize the governance files and validate them:

```powershell
pgk init --root . --project-name MyProject
pgk check --root .
```

Choose a governance profile and, when needed, sequential handoffs:

```powershell
pgk init --root . --profile lite
pgk init --root . --profile standard --collaboration-mode sequential-agents
pgk init --root . --profile strict
pgk init --root . --profile standard --visibility team-private
pgk init --root . --profile standard --visibility hybrid
```

Lite creates the core requirements, task, bug, and verification structure;
Standard creates the complete governance skeleton; Strict adds risk, security,
and release indexes.

Recommended first-agent flow: read `AGENTS.md`, `docs/INDEX.md`, and
`docs/STATUS.md`, then run `pgk doctor --root . --json`. After the user accepts
the requirements, create the REQ → DES/ADR → TASK → REVIEW → VER records and
run `pgk check` plus `pgk handoff` before pausing or handing off. `git init`,
commit, push, Issue/PR, merge, tag, release, and deletion are protected actions
that remain user-confirmed; the Kit never performs them automatically.

For an existing project, inspect it first with read-only commands:

```powershell
pgk adopt --root C:\path\to\project --json
pgk doctor --root C:\path\to\project
```

Create a task and hand it between agents or sessions:

```powershell
pgk new task TASK-001 "Implement feature" --root . --status in_progress --related REQ-001
pgk handoff TASK-001 --root . --next-action "run integration tests" --verification "unit tests passed"
pgk check --root . --json
```

`pgk new` also supports `requirement`, `design`, `decision`, `task`, `bug`,
`review`, `verification`, and `migration`. Write commands support `--dry-run`, and agent callers can use
`--json`. See the [usage guide](docs/usage.md) for complete arguments,
statuses, and collaboration flow.

Common commands:

```text
pgk init       create missing governance files
pgk adopt      inspect an existing project (read-only)
pgk doctor     inspect project governance health
pgk check      validate documents, links, and status
pgk new        create a governance record
pgk index      update the work index
pgk handoff    update task handoff information
pgk migrate    plan, approve, and apply existing-document migration
```

## Status

The current version is the pre-release `0.2.0.dev0`. The toolkit repository
dogfoods its own governance architecture, and TouzhiAgent is its first
external trial project.

v0.2 includes the existing-project supplement and document migration MVP:

```powershell
pgk init --root C:\path\to\project --mode supplement
pgk migrate plan --root C:\path\to\project --json
pgk migrate approve MIG-001 --root C:\path\to\project --json
pgk migrate apply MIG-001 --root C:\path\to\project --json
```

Migration preserves originals and creates source-hashed `draft` governance copies. Unapproved items are not written, and conflicts or sensitive content are never copied or overwritten.
Resolvable local Markdown links are rewritten for the copied location; missing targets remain unchanged for human review.

## Documentation

- [Documentation index](docs/INDEX.md)
- [Usage guide](docs/usage.md)
- [v0.1 requirements](docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.md) · [中文权威基线](docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.zh-CN.md)
- [v0.1 accepted design](docs/design/2026-09-04-project-governance-kit-v0.1-design.zh-CN.md)
- [v0.2 migration requirements](docs/requirements/2026-09-07-project-governance-kit-v0.2-migration-requirements.zh-CN.md)
- [v0.2 migration design](docs/design/2026-09-07-project-governance-kit-v0.2-migration-design.zh-CN.md)
- [v0.2 migration verification](docs/verification/VER-002-v0-2-migration-mvp.md)
