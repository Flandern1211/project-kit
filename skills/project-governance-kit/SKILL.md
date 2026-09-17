---
name: project-governance-kit
description: Use Project Governance Kit through natural-language conversation. Use this skill whenever the user wants to create, start, bootstrap, govern, adopt, or resume a software project with PGK; wants the Agent to handle pgk initialization; or wants to bring an existing repository under Project Governance Kit. Classify the project safely, run the local pgk CLI, create only draft requirements before user acceptance, and preserve all Git and migration authorization gates. Do not trigger merely to explain PGK, compare tools, or make an ordinary code change in a project that has not asked for PGK governance.
---

# Project Governance Kit Agent Entry

Act as the conversational interface to Project Governance Kit. The user should be able to describe
the project and make decisions while you handle deterministic `pgk` commands and repository records.
The user's instructions take precedence over this skill; target-repository `AGENTS.md` instructions
govern all work inside that repository.

This workflow requires a local `pgk` command or an accessible `project_governance` Python module.

## Start safely

1. Resolve the exact target root. Do not initialize an ambiguous directory.
2. Inspect the directory without changing it. Check for `.project-governance.toml`, `AGENTS.md`,
   Git metadata, code, and existing documents.
3. Confirm that `pgk` is available with `pgk --help`. If only repository source is available, use
   the equivalent `python -m project_governance --help`. If neither works, report the installation
   blocker and a local installation command; do not claim initialization succeeded.
4. Classify the target as `governed`, `existing`, `new`, or `unclear` using the rules below.

## Classify the project

### Governed

Treat a project as governed when it has `.project-governance.toml` and the expected governance
entry documents. Do not run `pgk init` again. Read, in order:

1. `AGENTS.md`;
2. `docs/INDEX.md` or the configured governance index;
3. `docs/project-structure.md`;
4. `docs/STATUS.md`;
5. records linked to the current task or the user's requested change.

Resume the active task when one exists. For new requested behavior, follow the repository's
requirement/design/task chain instead of inventing a shortcut.

### Existing

Treat a directory as an existing project when it contains code, project documents, or meaningful Git
history but no PGK configuration. Run only read-only discovery first:

```text
pgk adopt --root <root> --json
pgk doctor --root <root> --json
```

Summarize existing governance files, missing files, candidate mappings, sensitive findings, Git state,
and the recommended choice between supplement and migration. Stop for the user's confirmation. Do not
run `init --mode supplement`, `migrate approve`, or `migrate apply` merely because the user asked for
an assessment or said they eventually want PGK.

### New

Treat an empty directory, or a directory explicitly designated for a new project without existing
business content, as new. Ask only for information that materially affects initialization: the target
root, project name, and governance visibility when it is not already clear. Use Kit defaults for
profile and collaboration mode unless the user requests otherwise.

Preview before writing:

```text
pgk init --root <root> --project-name <name> --dry-run --json
```

When the user explicitly asked to create or start this new project with PGK, that request authorizes
creation of the missing governance files in the named root. It does not authorize Git initialization,
commit, push, PR, merge, tag, release, deletion, or remote permission changes.

Run initialization, then read the generated Agent contract and governance entry documents. Run
`pgk check --root <root> --json`. Create the next available requirement record with `status=draft`,
using the user's stated project goal as its title and content. Capture goals, scope, non-scope,
assumptions, open questions, and acceptance criteria without pretending uncertain details are facts.

Stop after presenting the draft requirement and ask the user to confirm or revise it. Do not create a
design, implementation task, or business code until the requirement is accepted.

### Unclear

If the root, existing-project status, or intended write location is genuinely ambiguous, ask one short
question that resolves the ambiguity. Continue read-only inspection while waiting when useful.

## Authorization boundaries

- Existing-project supplement and migration writes require confirmation after the read-only proposal.
- Migration apply handles only explicitly approved items and follows the target repository's records.
- `git init`, commit, push, PR, merge, tag, release, deletion, and remote changes retain their own
  authorization requirements. Never treat authorization for one action as authorization for another.
- Never overwrite existing project documents. Use PGK preview, conflict reporting, and proposal flows.

## Report back

Keep the response compact and state:

- classification: new, existing, governed, or unclear;
- read-only checks and local writes performed;
- current governance stage and any blocker;
- the single next user decision or next action.

The normal pause for a new project is requirement confirmation. The normal pause for an existing
project is adoption-plan confirmation.
