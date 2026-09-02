# Project structure

The project is a Python package that treats governance documents as a first-
class product surface.

```text
src/project_governance/
├── cli.py          # argparse command entry points
├── config.py       # project configuration and profiles
├── documents.py    # metadata, templates, and record creation
├── checks.py       # read-only repository validation
├── git_context.py  # safe Git inspection
└── handoff.py      # task handoff updates
```

The `templates/` package data is copied into target projects by `pgk init` and
`pgk new`. The CLI never becomes a runtime dependency of the target project's
business code.

## Document boundaries

- `docs/requirements/`: accepted product intent and acceptance criteria;
- `docs/design/`: architecture and implementation design;
- `docs/decisions/`: durable decisions with alternatives and consequences;
- `docs/plans/`: milestone or implementation plans;
- `docs/work/`: active tasks and meaningful bugs;
- `docs/verification/`: evidence-backed validation and acceptance records;
- `docs/operations/`: runbooks, incidents, and postmortems when a project runs
  a service.

