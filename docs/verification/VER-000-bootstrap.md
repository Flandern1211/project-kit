---
id: VER-000
type: verification
status: verified
created: 2026-09-02
updated: 2026-09-03
related:
  - TASK-000
---

# Bootstrap verification

## Scope

Verify that the toolkit can validate its own governance documents and that the
v0.1 CLI behavior is covered by automated tests.

## Evidence

- `py -3 -m pytest -o addopts='' -q` — 20 passed;
- `py -3 -m compileall -q src tests` — passed;
- `git diff --check` — passed;
- `D:\skills\bootstrap-project-governance\scripts\validate_project_docs.py .` — 0 errors, 0 warnings;
- editable install with `.venv\Scripts\python.exe -m pip install --no-deps -e .` — passed;
- `.venv\Scripts\pgk.exe check --root . --json` — `ok=true`, no issues;
- empty fixture: `pgk init` created 10 files, `pgk check` returned `ok=true`, and
  `pgk new ... --dry-run` returned a planned path without writing it;
- `.venv\Scripts\pgk.exe adopt --root C:\Users\31800\Documents\ChatGPT\TouzhiAgent --json`
  — reported 3 existing governance files, 4 legacy mappings, and 7 missing
  standard files; no external project files were modified.

## Unverified boundaries

GitHub API mutation, model-provider integrations, runtime log collection,
performance, deployment, and long-running multi-agent operation remain outside
the v0.1 core validation.
