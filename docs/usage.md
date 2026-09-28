# 使用说明 / Usage Guide

本文说明 Project Governance Kit（`pgk`）的实际使用方式。命令只管理
项目治理记录，不负责编写业务代码、运行项目本身或操作远程平台。

This guide explains how to use Project Governance Kit (`pgk`). The commands
manage governance records only; they do not write business code, run the
project itself, or mutate remote platforms.

## 0. 当前已实现能力 / Implemented capabilities

| 命令 | 当前实现 | 写入边界 | 人工审查重点 |
|---|---|---|---|
| `pgk init` | 新项目初始化、已有项目 `supplement` 补齐、Lite/Standard/Strict、single/sequential、team-private/hybrid/public | 只创建缺失文件；不覆盖已有文件 | profile、协作模式、visibility 和目标目录 |
| `pgk adopt` | 只读盘点已有治理文件、Git 状态、候选文档和敏感项 | 不写文件 | 候选类型、敏感内容和排除规则 |
| `pgk doctor` | 汇总 check、adoption、Git 和 Python/pytest/临时目录预检 | 只读 | 环境阻塞与治理问题必须分开判断 |
| `pgk check` | 检查基线、链接、frontmatter、ID、状态、终态合同、生成视图、STATUS 引用、配置、Kit 版本、Git 和迁移结果 | 只读；发现问题返回退出码 1 | 不得把结构完整误报为验收完成 |
| `pgk new` | 创建 requirement/design/decision/task/bug/review/verification/migration 记录 | 拒绝重复 ID 和覆盖；记录、视图、活动一并暂存和回滚；支持 `--dry-run` | 上游记录、owner、scope 和证据字段 |
| `pgk index` | 重建记录索引、工作索引和 BOARD | 只重写带 `PGK_GENERATED` 标记的视图；失败时回滚 | 记录是否完整入索引 |
| `pgk transition` | 校验并执行正式记录状态迁移；终态任务/缺陷强制验证 terminal-v2 合同 | 分阶段更新 frontmatter、生成视图和活动记录；失败时回滚；支持 `--dry-run` | 每个 `AC-*` 是否有 reciprocal VER 结果和证据 |
| `pgk upgrade` | 预览或应用已治理项目的版本化 Kit 合同升级 | 默认只读；仅 `--apply` 写入；冲突时零写入，配置最后更新 | 逐文件 diff/hash、项目自定义章节、来源版本和冲突 |
| `pgk handoff` | 更新 TASK/BUG 的受控 handoff 区块和活动记录 | 只写标记区；记录、视图、活动失败时回滚；不改变 frontmatter 状态 | branch、HEAD、dirty、未提交内容、阻塞和唯一下一步 |
| `pgk migrate` | 包含 `plan`、`approve`、`apply`：扫描、审查并执行文档迁移 | 原文件不移动、不删除；只应用明确批准的条目；脏目标阻断 | 来源、目标、哈希、敏感性、置信度、链接、冲突和 VER 证据 |

后续只规划两项扩展：并行 Agent 协作安全/worktree 管理，以及经任务级明确授权的本地
自动 commit。Web/托管后台、模型调用、复杂格式转换、语义改写、Git 历史清理、远程
权限修改、自动治理等级评估、通用外部平台集成、公开副本自动导出，以及自动
push/PR/merge/tag/release 均为产品非目标，不属于延期路线图。

## 1. 安装 / Install

在工具包仓库或已打包的发布版本中安装：

Install from this repository or a packaged release:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

安装后可使用 `pgk` 命令，也可以使用等价的模块入口：

After installation, use the `pgk` command or the equivalent module entry point:

```text
pgk --help
python -m project_governance --help
```

### 1.1 推荐的 Agent-first 使用方式 / Recommended Agent-first workflow

仓库提供 `skills/project-governance-kit/`。将该目录复制到 Codex 用户 Skill 目录
（默认 `%USERPROFILE%\.codex\skills\project-governance-kit`；自定义 `CODEX_HOME`
时使用其 `skills` 子目录）后，通常不需要再手工输入 PGK 命令。

The repository includes `skills/project-governance-kit/`. Copy it to the Codex
user skills directory (normally
`%USERPROFILE%\.codex\skills\project-governance-kit`, or the `skills` directory
under a custom `CODEX_HOME`). After that, normal use is conversational.

在本仓库根目录可以显式执行一次：

```powershell
$pgkCodexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$pgkSkillTarget = Join-Path $pgkCodexRoot 'skills\project-governance-kit'
New-Item -ItemType Directory -Force -Path $pgkSkillTarget | Out-Null
Copy-Item -Recurse -Force .\skills\project-governance-kit\* $pgkSkillTarget
```

这是用户级配置写入，应由用户明确执行或授权 Agent 执行。更新 Skill 时重新复制该目录。

新项目示例：

```text
在 D:\Projects\PocketLedger 用 PGK 创建一个项目。先初始化并和我确认需求，不要开始写业务代码。
```

已有项目示例：

```text
把 D:\Projects\legacy-orders 接入 PGK。先只读检查并展示方案，不要修改现有文件。
```

已治理项目示例：

```text
继续这个 PGK 项目的当前任务，先读取 STATUS 和关联记录恢复上下文。
```

Agent 会负责命令编排和治理记录，用户负责目标、需求确认和受保护动作授权。新项目正常
停在需求确认；已有项目正常停在接入方案确认。CLI 仍是确定性执行层和手工备用入口。

Skill 安装是一次性的本地配置动作，不由 `pgk init` 静默执行。核心 Kit 仍不调用模型
提供商或远程服务。

## 2. 新项目 / New project

进入目标项目根目录，创建缺失的治理文件：

From the target project root, create missing governance files:

```powershell
pgk init --root . --project-name MyProject
pgk check --root .
```

`init` 默认使用 `standard` profile 和 `single-agent` 协作模式。可按项目治理深度
选择 `lite`、`standard` 或 `strict`；v0.1 协作模式可选 `single-agent` 或
`sequential-agents`，并行模式暂不支持：

```powershell
pgk init --root . --profile lite
pgk init --root . --profile standard --collaboration-mode sequential-agents
pgk init --root . --profile strict
pgk init --root . --profile standard --visibility team-private
pgk init --root . --profile standard --visibility hybrid
```

Lite 只创建核心需求、任务和验证记录；Standard 创建完整治理骨架；Strict 在
Standard 基础上增加风险、安全和发布索引。它只创建不存在的文件；已有文件会
列在 `skipped` 中，不会被覆盖。预览写入而不修改文件：

`visibility` 独立于 profile：`team-private` 将完整治理记录放入 `.pgk/`，适合
私有团队仓库；`hybrid` 将完整治理记录放入 `.pgk/`，并创建 `docs/public/` 作为
公开文档入口；`public` 保持治理文档位于 `docs/`。Kit 不自动修改远程仓库权限，
也不自动删除或重写已有 Git 历史。

`public` 可以显式指定 `--governance-dir governance`，默认布局仍为 `docs/`。
`team-private`/`hybrid` 也可配置独立治理根；已治理项目的 `adopt`/`doctor`
据此报告文件，迁移方案、治理副本、验证和索引也落在该目录。配置中的
`governance_dir`/`public_docs_dir` 必须是安全的相对目录；越界或重叠等无效配置
由 `pgk check` 报告，写入命令在使用前拒绝。

`init` uses the `standard` profile by default. It creates only missing files;
existing files are reported as `skipped` and are never overwritten. Preview
writes without changing files:

```powershell
pgk init --root . --dry-run --json
```

新项目的 Agent 首轮可直接复制以下流程：

```powershell
Get-Content AGENTS.md
Get-Content docs/INDEX.md
Get-Content docs/STATUS.md
pgk doctor --root . --json
pgk new requirement REQ-001 "Discuss project requirements" --root .
```

只有用户确认需求后才继续创建 DES/ADR、TASK、REVIEW 和 VER；暂停或交接前运行
`pgk check --root . --json` 与 `pgk handoff ...`。`git init`、commit、push、
Issue/PR、merge、tag、release 和删除属于受保护动作，仍需用户逐项确认，`pgk`
不会自动执行这些动作。

## 3. 接入已有项目 / Existing project

已有项目先执行只读检查，不要直接初始化：

Inspect an existing project first; adoption is read-only:

```powershell
pgk adopt --root C:\path\to\project --json
pgk doctor --root C:\path\to\project --json
```

只补齐治理骨架时，确认报告后运行：

```powershell
pgk init --root C:\path\to\project --mode supplement
```

`--mode supplement` 只创建缺失文件；已有 `docs/STATUS.md` 会原样保留，没有状态文件时新状态为 `adoption_review`。

`adopt` 报告已有文件、缺失文件和可识别的旧结构映射。确认方案后，才执行
`init` 补齐缺失文件：

`adopt` reports existing files, missing files, and recognized legacy mappings.
Run `init` only after reviewing that report:

```powershell
pgk init --root C:\path\to\project
```

工具不会自动重命名、删除或合并已有文档。

The tool does not automatically rename, delete, or merge existing documents.

迁移模式先生成 `MIG-*` 方案。只自动处理 Markdown、Markdown 变体和 UTF-8 纯文本；其他格式、敏感文件和无法分类的内容只报告：

```powershell
pgk migrate plan --root C:\path\to\project --json
pgk migrate approve MIG-001 --root C:\path\to\project --item ITEM-001 --json
pgk migrate apply MIG-001 --root C:\path\to\project --json
```

`plan` 写入候选方案，`approve` 只改变条目状态，`apply` 只复制明确批准的条目。原文件保留在原位置，治理副本为 `draft` 并包含来源路径、来源哈希和迁移批次。重复运行具有幂等性；源变化或目标冲突会报告且不覆盖。
如果目标治理副本路径有未提交 Git 修改，即使文件内容恰好等于本次生成结果，
`apply` 也将该条目标为 `conflict`，批次不会被误判为已验证；先人工审查目标变化。

迁移 Markdown 副本时，Kit 会把指向同批次治理副本的相对链接改写为新路径；指向仍保留在源项目中的现有文件时，改写为从治理副本可解析的源文件路径。外部链接、锚点和不存在的目标不改写，并保留为人工审查项。

Migration mode first creates a `MIG-*` plan. It automatically handles only Markdown, Markdown variants, and UTF-8 plain text; other formats, sensitive files, and unclassified content are report-only. Original files remain in place, and conflicts never overwrite existing targets.

### 3.1 已治理项目升级 / Governed-project upgrade

`init --mode supplement` 只补缺失文件，不能升级已有治理合同。已存在
`.project-governance.toml` 的项目使用 `upgrade`，默认行为就是只读预览：

`init --mode supplement` only adds missing files; it does not upgrade an
existing governance contract. Use `upgrade` for a project that already has
`.project-governance.toml`. Its default behavior is a read-only preview:

```powershell
pgk upgrade --root C:\path\to\project --dry-run --json
pgk upgrade --root C:\path\to\project --apply --json
```

JSON 报告包含 `from_version`、`to_version`、`changed`、逐文件 `changes`
（含 diff 和前后哈希）、`unchanged`、`conflicts`、`dry_run` 与 `applied`。
升级只处理版本化迁移中声明的 Agent 合同章节、WORKFLOW/约定章节、TASK/BUG/VER
模板和生成视图；历史生命周期记录保持逐字节不变。项目修改过受管模板或章节、缺少
生成标记、来源版本未知时，命令报告冲突且不写任何文件。
同版本只修复生成视图时不会写一条虚假的升级活动；生成视图漂移通常使用
`pgk index` 重建。

A same-version generated-view refresh does not append a fictitious upgrade
activity event. Normally regenerate stale views with `pgk index`.

The JSON report includes the source and target versions, changed paths,
per-file diffs and hashes, unchanged paths, conflicts, and application state.
Historical lifecycle records are byte-for-byte untouched. A customized managed
section/template, missing generated marker, or unknown source version blocks
the complete write. Successful application uses same-directory atomic replaces,
rolls back earlier writes if a later write fails, and updates `kit_version`
only after the governed contract succeeds. Never update only `kit_version`.

## 4. 创建治理记录 / Create records

记录 ID 必须使用安全前缀，例如 `REQ-`、`DES-`、`ADR-`、`TASK-`、`BUG-`、
`VER-`、`MIG-`。常用示例：

Record IDs use safe prefixes such as `REQ-`, `DES-`, `ADR-`, `TASK-`, `BUG-`,
`VER-`, and `MIG-`. Examples:

```powershell
pgk new requirement REQ-001 "Define the project goal" --root .
pgk new design DES-001 "Describe the architecture" --root . --related REQ-001
pgk new decision ADR-001 "Choose the durable task record" --root .
pgk new task TASK-001 "Implement the first feature" --root . --status in_progress --related REQ-001
pgk new bug BUG-001 "Record an observed problem" --root .
pgk new verification VER-001 "Verify the first feature" --root .
```

`--related` 可以重复使用；`--status` 默认是 `draft`。支持的状态为：

`--related` may be repeated. `--status` defaults to `draft`. Supported
statuses are:

```text
draft, accepted, in_progress, in_review, blocked, verified, done, rejected, superseded
```

预览记录路径而不写文件：

Preview the record path without writing a file:

```powershell
pgk new task TASK-002 "Preview a task" --root . --dry-run --json
```

如果 ID 已存在，命令返回退出码 `2`，不会覆盖原记录。

If the ID already exists, the command exits with code `2` and does not overwrite
the existing record.

## 5. 日常检查和索引 / Daily checks and index

开发过程中正常修改代码和测试；在交接或提交 Pull Request 前运行：

Edit code and tests normally. Before a handoff or pull request, run:

```powershell
pgk check --root .
pgk doctor --root .
```

`check` 检查治理基线、Markdown 本地链接、frontmatter、重复 ID、状态、终态合同、
声明文件、生成视图、STATUS 引用、Kit 版本一致性和当前 Git 分支状态。
发现问题时返回退出码 `1`；命令错误或参数错误返回 `2`。
文件范围重叠只对并行且正在执行/审查的任务报告；顺序任务共享文件不是冲突。

File-scope overlap is diagnostic for active parallel work only. Sequential
tasks may reuse shared files.

`check` validates governance baselines, local Markdown links, frontmatter,
duplicate IDs, statuses, terminal contracts, declared files, generated views,
STATUS references, Kit version consistency, and current Git branch state. It exits with `1` when issues are found and `2`
for command or runtime errors.

面向 Agent 时使用稳定 JSON 输出：

Use stable JSON output for Agent callers:

```powershell
pgk check --root . --json
pgk doctor --root . --json
```

`index` 用任务和 Bug 记录更新 `docs/work/INDEX.md`：

Use `index` to update `docs/work/INDEX.md` from task and bug records:

```powershell
pgk index --root .
pgk index --root . --dry-run --json
```

只有带有 `<!-- PGK_GENERATED: work-index -->` 标记的索引才允许被工具重写；
项目自有索引会被拒绝并要求人工审查。

Only an index containing `<!-- PGK_GENERATED: work-index -->` may be rewritten.
Project-owned indexes are rejected and must be reviewed manually.

`--dry-run --json` 的 `changed` 数组列出会被刷新、当前已漂移的视图。

The `changed` array from `--dry-run --json` lists views that currently differ
and would be refreshed.

`new`、`index`、`transition`、`handoff` 在同目录准备临时文件，再替换本次涉及的
记录、生成视图和活动文件；后续替换失败时回滚已替换目标。目标是符号链接时会拒绝
替换；如果回滚也失败，会报告不完整回滚并保留 `.pgk-backup` 文件供人工恢复。
这不是跨进程/跨文件系统事务：失败时新建的空目录可能残留，目标文件权限或 ACL
等元数据也可能变化。此时应先保存备份并人工检查，不要直接重试或清理恢复文件。

These commands stage affected records, generated views, and activity files
before replacement and roll back earlier replacements on failure. Symlink
targets are refused. If rollback also fails, `.pgk-backup` recovery files are
preserved for manual review. This is not a cross-process or cross-filesystem
transaction; empty directories or file metadata changes may still need review.

## 6. 正式状态迁移 / Formal status transitions

不要手工改 frontmatter 状态。先预览迁移，再正式执行：

Do not edit frontmatter status by hand. Preview, then apply the transition:

```powershell
pgk transition TASK-001 in_review --root . --dry-run --json
pgk transition TASK-001 in_review --root . --json
```

任务或 Bug 进入 `verified`/`done` 前必须带 terminal-v2 标记，以稳定 `AC-*`
编号声明验收，并关联已验证的 VER。每个 AC 必须同时有验收结果和证据。Standard
要求 VER；Strict 还要求已验证 Review。终态 `head_commit` 可以写实际哈希，或在包含
该记录的单次收尾提交前写 `record-commit`。

Before a task or bug enters `verified`/`done`, its terminal-v2 contract must use
stable `AC-*` IDs and a reciprocal verified VER. Each AC needs both an outcome
and evidence. Standard requires VER; Strict also requires a verified Review.
Use an actual commit hash or `record-commit` for a single closing commit.

## 7. 跨会话交接 / Cross-session handoff

任务记录创建后，在暂停或交给其他 Agent 时更新交接区：

After creating a task, update its handoff section when pausing or transferring
work to another Agent:

```powershell
pgk handoff TASK-001 --root . `
  --status in_progress `
  --verification "unit tests: 20 passed" `
  --blocker "none" `
  --next-action "run the integration tests" `
  --json
```

可以重复使用 `--blocker`。交接信息包含当前分支、HEAD、工作区是否干净、
验证摘要、阻塞和下一步动作，但不会保存完整终端输出。

`--blocker` may be repeated. The handoff records the current branch, HEAD,
worktree state, verification summary, blockers, and next action; it does not
capture full terminal output.

注意：`handoff --status` 更新的是交接区中的状态文字，不会自动修改文件顶部
frontmatter 的 `status`。正式状态使用 `pgk transition`。

Note: `handoff --status` updates the status text inside the handoff block; it
does not rewrite the frontmatter `status`. Use `pgk transition` for formal state.

预览交接修改而不写文件：

Preview a handoff without writing the record:

```powershell
pgk handoff TASK-001 --root . --next-action "review the plan" --dry-run --json
```

## 8. Agent 推荐流程 / Recommended Agent flow

```text
读取 AGENTS.md、docs/INDEX.md、docs/STATUS.md
        ↓
pgk doctor --root . --json
        ↓
读取对应的需求、设计和 TASK/BUG 记录
        ↓
在任务分支中修改代码、测试和必要文档
        ↓
pgk check --root . --json
        ↓
运行项目自己的测试和构建命令
        ↓
pgk transition ...；pgk handoff ...
        ↓
提交 PR，链接任务记录
```

Read the repository rules and status, inspect the project, read the linked
records, work on a task branch, validate, run the project's own tests, update
the handoff, and link the record from the pull request.

## 9. 安全边界 / Safety boundaries

- `doctor`、`check` 和 `adopt` 默认只读；
- `init`、`new`、`index`、`transition`、`handoff` 支持 `--dry-run`；`upgrade` 默认只读且只有 `--apply` 写入；
- v0.1 不自动 commit、push、merge、删除或覆盖已有文档；
- v0.1 不调用 GitHub API、模型提供商或其他网络服务；
- 不要把密码、API Key、私有数据、完整模型载荷或思维链写入记录；
- 生成的 Markdown/TOML 是项目普通文件，可脱离 `pgk` 独立维护。

- `doctor`, `check`, and `adopt` are read-only by default;
- `init`, `new`, `index`, `transition`, and `handoff` support `--dry-run`; `upgrade` previews by default and writes only with `--apply`;
- v0.1 does not automatically commit, push, merge, delete, or overwrite documents;
- v0.1 does not call GitHub APIs, model providers, or other network services;
- never put passwords, API keys, private data, full model payloads, or chain-of-thought in records;
- generated Markdown/TOML files remain ordinary project files and can be maintained without `pgk`.
