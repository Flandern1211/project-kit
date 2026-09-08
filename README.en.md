# Project Governance Kit

[中文](README.md) | English

Project Governance Kit (`pgk`) is an agent-first, human-readable toolkit for
preserving project context across requirements, design, tasks, bugs,
verification, Git history, and cross-session handoffs.

The toolkit is independent of a project's programming language, framework,
issue tracker, or model provider. It generates ordinary Markdown/TOML files
and provides offline validation.

## Current scope

The current development version is `0.2.0.dev0`. It includes v0.1 new-project initialization and the v0.2 existing-project migration MVP.

v0.1 includes:

- initialize or inspect a project governance structure;
- create requirement, design, decision, task, bug, and verification records;
- validate document metadata, IDs, statuses, and local links;
- provide human-readable and JSON output for people and agents;
- inspect Git branches, commits, and worktree state;
- update a task's cross-session handoff section.

v0.2 includes:

- supplement an existing project with missing governance files;
- scan existing Markdown/plain-text documents and create a migration plan;
- create source-hashed governance drafts only after explicit approval;
- preserve original files and report sensitive content, conflicts, source changes, and failures.

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
pgk init --root C:\path\to\project --mode supplement
pgk migrate plan --root C:\path\to\project --json
pgk migrate approve MIG-001 --root C:\path\to\project --json
pgk migrate apply MIG-001 --root C:\path\to\project --json
```

Migration preserves the original files and creates `draft` copies under the standard governance directories. Unapproved items are not written, and conflicts never overwrite existing files.

Create a task and hand it between agents or sessions:

```powershell
pgk new task TASK-001 "Implement feature" --root . --status in_progress --related REQ-001
pgk handoff TASK-001 --root . --next-action "run integration tests" --verification "unit tests passed"
pgk check --root . --json
```

`pgk new` also supports `requirement`, `design`, `decision`, `task`, `bug`,
`review`, and `verification`. Write commands support `--dry-run`, and agent callers can use
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
pgk migrate    plan, approve, and apply document migration
```

## Status

The current version is the pre-release `0.2.0.dev0`. The toolkit repository
dogfoods its own governance architecture, and TouzhiAgent is its first
external trial project.

## Documentation

- [Documentation index](docs/INDEX.md)
- [Usage guide](docs/usage.md)
- [v0.1 requirements](docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.md) · [中文](docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.zh-CN.md)
- [v0.1 design](docs/design/2026-09-02-project-governance-kit-v0.1-design.md)
- [Verification record](docs/verification/VER-000-bootstrap.md)
