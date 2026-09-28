# Changelog

## Unreleased

- Bootstrap the self-governed Project Governance Kit repository.
- Add an Agent-first Codex Skill for conversational new-project initialization,
  existing-project adoption review, and governed-project resume flows.
- Validate repository Skill metadata separately from lifecycle frontmatter and
  ignore generated Skill evaluation workspaces.
- Make the Agent-first Skill's trigger, input, workflow, output, and acceptance
  contracts explicit in the runtime instructions.
- Localize the Agent-first Skill body and Codex UI prompt for Chinese use, with
  a concise discovery description.
- Add type-aware `pgk transition` lifecycle gates, stable `AC-*` acceptance to
  verification mapping, and deterministic terminal task/bug checks.
- Detect stale generated indexes and boards, validate terminal Git references,
  and support one-commit finalization through `record-commit`.
- Preserve legacy record readability while applying the `terminal-v2`
  contract to newly generated task, bug, and verification records.
- Add conflict-safe `pgk upgrade` preview/apply for governed projects, with
  managed-section merges, atomic writes, rollback, and version-last updates.
- Stage record creation, generated-view refresh, formal transitions, and
  handoff updates together; restore earlier targets after a failed write and
  retain recovery backups if rollback also fails.
- Honor configured governance roots in public initialization, adoption reports,
  and migration plan/apply/verification; reject invalid directory settings and
  block dirty migration targets even when their contents match generated copies.
