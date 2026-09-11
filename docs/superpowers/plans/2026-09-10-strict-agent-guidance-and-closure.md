# Strict Agent Guidance and Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make initialized Kit projects explain the complete governance map, prevent unsupported architecture expansion, classify environment failures correctly, and validate the same behavior through a new three-model Strict experiment.

**Architecture:** Keep the existing eight lifecycle RecordTypes and existing CLI commands. Improve the generated Agent contract and structure documentation, add explicit control-document boundary checks, enrich read-only diagnostics, and document a two-phase finalization sequence without adding automatic commits or new lifecycle types.

**Tech Stack:** Python 3.11+, standard library, argparse, Markdown, pytest, Git worktrees.

**Spec:** `docs/superpowers/specs/2026-09-10-strict-agent-guidance-and-closure-design.md`

## Global Constraints

- Do not add lifecycle RecordTypes for risk, security, release, runbook, incident, or postmortem documents.
- Keep Strict control documents as ordinary Markdown; never invent unsupported `type` values.
- Do not automatically commit, push, merge, open pull requests, publish releases, or delete user data.
- Do not standardize business formulas, fields, thresholds, or model choices in the experiment.
- The core Kit must not call a model provider; any external Agent traffic must use `http://127.0.0.1:7897` and never fall back direct.
- Every implementation change must include focused tests and the required documentation update in the same change chain.
- The final experiment must use isolated projects, Strict profile, sequential-agents mode, public visibility, and the same governance invariants for all models.

---

### Task 1: Define the Agent and document map

**Files:**
- Modify: `src/project_governance/scaffold.py:11-63`
- Modify: `AGENTS.md:1`
- Modify: `docs/INDEX.md:1`
- Modify: `docs/project-structure.md:1`
- Modify: `docs/WORKFLOW.md:1`
- Modify: `docs/project-conventions.md:1`
- Test: `tests/test_scaffold.py`

**Interfaces:**
- `init_project()` continues to return the current `ScaffoldResult` and create the same profile-dependent file set.
- Generated `AGENTS.md` gains a compact repository map and hard prohibitions.
- `docs/project-structure.md` becomes the detailed map for Kit-owned directories.

- [ ] **Step 1: Write failing guidance tests**

Add assertions to `tests/test_scaffold.py` that initialize a Strict fixture and require the generated `AGENTS.md` to contain the supported RecordTypes, the control-document rule, the unknown-directory rule, and each Kit-owned path below:

```python
guidance = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
for path in (
    "docs/requirements/", "docs/design/", "docs/decisions/",
    "docs/work/tasks/", "docs/work/bugs/", "docs/reviews/",
    "docs/verification/", "docs/migrations/", "docs/activity/",
    "docs/operations/runbooks/", "docs/operations/incidents/",
    "docs/operations/postmortems/", "docs/risk/", "docs/security/",
    "docs/releases/", "docs/templates/",
):
    assert path in guidance
assert "risk/security/release/runbook" in guidance
assert "Do not create" in guidance
```

Assert `docs/project-structure.md` is generated and linked by the generated `docs/INDEX.md`.

- [ ] **Step 2: Run the guidance tests and verify failure**

Run `python -m pytest tests/test_scaffold.py -q` with the worktree source on `PYTHONPATH`. Expect failure because the current scaffold does not generate the map.

- [ ] **Step 3: Update the generated Agent contract**

Replace the short `STANDARD_FILES["AGENTS.md"]` template with sections in this order:

```markdown
## Read before acting
Read `AGENTS.md`, `docs/INDEX.md`, `docs/project-structure.md`, and `docs/STATUS.md` before changing files.

## Architecture limits
Supported lifecycle RecordTypes are `requirement`, `design`, `decision`, `task`, `bug`, `review`, `verification`, and `migration`.
Strict `risk`, `security`, `release`, `runbook`, `incident`, and `postmortem` paths contain ordinary control Markdown, not new RecordTypes. Do not add frontmatter types for them.
Do not create new governance directories, records, statuses, or business modules unless an accepted design and task authorize them.

## Repository map
...

## State gates
...
```

The map must give each generated Kit-owned path one purpose and one restriction. It must state that unknown business directories require an accepted design.

- [ ] **Step 4: Generate the detailed structure map**

Add `docs/project-structure.md` to `STANDARD_FILES` with a generated marker and a table covering root files, every `docs/` directory, `.agent/`, optional plan directories, and the distinction between source-of-truth records and coordination material. Update the repository copy with the same contract and link it from `docs/INDEX.md`.

- [ ] **Step 5: Document finalization order**

Update the generated workflow and conventions to state: complete records and code, run semantic checks, fill evidence, commit once, run clean-tree checks, and do not edit the repository after the clean-tree check. Explain that post-commit output belongs in the external experiment report or handoff.

- [ ] **Step 6: Run the focused guidance tests**

Run `python -m pytest tests/test_scaffold.py -q`; expect all guidance assertions to pass.

- [ ] **Step 7: Commit the task**

Run:

```text
git add AGENTS.md docs/INDEX.md docs/project-structure.md docs/WORKFLOW.md docs/project-conventions.md src/project_governance/scaffold.py tests/test_scaffold.py
git commit -m "docs: explain governance structure to agents"
```

---

### Task 2: Enforce the existing control-document boundary

**Files:**
- Modify: `src/project_governance/checks.py:1-60`
- Modify: `src/project_governance/frontmatter.py:1-55` only if a typed error is needed
- Test: `tests/test_checks.py`
- Test: `tests/test_profiles.py`
- Modify: `docs/project-structure.md:1`

**Interfaces:**
- `run_checks(root)` retains its current `CheckResult` shape.
- A Strict control document with lifecycle frontmatter produces a clear governance issue explaining that control paths are ordinary Markdown.
- Existing valid core records continue to parse unchanged.

- [ ] **Step 1: Write the boundary regression test**

Create a Strict fixture, write `docs/risk/RISK-001.md` with `type: risk`, and assert the result is not `ok` and includes one issue whose message directs the Agent to use ordinary Markdown and not add a RecordType. Also assert a plain `docs/risk/RISK-001.md` without frontmatter remains accepted.

- [ ] **Step 2: Run the boundary test and verify failure**

Run `python -m pytest tests/test_checks.py tests/test_profiles.py -q`; expect the new typed-control case to fail against the current generic parser behavior.

- [ ] **Step 3: Add the explicit control-path check**

Define one internal tuple of normalized control prefixes and inspect frontmatter-bearing files under those prefixes before normal record parsing. Emit a deterministic issue such as `unsupported_control_record_type` with the message:

```text
Strict control documents are ordinary Markdown; remove lifecycle frontmatter and do not add a new RecordType
```

Do not add `risk`, `security`, `release`, `runbook`, `incident`, or `postmortem` to `RecordType`, `PROFILE_RECORD_TYPES`, `RECORD_PREFIXES`, or the `pgk new` choices.

- [ ] **Step 4: Run focused checks**

Run `python -m pytest tests/test_checks.py tests/test_profiles.py -q` and verify both the invalid and plain control-document cases.

- [ ] **Step 5: Commit the task**

Run `git add src/project_governance/checks.py tests/test_checks.py tests/test_profiles.py docs/project-structure.md` and commit with `fix: enforce strict control document boundary`.

---

### Task 3: Separate Git and environment failures

**Files:**
- Modify: `src/project_governance/git_context.py:1-70`
- Modify: `src/project_governance/checks.py:360-395`
- Modify: `src/project_governance/cli.py:120-152`
- Test: `tests/test_git_context.py`
- Test: `tests/test_cli.py`
- Test: `tests/test_checks.py`

**Interfaces:**
- `inspect_git(root)` still returns `GitContext` for readable repositories and still rejects nested non-repositories.
- Read failures expose a stable error code through a `GitInspectionError` subclass of `ValueError`.
- `pgk doctor --json` exposes `git.available`, `git.error_code`, and a read-only `preflight` object without changing existing successful fields.

- [ ] **Step 1: Write failing Git diagnostic tests**

Add a monkeypatched subprocess test that makes Git return a `dubious ownership` or permission error and assert `inspect_git()` raises `GitInspectionError` with `code == "git_unreadable"`. Add CLI assertions that doctor reports `git.error_code` and does not claim `git_not_initialized` for this case.

Add a clean initialized repository case asserting `preflight` reports the current Python executable, pytest availability, Git readability, and a clean/dirty worktree state.

- [ ] **Step 2: Run focused diagnostics tests and verify failure**

Run `python -m pytest tests/test_git_context.py tests/test_cli.py tests/test_checks.py -q`; expect the new error-code and preflight assertions to fail.

- [ ] **Step 3: Implement typed Git inspection errors**

Add a `GitInspectionError(ValueError)` carrying `code` and `message`. Map missing repository metadata to `git_not_initialized`; map subprocess permission, safe-directory, and unreadable errors to `git_unreadable` or `git_permission_denied`. Preserve the existing nested-repository guard.

- [ ] **Step 4: Propagate diagnostic state through checks and doctor**

Change `run_checks()` so it only emits `git_not_initialized` when the repository is actually absent. Emit `git_unreadable` when Git exists but inspection failed, and avoid deriving a false `git_state_mismatch` from an unverifiable Git state. Extend `_doctor()` with a read-only preflight payload based on `sys.executable`, `importlib.util.find_spec("pytest")`, Git inspection, and the current worktree state.

- [ ] **Step 5: Run focused diagnostics tests**

Run `python -m pytest tests/test_git_context.py tests/test_cli.py tests/test_checks.py -q` and verify all new classifications and legacy cases.

- [ ] **Step 6: Commit the task**

Run `git add src/project_governance/git_context.py src/project_governance/checks.py src/project_governance/cli.py tests/test_git_context.py tests/test_cli.py tests/test_checks.py` and commit with `fix: distinguish git and environment failures`.

---

### Task 4: Full Kit verification and experiment preparation

**Files:**
- Modify: `docs/STATUS.md`
- Modify: `docs/WORKFLOW.md`
- Modify: `docs/project-conventions.md`
- Create: external experiment root `D:/Project/pgk/_test/run-20260910-strict-guidance-experiment/`
- Create: one report per model and one aggregate audit report outside the Kit source tree

**Interfaces:**
- The Kit branch remains isolated at `D:/Project/project-kit/.worktrees/strict-agent-guidance`.
- The experiment invokes the modified package from this worktree, not the stale globally installed package.

- [ ] **Step 1: Run the full Kit suite**

Run `python -m pytest -q --basetemp <writable-temp>` from the isolated worktree, then `python -m compileall -q src tests`, and `git diff --check`.

- [ ] **Step 2: Run local governance checks**

Run `python -m project_governance check --root <worktree> --json` and `python -m project_governance doctor --root <worktree> --json` with the worktree `src` on `PYTHONPATH`. Resolve only regressions caused by this change.

- [ ] **Step 3: Record the experiment protocol**

Create the new experiment root with three isolated child projects. Use the exact shared setup:

```text
git init
pgk init --profile strict --mode new --collaboration-mode sequential-agents --visibility public
```

Use one identical governance prompt for all models. Permit each project to choose its own fund-risk field names, formulas, thresholds, implementation files, and test count. Require the same state gates, supported RecordTypes, no extra directories, no remote actions, and local task-branch commits.

- [ ] **Step 4: Run Phase 1 gate checks**

Require each model to read generated `AGENTS.md`, `docs/INDEX.md`, `docs/project-structure.md`, and `docs/STATUS.md`; create only a draft `REQ-001`; and stop before design, task, code, or tests. Capture branch, commit, worktree, and `pgk check` output.

- [ ] **Step 5: Run Phase 2 implementation and closure**

After explicit requirement acceptance, require each model to create accepted `DES-001`, `TASK-001`, code, tests, usage docs, review, verification, and Strict control Markdown. Require the two-phase finalization order and a final clean commit. Do not let the controller edit a child project during the autonomous run.

- [ ] **Step 6: Perform the independent audit**

For each child, inspect the actual files and commit history, rerun read-only checks, and classify only against shared invariants:

```text
PASS
PASS_CONTROLLER_ASSISTED
FAIL_GOVERNANCE
BLOCKED_ENVIRONMENT
```

Do not rank the models. Distinguish the Agent-owned result from any controller intervention.

- [ ] **Step 7: Commit the final Kit documentation**

After all final repository edits, run the clean-tree checks once more, store their output in the external aggregate report, and commit the documentation-only change without editing the repository afterward.

---

## Final review checklist

- [ ] `AGENTS.md` is concise enough to read but contains every Kit-owned path and hard architecture boundary.
- [ ] `docs/project-structure.md` carries the detailed explanations without duplicating record bodies.
- [ ] No new lifecycle RecordType or automatic protected action was introduced.
- [ ] Unsupported control frontmatter receives an actionable error.
- [ ] Git unreadable, Git uninitialized, dirty, and clean states are distinct.
- [ ] Existing tests and new focused tests pass.
- [ ] The new three-model experiment uses the modified Kit and the same governance invariants.
- [ ] The aggregate report identifies controller assistance and environment blocks separately from Agent behavior.
