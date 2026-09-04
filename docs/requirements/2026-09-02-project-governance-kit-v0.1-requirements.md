---
id: REQ-001
type: requirement
status: accepted
created: 2026-09-02
updated: 2026-09-03
related:
  - REQ-001-ZH
---

# Project Governance Kit v0.1 Requirements

> This document is the English translation of the [Chinese v0.1 requirement baseline](2026-09-02-project-governance-kit-v0.1-requirements.zh-CN.md), accepted by the user on 2026-09-03. If the two languages differ, the Chinese baseline is authoritative.

- Document status: accepted
- Kit version: 0.1
- Revision date: 2026-09-03

## 1. Product goal

Project Governance Kit is a general document-centered development-governance
architecture. It initializes a complete, traceable, collaborative document and
Git structure for a new project so that users, different Agents, and different
sessions follow the same rules for requirements, design, implementation,
verification, handoff, and maintenance.

It reduces process risks rather than solving a particular business domain:
lost context, duplicated work, scope drift, unapproved designs treated as fact,
code/document divergence, missing verification evidence, and unreliable Agent
handoffs.

## 2. v0.1 scope

### 2.1 Target projects

v0.1 is required to support new-project initialization only. Migration,
consolidation, and automatic historical-document organization for existing
projects are deferred.

### 2.2 Document-driven development

After initialization, the user discusses project requirements with an Agent.
Requirements, designs, tasks, bugs, reviews, verification, and handoffs are
stored as versioned documents in the project repository. They provide shared
context across Agents, sessions, and people without depending on one chat.

### 2.3 Visualization

v0.1 uses Git-trackable Markdown tables, indexes, and Mermaid diagrams to show
project state, workflow nodes, and document relationships. It does not require
a web administration interface or hosted collaboration service.

### 2.4 Git collaboration

The project uses Git for code and governance documents. An implementable task
normally maps to one task branch. Parallel Agents use isolated worktrees and
record branch, worktree, owner, and file scope in the task record.

## 3. Initialization output

Initialization creates at least the following files and directories in a new
project. Every directory has an index or placeholder so Git can track it:

```text
AGENTS.md
README.md
CONTRIBUTING.md
CHANGELOG.md
.gitignore
.project-governance.toml
docs/
├── INDEX.md
├── STATUS.md
├── WORKFLOW.md
├── templates/
│   ├── INDEX.md
│   ├── requirement.md
│   ├── design.md
│   ├── decision.md
│   ├── task.md
│   ├── bug.md
│   ├── review.md
│   └── verification.md
├── requirements/
│   └── INDEX.md
├── design/
│   └── INDEX.md
├── decisions/
│   └── INDEX.md
├── work/
│   ├── BOARD.md
│   ├── tasks/
│   │   └── INDEX.md
│   └── bugs/
│       └── INDEX.md
├── reviews/
│   └── INDEX.md
├── verification/
│   └── INDEX.md
├── activity/
│   └── ACTIVITY.md
└── operations/
    ├── runbooks/
    │   └── INDEX.md
    ├── incidents/
    │   └── INDEX.md
    └── postmortems/
        └── INDEX.md
```

`operations/` is a pre-created placeholder structure. Records are required
there only when the project runs a service or has an operational event.
Runtime logs are managed by the project logging system and are separate from
development activity records.

Initialization establishes the structure and rules but does not invent
business requirements, technical choices, or acceptance conclusions.

### 3.1 Git initialization paths

- Existing Git repository: the Kit creates governance files for the normal
  user-controlled Git workflow and does not commit them automatically.
- No Git repository: the Kit reports `git_not_initialized`; an Agent must obtain
  user confirmation before running `git init`, and still cannot commit without
  separate authorization.
- User declines `git init`: the document structure may be created, but project
  state remains `git_not_initialized` and verified development cannot begin.

The core `pgk init` command does not run `git init`, commit, push, merge, or
remote operations by default.

## 4. Document records and authority

### 4.1 Record types

- `REQ-*`: user goals, scope, exclusions, assumptions, and acceptance criteria;
- `DES-*`: technical, data, API, security, or interface design;
- `ADR-*`: durable architecture or governance decisions;
- `TASK-*`: product or engineering tasks;
- `BUG-*`: reproducible problem, impact, reproduction, and repair;
- `REVIEW-*`: code/document review, reviewer, base/head revisions, findings,
  and verdict;
- `VER-*`: test, inspection, human acceptance, and external verification
  evidence.

Every record contains at least `id`, `type`, `status`, `created`, `updated`,
and `related`. Task, bug, review, and verification records also contain the
applicable owner, scope, evidence, Git references, blockers, and next action.

### 4.2 Activity record

`docs/activity/ACTIVITY.md` records important governance actions and state
transitions with this stable format:

```text
timestamp | actor | action | record_id | git_ref | result
```

It records events such as requirement creation/acceptance, task start, review,
verification, handoff, and closure. It does not record chain-of-thought, full
chat history, every command, or raw terminal output.

## 5. Agent development rules

### 5.1 Before any governed action

The Agent reads, in order:

1. `AGENTS.md`;
2. `docs/INDEX.md`;
3. `docs/STATUS.md`;
4. requirements, designs, TASK/BUG, REVIEW, and verification records related
   to the current action;
5. current Git branch, HEAD, worktree status, and file ownership.

If required files are missing, links are broken, states conflict, or an
upstream record is not accepted, the Agent stops the action, records a blocker,
and asks the user instead of continuing silently.

### 5.2 Requirements discussion and acceptance

- User/Agent requirement discussions create a `REQ-*` draft.
- A draft identifies scope, exclusions, assumptions, open questions, and
  acceptance criteria.
- Only the user can confirm it for `accepted` status.
- Unaccepted requirements cannot authorize implementation.
- A changed requirement updates the authoritative record or creates an
  explicit revision; changing only chat content is insufficient.

### 5.3 Design, tasks, and implementation

- New-feature path: `REQ → DESIGN/ADR → TASK → CODE/TEST → REVIEW → VERIFICATION`.
- Bug path: `BUG → CODE/TEST → REVIEW → VERIFICATION`; link REQ/DES when needed.
- Architecture, API, data, or security boundary changes require a design or ADR.
- Every code or governance-document change links to a TASK/BUG or is explicitly
  identified as a requirement/design review action.
- An Agent does not present plans, guesses, or temporary choices as accepted
  design.

### 5.4 Verification, handoff, and closure

- A task requires repeatable test, check, or human-acceptance evidence before
  `verified` or `done`.
- A review record identifies base/head revisions, verdict, unresolved findings,
  and evidence.
- A handoff includes current work, completed and remaining work, branch, HEAD,
  worktree state, uncommitted changes, blockers, and one next action.
- A new Agent must be able to resume from project documents and Git state
  without reading the previous full chat.

### 5.5 Enforcement boundary

The Kit provides governance rules and violation reports through project-local
`AGENTS.md`, templates, state constraints, and `pgk check`. It cannot
technically intercept an arbitrary external Agent or user who ignores the
rules.

A compliant Agent integration must stop when state or authorization is
missing. A non-integrated Agent may be detected through document checks, but
the Kit does not claim to block every external command.

## 6. Git collaboration and user authorization

### 6.1 Local branches and worktrees

- After task acceptance, an Agent may create and record a local task branch.
- Default feature branch: `task/<TASK-ID>-<slug>`; default bug branch:
  `bug/<BUG-ID>-<slug>`. Prefixes are project-configurable.
- Parallel Agents use isolated worktrees under the default project-local
  `.worktrees/` directory.
- Serial single-Agent development requires a task branch but not another
  worktree.
- A task records `branch`, `worktree`, `owner`, and `files`; conflicting file
  scopes require the Agent to stop and report the conflict.
- Non-implementation records may use `N/A` or an upstream reference for
  branch/worktree/HEAD instead of inventing Git state.

### 6.2 Protected-action authorization

The following actions require explicit user confirmation by default:

- `git commit`;
- `git push`;
- creating, updating, closing, or replying to GitHub/GitLab/Plane Issues;
- creating, updating, closing, or replying to Pull Requests/Merge Requests;
- merge;
- creating or pushing a tag;
- publishing a release, package, or other public artifact;
- deleting a branch, worktree, or other potentially history/data-losing action.

Task- or session-level authorization removes repeated confirmation only when:

1. the action is named explicitly;
2. the target repository, branch, Issue/PR, or release target is explicit;
3. an expiry or task/session scope is explicit;
4. the user has not revoked the authorization;
5. the current action stays within that authorization.

Without matching authorization, the Agent may prepare a command, commit
message, or PR draft but may not execute it. Commit permission does not imply
push, PR, or merge permission, and permission for one task does not apply to
another task.

### 6.3 Evidence for protected/public actions

After a protected action, the task or review record stores the action, target,
authorization evidence, time, result, commit/link, and subsequent verification.
The core CLI does not directly call remote platforms; only an Agent integration
with matching authorization may perform the public action.

## 7. State and node visualization

Project stage and individual record state are separate:

- project stages: `initialized`, `requirements_discussion`,
  `requirements_review`, `active_development`, `maintenance`, and `blocked`;
- record states include at least `draft`, `accepted`, `in_progress`,
  `in_review`, `blocked`, `verified`, `done`, `rejected`, and `superseded`;
  each record type may restrict the subset it uses.

Multiple tasks, bugs, and worktrees may be active. `STATUS.md` describes the
global stage and current focus; `BOARD.md` shows all records.

### 7.1 Minimum visualization contract

- `docs/STATUS.md`: authoritative current global state; contains project stage,
  current requirement/design/task, owner, blockers, next action, and update time.
- `docs/work/BOARD.md`: columns `ID`, `type`, `status`, `owner`, `related`,
  `branch/worktree`, `verification`, `blocker`, and `next`.
- `docs/WORKFLOW.md`: Mermaid state diagram including entry into and recovery
  from `blocked`.
- `docs/INDEX.md` and directory indexes: unique links to records without body
  duplication.
- Record creation, state transitions, handoffs, reviews, and completed
  verification update the relevant indexes and activity record.
- `pgk check` validates indexing, links, and required fields.
- Non-implementation nodes use `N/A` or an upstream Git reference rather than
  fabricated branch/commit values.

## 8. Functional requirements

### FR-01 New-project initialization

The Kit creates the directories, indexes, templates, configuration, state, and
Agent rule files defined in Section 3. Existing files are not overwritten by
default.

### FR-02 Agent rule entry point

The Kit provides `AGENTS.md` and Agent-integration instructions requiring
Agents to read project documents, obey state gates, register tasks, preserve
verification evidence, and request authorization for protected actions.

### FR-03 Requirement-to-verification chains

The Kit supports and checks the feature path
`REQ → DESIGN/ADR → TASK → CODE/TEST → REVIEW → VERIFICATION` and bug path
`BUG → CODE/TEST → REVIEW → VERIFICATION`.

### FR-04 Records and activity indexes

The Kit provides indexes for requirements, designs, decisions, tasks, bugs,
reviews, verification, and important activity. Indexes navigate rather than
duplicate record bodies; activity logs contain governance events only.

### FR-05 Git collaboration

The Kit records relationships between tasks, branches, worktrees, commits,
reviews, merges, and public-action evidence. It reports dirty worktrees,
unregistered branches, conflicting file scopes, and missing record links.

### FR-06 User-authorization gate

The Kit provides authorization rules and check results usable by Agent
integrations. Without matching authorization, a compliant Agent integration
stops protected actions. The core CLI does not perform those actions.

### FR-07 Readability and recovery

A person or Agent can determine current stage, nodes, completed work, blockers,
authorization state, and next action from project documents and Git state.

## 9. Non-functional requirements

- Documents and Git are the durable source of truth, not chat context.
- Documents, indexes, state, authorization, and activity use stable,
  checkable formats.
- Initialization and checks do not overwrite existing files or delete history.
- The structure supports Python, Go, Node, Java, and other technology stacks.
- Generated content is human-readable and Agent-parseable.
- Repeated checks against the same state are deterministic.
- Secrets, passwords, private data, full model payloads, and chain-of-thought
  are not written to the repository.
- Runtime logs and development records remain separate.
- Important conclusions trace to requirements, designs, records, commits,
  tests, or human-acceptance evidence.

## 10. v0.1 acceptance criteria

- AC-01: initializing an empty new-project directory creates every required
  directory with Git-trackable indexes/placeholders.
- AC-02: initializing a new project that already uses Git does not auto-commit;
  the generated `AGENTS.md` guides an Agent's first action.
- AC-03: for a non-Git project, an Agent may run `git init` only after user
  confirmation; if declined, state remains `git_not_initialized` and verified
  development cannot begin.
- AC-04: the initialized project stage is `requirements_discussion` and no
  fabricated business requirements exist.
- AC-05: a requirement draft cannot authorize design/implementation until the
  user accepts it.
- AC-06: users and Agents can create linked REQ, DES, ADR, TASK, BUG, REVIEW,
  and VER records.
- AC-07: before implementation, an Agent checks upstream records/state and
  stops with a recorded blocker when acceptance is missing.
- AC-08: STATUS, BOARD, WORKFLOW, and ACTIVITY satisfy Section 7.1.
- AC-09: task, branch, worktree, and commit relationships are traceable, and
  conflicting file scopes are detectable.
- AC-10: without matching user authorization, a compliant Agent integration
  does not execute commit, push, Issue/PR, merge, tag, release, or deletion;
  the core CLI never executes these actions.
- AC-11: a handoff lets a new Agent continue without the prior full chat.
- AC-12: review and verification records contain base/head, verdict, findings,
  and evidence as applicable.
- AC-13: the Kit repository uses the same document, task, verification, and Git
  collaboration rules.
- AC-14: a newly created trial project can be initialized and checked without
  importing project-specific business rules.

## 11. Accepted defaults

- v0.1 initializes new projects only; existing-project adoption is deferred.
- Visualization uses Git-trackable Markdown, indexes, and Mermaid only.
- `pgk init` creates files only and does not run `git init`, commit, push,
  merge, or remote operations by default.
- Without Git, the Agent obtains user confirmation before running `git init`.
- An accepted task may create a local branch; only parallel development uses
  an isolated worktree by default.
- Commit, push, Issue/PR, merge, tag, release, and deletion default to
  per-action confirmation. Explicit task/session authorization names action,
  target, and expiry and does not expand to adjacent actions.
- Activity logs contain governance nodes, not every command or conversation.
- `operations/` is pre-created and populated only when applicable.
- Existing TouzhiAgent is not a v0.1 new-project initialization acceptance
  target.
