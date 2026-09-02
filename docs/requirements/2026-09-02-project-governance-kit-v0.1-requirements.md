---
id: REQ-001
type: requirement
status: accepted
created: 2026-09-02
updated: 2026-09-02
---

# Project Governance Kit v0.1 Requirements

- Status: accepted for initial implementation
- Version: 0.1
- Date: 2026-09-02

## 1. Goal

Provide an agent-first, human-readable toolkit that makes a software project
recoverable across Agent sessions, models, and contributors by standardizing
durable records, Git references, validation evidence, and handoffs.

## 2. Scope

The first version targets local Git repositories and produces versioned
Markdown plus a small project configuration file. It must work for projects in
different programming languages. The toolkit itself is implemented in Python
3.11+ with no runtime dependency beyond the standard library.

## 3. Functional requirements

### FR-01 Initialization

`pgk init` shall create only missing governance files for a selected profile,
report skipped existing files, and never overwrite an existing instruction or
project document.

### FR-02 Adoption and inspection

`pgk adopt` and `pgk doctor` shall inspect an existing repository and report
missing or mappable governance artifacts without writing by default.

### FR-03 Record creation

`pgk new` shall create requirement, design, decision, task, bug, and
verification records from templates. Each record shall have a unique ID,
document type, lifecycle status, dates, and links to related records.

### FR-04 Validation

`pgk check` shall validate supported frontmatter, duplicate IDs, allowed
statuses, local Markdown links, required baseline files, and basic repository
state. It shall return a non-zero exit code for errors and support stable JSON
output.

### FR-05 Handoff

`pgk handoff` shall update the handoff section of an existing task record with
the current branch, commit, worktree state, verification state, blockers, and
one explicitly supplied next action. It shall not capture secrets or full
terminal output.

### FR-06 Git context

The toolkit shall inspect branch, HEAD, worktree status, and recent commits
without committing, pushing, merging, resetting, or deleting files.

### FR-07 Self-validation

The toolkit repository shall use its own requirements, design, task, test,
verification, and handoff records. Its checks shall run against itself.

## 4. Non-functional requirements

- deterministic output for the same repository state;
- human-readable output by default and machine-readable `--json` output;
- explicit `--dry-run` for write-capable commands;
- safe failure with actionable messages;
- portable across Windows, macOS, and Linux;
- no credentials or model-provider traffic in the core CLI;
- generated files remain ordinary project files and do not require a central
  service.

## 5. Out of scope for v0.1

- automatic GitHub/GitLab/Plane API mutation;
- automatic commits, pushes, merges, or releases;
- web dashboards or a hosted coordination service;
- runtime log collection and storage;
- semantic approval of requirements or architecture;
- code generation and model-provider calls;
- project-specific business templates.

## 6. Acceptance criteria

- AC-01: an empty fixture repository can be initialized without errors;
- AC-02: an existing repository can be inspected without file changes;
- AC-03: all v0.1 record types can be generated with valid metadata;
- AC-04: checks detect duplicate IDs, invalid statuses, and broken local links;
- AC-05: handoff output includes Git state and a supplied next action;
- AC-06: `--json` output is parseable and stable for Agent callers;
- AC-07: the kit can run its own checks and tests;
- AC-08: TouzhiAgent can be inspected as an external trial without importing
  fund-specific rules into the toolkit.
