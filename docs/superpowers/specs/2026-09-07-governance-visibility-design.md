# Governance Record Visibility Design

> Status: accepted. The user approved this specification before implementation.

## Goal

Allow a team to use complete Project Governance Kit records for internal
collaboration while preventing internal requirements, design history, Agent
logs, Bug analysis, Review notes, and handoffs from being published with a
public project.

## Design principles

- Governance visibility is independent of the Lite/Standard/Strict profile and
  the Agent collaboration mode.
- A Git repository's private/public setting is an external deployment choice;
  the Kit must not pretend it can enforce that setting without a platform API.
- Internal records and public project documentation have different audiences
  and different publication rules.
- Existing records are never silently deleted, moved, or rewritten.
- The core Kit remains local and offline; it does not call GitHub, GitLab, or
  other remote APIs.

## Visibility modes

### team-private

The canonical team repository is private. Complete governance records are
tracked in that private repository so team members and Agents can collaborate
through Git. A public release must be produced from a sanitized copy or a
separate public repository; changing the repository visibility alone is not a
supported publication workflow.

### hybrid

The project has a public code/document surface and a private governance
surface. Public README, usage, API, and release documents remain in the public
repository. Complete governance records are stored in a private governance
repository or an explicitly private local path configured by the project.

### public

Governance records are intentionally tracked and published with the project.
This is suitable for teaching, governance examples, or projects where the
development process is itself public.

## Configuration contract

The project configuration gains independent visibility fields:

```toml
profile = "standard"
collaboration_mode = "sequential-agents"
visibility = "team-private"
governance_dir = ".pgk"
public_docs_dir = "docs/public"
```

`visibility` values are `team-private`, `hybrid`, and `public`.

## v0.1 implementation scope

- Parse and validate the visibility configuration.
- Initialize the configured governance directory and public documentation
  directory without overwriting existing files.
- Ensure the private governance directory is represented in local Git ignore
  configuration when it is not intended for the public repository.
- Make checks report inconsistent visibility configuration, missing ignore
  rules, or governance records placed in a public path.
- Keep public README and usage documentation synchronized with the mode.
- Provide a dry-run/reporting path before any migration or publication action.

## Explicitly deferred

- GitHub/GitLab repository visibility API changes;
- automatic repository splitting or history rewriting;
- automatic public release creation;
- secret scanning as a replacement for publication review;
- remote governance repository synchronization;
- deletion or migration of existing governance files without a reviewed plan.

## Publication safety

The Kit must warn that `.gitignore` is not a historical privacy boundary. If a
governance file was previously committed to a public repository, removing it
from the working tree does not remove old commits, forks, clones, caches, or
copies. Publication requires a separate sanitized source or an explicit
history-cleaning process outside the core Kit.

## Acceptance criteria

- A team-private project can keep complete governance records in a private
  canonical repository without treating them as public documentation.
- A hybrid project clearly separates public docs from private governance data.
- A public project can intentionally keep governance records visible.
- Visibility does not change profile or collaboration-mode behavior.
- No core command changes GitHub/GitLab visibility or performs remote writes.
- Existing files are preserved and any migration is previewable before writes.
