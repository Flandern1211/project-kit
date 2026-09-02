---
id: ADR-0001
type: decision
status: accepted
created: 2026-09-02
updated: 2026-09-02
---

# Repository Markdown is the durable task record

## Context

Agents need to resume work across sessions and machines. GitHub Issues are
useful for discussion but are external to a checkout and may be unavailable or
stale.

## Decision

Use one Markdown task or Bug record in the project repository as the durable
source of truth. Link the corresponding GitHub Issue and Pull Request from the
record when they exist.

## Consequences

- the project remains recoverable from its checkout;
- Git versions the requirements, decisions, and handoffs together with code;
- the Issue and PR do not need to duplicate the full project context;
- the CLI can validate records offline;
- teams must update the task record in the same change chain as the code.

## Revisit condition

Revisit this decision if a project requires an external system to be the
authoritative audit store or if repository access is intentionally unavailable
to its Agents.

