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
| `pgk check` | 检查基线、链接、frontmatter、ID、状态、索引、STATUS 引用、配置、Kit 版本、Git 和迁移结果 | 只读；发现问题返回退出码 1 | 不得把 dirty/unregistered 等问题误报为已验证 |
| `pgk new` | 创建 requirement/design/decision/task/bug/review/verification/migration 记录 | 拒绝重复 ID 和覆盖；支持 `--dry-run` | 上游记录、owner、scope 和证据字段 |
| `pgk index` | 重建记录索引、工作索引和 BOARD | 只重写带 `PGK_GENERATED` 标记的视图 | 记录是否完整入索引 |
| `pgk handoff` | 更新 TASK/BUG 的受控 handoff 区块和活动记录 | 只写标记区；不改变 frontmatter 状态 | branch、HEAD、dirty、未提交内容、阻塞和唯一下一步 |
| `pgk migrate` | 包含 `plan`、`approve`、`apply`：扫描、审查并执行文档迁移 | 原文件不移动、不删除；只应用明确批准的条目 | 来源、目标、哈希、敏感性、置信度、链接、冲突和 VER 证据 |

当前不实现：parallel Agent 调度、自动 Git commit/push/merge、Issue/PR 或远程仓库操作、
Web 管理后台、模型调用、公开副本导出、历史清理以及 Markdown/UTF-8 纯文本之外的自动转换。

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

迁移 Markdown 副本时，Kit 会把指向同批次治理副本的相对链接改写为新路径；指向仍保留在源项目中的现有文件时，改写为从治理副本可解析的源文件路径。外部链接、锚点和不存在的目标不改写，并保留为人工审查项。

Migration mode first creates a `MIG-*` plan. It automatically handles only Markdown, Markdown variants, and UTF-8 plain text; other formats, sensitive files, and unclassified content are report-only. Original files remain in place, and conflicts never overwrite existing targets.

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

`check` 检查治理基线、Markdown 本地链接、frontmatter、重复 ID、状态、STATUS 引用、
Kit 版本一致性和当前 Git 分支状态。
发现问题时返回退出码 `1`；命令错误或参数错误返回 `2`。

`check` validates governance baselines, local Markdown links, frontmatter,
duplicate IDs, statuses, STATUS references, Kit version consistency, and current
Git branch state. It exits with `1` when issues are found and `2`
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

## 6. 跨会话交接 / Cross-session handoff

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
frontmatter 的 `status`。需要改变正式记录状态时，应审查后手动修改 frontmatter，
再运行 `pgk check`。

Note: `handoff --status` updates the status text inside the handoff block; it
does not rewrite the frontmatter `status`. Change the formal record status
intentionally, then run `pgk check`.

预览交接修改而不写文件：

Preview a handoff without writing the record:

```powershell
pgk handoff TASK-001 --root . --next-action "review the plan" --dry-run --json
```

## 7. Agent 推荐流程 / Recommended Agent flow

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
pgk handoff ... 或更新任务为 verified/done
        ↓
提交 PR，链接任务记录
```

Read the repository rules and status, inspect the project, read the linked
records, work on a task branch, validate, run the project's own tests, update
the handoff, and link the record from the pull request.

## 8. 安全边界 / Safety boundaries

- `doctor`、`check` 和 `adopt` 默认只读；
- `init`、`new`、`index`、`handoff` 支持 `--dry-run`；
- v0.1 不自动 commit、push、merge、删除或覆盖已有文档；
- v0.1 不调用 GitHub API、模型提供商或其他网络服务；
- 不要把密码、API Key、私有数据、完整模型载荷或思维链写入记录；
- 生成的 Markdown/TOML 是项目普通文件，可脱离 `pgk` 独立维护。

- `doctor`, `check`, and `adopt` are read-only by default;
- `init`, `new`, `index`, and `handoff` support `--dry-run`;
- v0.1 does not automatically commit, push, merge, delete, or overwrite documents;
- v0.1 does not call GitHub APIs, model providers, or other network services;
- never put passwords, API keys, private data, full model payloads, or chain-of-thought in records;
- generated Markdown/TOML files remain ordinary project files and can be maintained without `pgk`.
