# Project status

```yaml
status: verified
version: 0.1.0.dev0
active_task: none
owner: root
updated: 2026-09-03
```

## Current scope

The v0.1 governance contract and minimal Python CLI are implemented. The
toolkit is agent-first and remains readable and usable without any specific
model provider or issue tracker.

## Known constraints

- v0.1 uses Python 3.11+ and the standard library at runtime;
- GitHub integration is link-only in v0.1;
- no automatic commit, push, merge, deletion, or model-provider call;
- TouzhiAgent is an external trial, not a source of business rules for this kit.

## Verification snapshot

- `pgk check --root . --json`: `ok=true`, no issues;
- editable package installation and `pgk --help`: passed;
- empty-project `pgk init`, `pgk check`, and `pgk new --dry-run`: passed;
- TouzhiAgent `pgk adopt`: read-only mapping report produced, no files changed;
- full test suite, compile check, and project-document validator: passed.

## Next action

Review the usage documentation and decide whether to start the first external
TouzhiAgent trial.
