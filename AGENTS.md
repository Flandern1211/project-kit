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

