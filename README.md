# Project Governance Kit

Project Governance Kit (`pgk`) is an agent-first, human-readable toolkit for
maintaining project context across requirements, design, implementation,
verification, Git history, and handoffs.

The toolkit is independent of a project's programming language, framework,
issue tracker, or model provider. It writes versioned Markdown and TOML into a
target repository and provides safe checks for document structure, links,
identifiers, and workflow state.

## v0.1 scope

- initialize or inspect a repository governance structure;
- create requirement, design, decision, task, bug, verification, and handoff records;
- validate document metadata, local links, identifiers, and project status;
- expose deterministic human-readable and JSON output for agents;
- read Git context without committing, pushing, merging, or deleting files.

GitHub Issues and pull requests remain optional discussion and review entry
points. The repository Markdown record is the durable source of truth.

## Development

This repository dogfoods its own governance rules. Start with:

```powershell
py -3 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python -m project_governance --help
```

The first external trial project is
[TouzhiAgent](C:/Users/31800/Documents/ChatGPT/TouzhiAgent).

## Status

The package is pre-release (`0.1.0.dev0`). The v0.1 contract is recorded in
the [requirements](docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.md)
and [design](docs/design/2026-09-02-project-governance-kit-v0.1-design.md)
documents.

