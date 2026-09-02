# Project status

```yaml
status: bootstrap_in_progress
version: 0.1.0.dev0
active_task: TASK-000-bootstrap
owner: root
updated: 2026-09-02
```

## Current scope

The repository is establishing the v0.1 governance contract and a minimal
Python CLI. The toolkit is agent-first and remains readable and usable without
any specific model provider or issue tracker.

## Known constraints

- v0.1 uses Python 3.11+ and the standard library at runtime;
- GitHub integration is link-only in v0.1;
- no automatic commit, push, merge, deletion, or model-provider call;
- TouzhiAgent is an external trial, not a source of business rules for this kit.

## Next action

Complete the v0.1 requirements/design review, then implement the smallest
CLI slice with tests and run the toolkit's own checks against this repository.

