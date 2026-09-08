# Project Governance Kit v0.2 migration implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended when executing inline) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不破坏 v0.1 新项目初始化和用户授权边界的前提下，实现已有项目的补齐模式、迁移方案、批准门禁、非破坏文档副本和可验证的 MIG 记录链。

**Architecture:** 在现有 scaffold/records/checks/cli 边界上增加 migration 模块。扫描器只读并输出确定性候选；规划器把候选写入 `MIG-*`；批准器只改变迁移记录状态；应用器只复制明确批准的 Markdown/纯文本并逐项记录结果；检查器验证来源、哈希、目标、索引和状态，不执行 Git 或远程动作。

**Tech Stack:** Python 3.11+、标准库、`argparse`、`pathlib`、`hashlib`、`re`、现有 frontmatter/records/checks 模块、pytest。

**Spec:** `docs/requirements/2026-09-07-project-governance-kit-v0.2-migration-requirements.zh-CN.md`; `docs/design/2026-09-07-project-governance-kit-v0.2-migration-design.zh-CN.md`

## Global Constraints

- v0.2 是迁移功能的首个版本，不回写 v0.1 验收范围。
- 第一版只自动处理 Markdown、Markdown 变体和 UTF-8 纯文本；其他格式只报告。
- 迁移默认保留原文件并生成治理副本，不保存额外原文快照。
- 不覆盖、移动、重命名、删除或合并原文件和人工修改过的治理副本。
- 生成的治理副本初始状态必须是 `draft`；迁移工具不得推导 `accepted`、`verified` 或 `done`。
- 相同源路径和哈希重复运行必须幂等；源变化、目标存在或目标脏写入必须报告冲突。
- 未明确批准的 MIG 条目不得写入治理副本；失败条目不得回滚其他成功条目。
- 核心 CLI 不执行 `git init`、commit、push、PR、merge、tag、release 或删除。
- 不写入密钥、密码、证书、账号配置、完整模型载荷或未脱敏运行日志。
- 受保护 Git/远程动作需要用户逐次授权；本计划中的 commit 步骤只有在用户明确批准后才能执行。

---

### Task 1: Extend record schema and existing-project scaffold modes

**Files:**
- Modify: `src/project_governance/models.py`
- Modify: `src/project_governance/frontmatter.py`
- Modify: `src/project_governance/records.py`
- Modify: `src/project_governance/templates.py`
- Modify: `src/project_governance/scaffold.py`
- Create: `src/project_governance/templates/migration.md`
- Test: `tests/test_migration_schema.py`
- Modify: `tests/test_scaffold.py`

**Interfaces:**
- Add `RecordType.MIGRATION = "migration"` and map it to `docs/migrations/`.
- Extend `RECORD_ID_PATTERN`, `RECORD_PREFIXES`, `RECORD_DIRECTORIES`, `RECORD_INDEXES` and template type lists with `MIG-*`/`migration`.
- Keep `parse_frontmatter()` backward compatible: it must continue ignoring unknown metadata fields while preserving all existing required-field validation.
- Change `init_project(root, *, project_name=None, profile="standard", mode="new", dry_run=False)` so `mode` accepts `"new"` and `"supplement"`; default `"new"` preserves v0.1 behavior.
- In `mode="supplement"`, create `docs/STATUS.md` with `project_stage: adoption_review` only when the file is missing; skip and preserve an existing status file byte-for-byte.
- Add `docs/migrations/INDEX.md` and `docs/templates/migration.md` to the standard generated skeleton. The migration template must include Purpose, Owner, Scope, Scan, Items, Approval, Evidence, Changes, Blockers, Next action, Git, and Handoff sections.

- [ ] **Step 1: Write failing schema and scaffold tests**

```python
def test_migration_record_type_and_directory(tmp_path: Path):
    init_project(tmp_path)
    path = create_record(tmp_path, "migration", "MIG-001", "Initial migration")
    assert path.relative_to(tmp_path).as_posix() == "docs/migrations/MIG-001-initial-migration.md"
    metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    assert metadata.type is RecordType.MIGRATION


def test_supplement_mode_uses_adoption_review_without_overwriting_status(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    assert "project_stage: adoption_review" in (tmp_path / "docs/STATUS.md").read_text(encoding="utf-8")
    status = tmp_path / "status-project"
    status.mkdir()
    (status / "docs").mkdir()
    (status / "docs/STATUS.md").write_text("project_stage: maintenance\n", encoding="utf-8")
    init_project(status, mode="supplement")
    assert (status / "docs/STATUS.md").read_text(encoding="utf-8") == "project_stage: maintenance\n"
```

- [ ] **Step 2: Run the focused tests and verify they fail**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task1 tests/test_migration_schema.py tests/test_scaffold.py -q`

Expected: failure because the migration record type, migration directory and `mode="supplement"` are not implemented.

- [ ] **Step 3: Implement the schema and scaffold changes**

Use the existing enum/dictionary boundaries. Do not add a second record parser. The migration template must use the same frontmatter renderer and safe record ID validation as all other record types. Add the `mode` argument without changing callers that omit it.

- [ ] **Step 4: Run the focused tests and the existing scaffold suite**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task1b tests/test_migration_schema.py tests/test_scaffold.py -q`

Expected: PASS, including all pre-existing scaffold tests.

- [ ] **Step 5: Commit only after user authorization**

Prepare `git add src/project_governance/models.py src/project_governance/frontmatter.py src/project_governance/records.py src/project_governance/templates.py src/project_governance/scaffold.py src/project_governance/templates/migration.md tests/test_migration_schema.py tests/test_scaffold.py` and the message `feat: add migration record and supplement scaffold mode`. Do not run `git commit` without matching user authorization.

### Task 2: Build deterministic adoption scanning and candidate classification

**Files:**
- Create: `src/project_governance/migration.py`
- Modify: `src/project_governance/scaffold.py`
- Modify: `src/project_governance/config.py`
- Test: `tests/test_migration_scan.py`

**Interfaces:**
- Define immutable `MigrationCandidate` with fields `source_path: str`, `source_hash: str`, `source_format: str`, `suggested_type: str | None`, `confidence: str`, `reason: str`, `sensitive: bool`, `sensitive_reason: str | None`, `status: str = "candidate"`.
- Define `scan_project(root: str | Path, *, scan_roots: Sequence[str] | None = None, exclude_patterns: Sequence[str] | None = None) -> tuple[MigrationCandidate, ...]`.
- Extend `ProjectConfig` with `scan_roots: tuple[str, ...]` and `exclude_patterns: tuple[str, ...]`; when scan arguments are omitted, load these values from `.project-governance.toml`, falling back to the documented defaults.
- Reject scan roots and configured paths that resolve outside `root`; normalize every returned path to a project-relative POSIX path.
- Use UTF-8 reads only; unreadable files are returned as non-copyable candidates with a safe error category, not an exception that aborts the scan.
- Scan root-level `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` and configured/default documentation directories (`docs`, `doc`, `documentation`, `设计`, `需求`).
- Exclude `.git`, `.agent`, `.venv`, `node_modules`, `vendor`, `build`, `dist`, caches, runtime data, generated governance directories (`docs/requirements`, `docs/design`, `docs/decisions`, `docs/migrations`, `docs/work`, `docs/reviews`, `docs/verification`), `.env`, key/certificate/password/account filenames and files larger than 2 MiB.
- Restrict automatic candidates to `.md`, `.markdown`, and `.txt`; report other encountered documentation files as `suggested_type=None`, `status="needs_review"` without copying their contents.
- Classify path/name hints deterministically: PRD/requirements → requirement, TSD/architecture/design → design, ADR → decision, bug/issue → bug, task/todo → task; no hint or conflicting hints → `needs_review`/low confidence.
- Detect likely secrets by filename and content patterns (`password`, `secret`, `token`, private-key markers, certificate markers); never include matching content in the result.
- Exclude existing standard governance records from candidate discovery so a second scan does not migrate Kit-generated records.

- [ ] **Step 1: Write failing scanner tests**

```python
def test_scan_classifies_supported_files_and_excludes_generated_or_sensitive_files(tmp_path: Path):
    (tmp_path / "docs" / "coding").mkdir(parents=True)
    (tmp_path / "docs" / "coding" / "PRD.md").write_text("requirements", encoding="utf-8")
    (tmp_path / "docs" / "notes.txt").write_text("notes", encoding="utf-8")
    (tmp_path / "docs" / "secret.env").write_text("TOKEN=do-not-report", encoding="utf-8")
    (tmp_path / "docs" / "requirements").mkdir(parents=True)
    (tmp_path / "docs" / "requirements" / "REQ-001.md").write_text("generated", encoding="utf-8")
    candidates = scan_project(tmp_path, scan_roots=["docs/coding", "docs/notes.txt", "docs/secret.env"])
    by_path = {item.source_path: item for item in candidates}
    assert by_path["docs/coding/PRD.md"].suggested_type == "requirement"
    assert by_path["docs/coding/PRD.md"].confidence == "high"
    assert by_path["docs/notes.txt"].suggested_type is None
    assert not any(item.source_path.endswith("secret.env") for item in candidates)
    assert not any(item.source_path.endswith("REQ-001.md") for item in candidates)


def test_scan_is_deterministic_and_hashes_source_bytes(tmp_path: Path):
    document = tmp_path / "README.md"
    document.write_text("hello", encoding="utf-8")
    first = scan_project(tmp_path)
    second = scan_project(tmp_path)
    assert first == second
    assert len(first[0].source_hash) == 64
```

- [ ] **Step 2: Run the scanner tests to verify failure**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task2 tests/test_migration_scan.py -q`

Expected: failure because `scan_project` and `MigrationCandidate` do not exist.

- [ ] **Step 3: Implement scanner and extend the read-only adoption report**

Keep `adopt_project()` backward compatible for existing callers, but include a structured candidate summary in its serialized report or expose scanning through the migration command. All paths in results must be project-relative POSIX paths, sorted lexicographically. Use SHA-256 over source bytes.

- [ ] **Step 4: Run scanner, scaffold and CLI regression tests**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task2b tests/test_migration_scan.py tests/test_scaffold.py tests/test_cli.py -q`

Expected: PASS.

- [ ] **Step 5: Commit only after user authorization**

Prepare the scanner files and tests for review; do not run `git commit` without explicit authorization.

### Task 3: Generate MIG plans and implement explicit approval state

**Files:**
- Modify: `src/project_governance/migration.py`
- Modify: `src/project_governance/records.py`
- Modify: `src/project_governance/templates/migration.md`
- Test: `tests/test_migration_plan.py`

**Interfaces:**
- Define `create_migration_plan(root: str | Path, candidates: Sequence[MigrationCandidate], *, migration_id: str | None = None, scan_roots: Sequence[str] = (), exclude_patterns: Sequence[str] = (), dry_run: bool = False) -> Path`. A non-dry plan writes the MIG record, refreshes the migration/record indexes, and appends one `plan` activity event.
- Define immutable `MigrationEntry` and `MigrationPlan` models; `load_migration_plan(root: str | Path, migration_id: str) -> MigrationPlan` parses the fixed MIG item blocks and rejects malformed or duplicate item IDs.
- Define `approve_migration(root: str | Path, migration_id: str, *, item_ids: Sequence[str] | None = None, exclude_item_ids: Sequence[str] = ()) -> Path`. With `item_ids=None`, mark all eligible `candidate` items approved; with IDs supplied, mark only those items approved. `exclude_item_ids` marks selected candidate items `excluded`. Existing `needs_review`, `conflict`, `source_changed`, `applied` and `failed` items remain unchanged.
- Use stable batch IDs `MIG-001`, `MIG-002`, etc., selecting the first unused ID when none is supplied. Assign item IDs `ITEM-001`, `ITEM-002`, etc. in deterministic candidate order, and use target IDs `REQ-MIG-001-001`, `DES-MIG-001-002`, `ADR-MIG-001-003`, `TASK-MIG-001-004`, `BUG-MIG-001-005` only for supported classified items.
- Store each item in MIG body with `item_id`, `source_path`, `source_hash`, `source_format`, `target_id`, `target_path`, `suggested_type`, `confidence`, `reason`, `sensitive`, and `status` fields. Store `approval: pending|approved` in frontmatter/body.
- `create_migration_plan(..., dry_run=True)` returns the planned path and does not write files, indexes or activity entries.
- Reject unsafe or duplicate IDs through existing record validation. Never infer acceptance from source content.

- [ ] **Step 1: Write failing plan and approval tests**

```python
def test_plan_has_stable_targets_and_does_not_write_on_dry_run(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (
        MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "filename hint", False, None),
    )
    path = create_migration_plan(tmp_path, candidates, migration_id="MIG-001", dry_run=True)
    assert path.as_posix().endswith("docs/migrations/MIG-001-migration-plan.md")
    assert not path.exists()


def test_approve_changes_only_selected_items(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    candidates = (
        MigrationCandidate("README.md", "a" * 64, "markdown", "requirement", "high", "hint", False, None),
        MigrationCandidate("docs/notes.txt", "b" * 64, "text", None, "low", "no hint", False, None),
    )
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001", item_ids=["ITEM-001"])
    text = next((tmp_path / "docs/migrations").glob("MIG-001-*.md")).read_text(encoding="utf-8")
    assert "item_id: ITEM-001" in text and "status: approved" in text
    assert "item_id: ITEM-002" in text and "needs_review" in text
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task3 tests/test_migration_plan.py -q`

Expected: failure because plan persistence and approval updates are not implemented.

- [ ] **Step 3: Implement plan serialization and approval updates**

Use a deterministic Markdown table or fixed item blocks that can be parsed without a YAML dependency. Update only the MIG record and its activity event during approval. Do not generate governance copies in this task.

- [ ] **Step 4: Run migration plan, records and index tests**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task3b tests/test_migration_plan.py tests/test_records.py tests/test_records_commands.py -q`

Expected: PASS.

- [ ] **Step 5: Commit only after user authorization**

Prepare the plan/approval changes for review; do not run `git commit` without explicit authorization.

### Task 4: Apply approved items as non-destructive governance copies

**Files:**
- Modify: `src/project_governance/migration.py`
- Modify: `src/project_governance/records.py`
- Test: `tests/test_migration_apply.py`

**Interfaces:**
- Define `apply_migration(root: str | Path, migration_id: str, *, item_ids: Sequence[str] | None = None, dry_run: bool = False) -> MigrationApplyResult`.
- Define immutable `MigrationApplyResult` with `migration_id`, `applied`, `skipped`, `conflicts`, `failed`, `changed`, and `verification_paths` collections; expose `as_dict()` with JSON-safe values.
- Process only items whose status is `approved` (or the explicitly approved subset). Do not provide a force-all bypass.
- Before copying, require the source to exist, recompute its SHA-256, and compare it to the planned hash. A mismatch becomes `source_changed` and is not copied.
- Target paths are under the corresponding standard directory and use the stable target ID plus a safe slug. Existing target files are never overwritten; if their bytes equal the planned generated copy, classify the item as an idempotent `skipped`/`applied` result, otherwise classify it as `conflict` and leave it untouched.
- Generated copy format: standard Kit frontmatter with target metadata, `status: draft`, `migration_id`, `source_path`, `source_hash`, `source_format`, `migration_status: applied`, `confidence`, then a provenance note and the complete original source text between `PGK_SOURCE_BEGIN`/`PGK_SOURCE_END` markers. Do not semantically rewrite source content.
- A single item read/write error updates only that item to `failed` and continues with other approved items. Error text must be a short category/message without source content.
- On successful application update the MIG item to `applied`, refresh indexes, append one activity event, and return paths for verification. If every approved item is `applied` or idempotently skipped and there are no conflicts, failures or source changes, create `VER-MIG-001` (or the corresponding batch ID) with status `verified`, exact command evidence and a relation to the MIG record; never overwrite an existing project-owned verification record. Set the MIG batch to `verified` in this case; otherwise set it to `blocked` when actionable conflicts/failures remain.

- [ ] **Step 1: Write failing apply tests**

```python
def test_apply_requires_approval_and_preserves_source(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "README.md"
    source.write_text("original", encoding="utf-8")
    candidates = scan_project(tmp_path, scan_roots=["README.md"])
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    result = apply_migration(tmp_path, "MIG-001")
    assert not result.applied
    approve_migration(tmp_path, "MIG-001")
    result = apply_migration(tmp_path, "MIG-001")
    assert result.applied
    assert source.read_text(encoding="utf-8") == "original"
    target = next((tmp_path / "docs/requirements").glob("REQ-MIG-001-*.md"))
    assert "status: draft" in target.read_text(encoding="utf-8")
    assert "original" in target.read_text(encoding="utf-8")


def test_apply_reports_source_change_and_target_conflict_without_overwrite(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    source = tmp_path / "README.md"
    source.write_text("v1", encoding="utf-8")
    candidates = scan_project(tmp_path, scan_roots=["README.md"])
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    source.write_text("v2", encoding="utf-8")
    changed = apply_migration(tmp_path, "MIG-001")
    assert changed.changed
    assert not changed.applied
```

- [ ] **Step 2: Run the apply tests to verify failure**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task4 tests/test_migration_apply.py -q`

Expected: failure because `apply_migration` and result classification do not exist.

- [ ] **Step 3: Implement safe copy, hash checks, conflict handling and item-level updates**

Use exclusive creation (`open(..., "x")`) or an equivalent existence check plus a second check immediately before write. Never delete or overwrite source or target files. Keep the source path relative and normalize it to POSIX form.

- [ ] **Step 4: Run apply, plan, scaffold and checks regression tests**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task4b tests/test_migration_apply.py tests/test_migration_plan.py tests/test_scaffold.py tests/test_checks.py -q`

Expected: PASS.

- [ ] **Step 5: Commit only after user authorization**

Prepare the applier changes for review; do not run `git commit` without explicit authorization.

### Task 5: Add migration validation, project-stage checks and CLI commands

**Files:**
- Modify: `src/project_governance/checks.py`
- Modify: `src/project_governance/cli.py`
- Modify: `src/project_governance/__init__.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_governance_checks.py`
- Create: `tests/test_migration_cli.py`

**Interfaces:**
- Add `adoption_review` to `PROJECT_STAGES` and validate it like other project stages.
- Include the migration index in generated-index checks and `pgk index` output without removing existing index paths.
- Validate MIG records: valid `MIG-*` ID/type, required migration sections, item statuses from the allowed set, source existence, source hash format, target path safety, and applied-item target existence. Report stable codes such as `invalid_migration_item`, `missing_migration_source`, `migration_source_changed`, `migration_target_conflict`, and `unindexed_migration`.
- Preserve the existing `CheckResult` JSON shape and deterministic issue sorting.
- Extend `pgk init` with `--mode {new,supplement}`.
- Add nested commands:

```text
pgk migrate plan --root <project> [--scan-root PATH] [--exclude PATTERN] [--dry-run] [--json]
pgk migrate approve MIG-001 --root <project> [--item ITEM_ID ...] [--exclude-item ITEM_ID ...] [--json]
pgk migrate apply MIG-001 --root <project> [--item ITEM_ID ...] [--dry-run] [--json]
```

- `plan` is read-only when `--dry-run`; normal plan writes only the MIG record and activity/index records. `approve` changes only the selected MIG record. `apply` returns nonzero only for command-level errors; item conflicts and failures are represented in the JSON result and MIG record.
- No CLI path invokes subprocess Git mutation or any network API.

- [ ] **Step 1: Write failing check and CLI tests**

```python
def test_cli_migrate_plan_approve_apply_flow(tmp_path: Path, capsys):
    init_project(tmp_path, mode="supplement")
    (tmp_path / "README.md").write_text("requirements", encoding="utf-8")
    assert main(["migrate", "plan", "--root", str(tmp_path), "--json"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["migration_id"] == "MIG-001"
    assert main(["migrate", "apply", "MIG-001", "--root", str(tmp_path), "--json"]) == 0
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["applied"] == []
    assert main(["migrate", "approve", "MIG-001", "--root", str(tmp_path), "--json"]) == 0
    capsys.readouterr()
    assert main(["migrate", "apply", "MIG-001", "--root", str(tmp_path), "--json"]) == 0
    applied = json.loads(capsys.readouterr().out)
    assert applied["applied"]


def test_checks_accept_adoption_review_and_report_changed_migration_source(tmp_path: Path):
    init_project(tmp_path, mode="supplement")
    assert run_checks(tmp_path).ok
    source = tmp_path / "README.md"
    source.write_text("v1", encoding="utf-8")
    candidates = scan_project(tmp_path, scan_roots=["README.md"])
    create_migration_plan(tmp_path, candidates, migration_id="MIG-001")
    approve_migration(tmp_path, "MIG-001")
    source.write_text("v2", encoding="utf-8")
    result = run_checks(tmp_path)
    assert any(issue["code"] == "migration_source_changed" for issue in result.issues)
```

- [ ] **Step 2: Run the focused tests to verify failure**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task5 tests/test_migration_cli.py tests/test_cli.py tests/test_governance_checks.py -q`

Expected: failure because the nested commands, migration checks and `adoption_review` stage are not implemented.

- [ ] **Step 3: Implement checks and argparse dispatch**

Keep human output compact and JSON deterministic. Reuse `_emit`, `_root`, and existing command error handling. Do not make `approve` pretend to authenticate the human; its purpose is to persist the explicit approval command in the MIG record, while the Agent integration remains responsible for obtaining user confirmation.

- [ ] **Step 4: Run the complete CLI/check suite**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task5b tests/test_cli.py tests/test_checks.py tests/test_governance_checks.py tests/test_migration_cli.py -q`

Expected: PASS.

- [ ] **Step 5: Commit only after user authorization**

Prepare the check/CLI changes for review; do not run `git commit` without explicit authorization.

### Task 6: Complete documentation, fixture acceptance and v0.2 verification

**Files:**
- Modify: `docs/usage.md`
- Modify: `README.md`
- Modify: `docs/INDEX.md`
- Modify: `docs/STATUS.md`
- Modify: `docs/work/BOARD.md`
- Modify: `docs/work/tasks/TASK-011-implement-v0-2-existing-project-migration.md`
- Modify: `pyproject.toml`
- Create: `docs/verification/VER-002-v0-2-migration-mvp.md`
- Create: `tests/test_migration_acceptance.py`

**Interfaces:**
- Document supplement and migration flows in Chinese first, with concise English command labels where the existing guide is bilingual.
- Update `pyproject.toml` from `0.1.0.dev0` to `0.2.0.dev0` and update the README's current-version wording; preserve the historical v0.1 requirement/design links.
- Document that original files remain in place, `MIG-*` is a candidate plan, `approve` is required before `apply`, and unsupported/sensitive files are report-only.
- Add a fixture-based end-to-end test covering an existing Git project and a non-Git project: plan, no-op apply before approval, approval, copy, source preservation, index refresh, source-change detection, target conflict and `pgk check` evidence.
- Create VER-002 with exact commands, test count, compile check, `git diff --check`, fixture results, known Windows pytest temp-directory workaround if it recurs, and explicit statements of what remains externally unverified.
- Update TASK-011 from accepted to verified only after all code/tests/docs evidence is available. Keep v0.1 VER-001 unchanged.

- [ ] **Step 1: Write the acceptance fixture tests**

```python
def test_existing_project_migration_fixture_is_non_destructive(tmp_path: Path):
    project = tmp_path / "existing"
    project.mkdir()
    (project / "docs" / "coding").mkdir(parents=True)
    source = project / "docs" / "coding" / "PRD.md"
    source.write_text("legacy requirements", encoding="utf-8")
    before = source.read_bytes()
    init_project(project, mode="supplement")
    candidates = scan_project(project, scan_roots=["docs/coding"])
    create_migration_plan(project, candidates, migration_id="MIG-001")
    assert not apply_migration(project, "MIG-001").applied
    approve_migration(project, "MIG-001")
    result = apply_migration(project, "MIG-001")
    assert result.applied
    assert source.read_bytes() == before
    assert run_checks(project).ok
```

- [ ] **Step 2: Run the acceptance fixture before documentation updates**

Run: `py -3 -m pytest --basetemp .pytest-tmp-task6 tests/test_migration_acceptance.py -q`

Expected: PASS after Tasks 1–5 are complete.

- [ ] **Step 3: Update usage, README, indexes, status and verification records**

Use exact CLI examples that can run locally. Do not claim real remote GitHub/Issue/PR, model-provider, deployment, performance or long-running monitoring verification. Keep the v0.1 scope statement and VER-001 historical evidence intact.

- [ ] **Step 4: Run the full verification set**

Run:

```powershell
$tmp = Join-Path (Get-Location) '.pytest-tmp-final'
py -3 -m pytest --basetemp $tmp -q
py -3 -m compileall src
git diff --check
py -3 -m project_governance check --root . --json
```

Expected: all tests pass, compileall succeeds, diff check is clean, and the project check reports only any explicitly documented dirty-worktree condition.

- [ ] **Step 5: Record verification and handoff**

Write VER-002, update TASK-011 handoff with branch, HEAD, worktree, dirty state, test/compile/check evidence, unresolved external validation, and one next action. Update `docs/STATUS.md` and generated indexes only through their marked/generated paths.

- [ ] **Step 6: Commit only after user authorization**

Prepare the complete diff and proposed message `feat: add v0.2 existing-project migration MVP`. Do not commit, push, open a PR, merge, tag or release until the user explicitly authorizes the specific action and target.

## Plan self-review

- Requirement coverage: REQ-002 AC-01/03 are covered by Tasks 1–2; AC-02 by Task 1; AC-04/05 by Task 3; AC-06/07/11 by Task 4; AC-08/09/10 by Tasks 4–5; AC-12 by Task 6.
- v0.1 compatibility: the default `init_project(..., mode="new")`, existing record types, existing CLI commands and VER-001 are preserved; new migration records and indexes are additive.
- Safety: no task deletes, moves or overwrites source files; apply has no force bypass; Git/remote operations remain outside core CLI.
- Determinism: source paths, hashes, target IDs, item ordering, issue sorting and JSON output are explicitly defined.
- No placeholders or unresolved design choices remain in the plan.
