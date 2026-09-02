---
id: DES-001
type: design
status: accepted
created: 2026-09-02
updated: 2026-09-02
related:
  - REQ-001
---

# Project Governance Kit v0.1 Design

- Status: accepted for initial implementation
- Version: 0.1
- Date: 2026-09-02
- Requirement: [v0.1 requirements](../requirements/2026-09-02-project-governance-kit-v0.1-requirements.md)

## 1. Architecture

The kit has five layers:

1. **Core models** define configuration, document metadata, result objects, and
   lifecycle values.
2. **Document services** parse frontmatter, render templates, create records,
   and update task handoff sections.
3. **Checks** perform read-only validation of files, links, IDs, statuses, and
   Git context.
4. **CLI** exposes deterministic human and JSON interfaces using `argparse`.
5. **Adapters** are deferred extension points for issue trackers and Agent
   hosts; v0.1 includes no network adapter.

The target repository remains self-contained. The CLI writes ordinary Markdown
and TOML files; it does not maintain a hidden database.

## 2. Target repository contract

The standard profile creates:

```text
AGENTS.md
CONTRIBUTING.md
CHANGELOG.md
.project-governance.toml
docs/
├── INDEX.md
├── STATUS.md
├── project-structure.md
├── project-conventions.md
├── requirements/
├── design/
├── decisions/
├── plans/
├── work/
│   ├── INDEX.md
│   ├── tasks/
│   └── bugs/
├── verification/
└── operations/
```

Existing files are never overwritten by initialization. Adoption reports can
map existing structures such as a project's PRD/TSD folders to these logical
roles without forcing a rename.

## 3. Record format

Record Markdown uses a small YAML frontmatter block:

```yaml
---
id: TASK-001
type: task
status: in_progress
created: 2026-09-02
updated: 2026-09-02
related:
  - REQ-001
---
```

The body contains purpose, scope, acceptance, evidence, changes, blockers,
next action, and (for tasks) a handoff section. The parser intentionally
supports only the subset needed by the toolkit; it does not attempt to be a
general YAML implementation.

## 4. Safety model

- read-only commands (`doctor`, `check`) never modify files;
- write commands refuse to overwrite a file unless an explicit future version
  adds a reviewed migration mode;
- `--dry-run` shows planned writes;
- Git operations are subprocess reads only;
- external URLs and credentials are never contacted by the core CLI;
- errors identify the file and field that need attention.

## 5. Self-hosting

This repository uses the same structure it generates. `TASK-000-bootstrap` is
the initial task. The implementation plan is linked from `docs/INDEX.md`, and
the final verification record must cite the actual commands and results.

## 6. Deferred compatibility

GitHub Issue/PR links, Agent-specific skills, language-specific test commands,
and organization-level dashboards will be implemented as adapters only after
the core document contract has been exercised on TouzhiAgent and at least one
other project type.
