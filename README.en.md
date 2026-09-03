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

Common commands:

```text
pgk init       create missing governance files
pgk adopt      inspect an existing project (read-only)
pgk doctor     inspect project governance health
pgk check      validate documents, links, and status
pgk new        create a governance record
pgk index      update the work index
pgk handoff    update task handoff information
```

## Status

The current version is the pre-release `0.1.0.dev0`. The toolkit repository
dogfoods its own governance architecture, and TouzhiAgent is its first
external trial project.

## Documentation

- [Documentation index](docs/INDEX.md)
- [v0.1 requirements](docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.md)
- [v0.1 design](docs/design/2026-09-02-project-governance-kit-v0.1-design.md)
- [Verification record](docs/verification/VER-000-bootstrap.md)
