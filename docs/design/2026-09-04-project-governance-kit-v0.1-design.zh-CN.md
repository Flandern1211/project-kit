---
id: DES-002-ZH
type: design
status: accepted
created: 2026-09-04
updated: 2026-09-07
related:
  - REQ-001-ZH
  - REQ-001
---

# Project Governance Kit v0.1 技术设计

> 本文由用户于 2026-09-04 确认，并由 2026-09-07 的 ADR-0002 修订。设计不增加需求范围；如果设计与需求冲突，以需求为准。

## 1. 设计边界

Kit 为新项目生成自包含的文档、规则、索引和 Git 协作骨架。项目状态保存在项目
仓库，Git 保存代码和文档，Kit 不拥有业务数据，也不依赖中心化服务。

v0.1 使用 Python 3.11+ 标准库。核心 CLI 只负责本地文件和只读 Git 查询，不执行
`git init`、commit、push、merge、tag、release、删除或任何远程 API，也不调用模型。

### 1.1 治理等级与协作模式（2026-09-07 修订）

- 治理等级为 Lite、Standard、Strict，只控制文档和检查深度；
- 协作模式独立于治理等级，分为 `single-agent`、`sequential-agents` 和
  `parallel-agents`；
- v0.1 只实现单 Agent 和跨会话顺序交接；并行 Agent、worktree 协调、文件范围
  锁定和自动合并延期；
- Agent 可以生成治理变更提案，但治理配置只有在用户确认后才能修改；
- GitHub/Issue、Web、模型调用和自动公开操作是后续可选扩展。

本节由 [ADR-0002](../decisions/ADR-0002-governance-profiles-and-v0-1-scope.md)
记录，优先于旧版并行协作表述。

## 2. 初始化流程

```text
检查目标目录和已有文件
        ↓
只读检查 Git 状态
        ↓
创建缺失的规则、索引、模板、状态和活动文件
        ↓
设置 project_stage=requirements_discussion
        ↓
输出 created/skipped/git_state 报告
        ↓
用户与 Agent 开始需求讨论
```

### 2.1 写入规则

- 目标目录不存在或不是目录时安全失败；
- 已有文件一律 `skipped`，不覆盖、不删除、不重命名；
- 目录通过 `INDEX.md`、`BOARD.md`、`WORKFLOW.md` 或 `ACTIVITY.md` 占位；
- 文件写入部分失败时返回已创建、未创建和错误；
- 无 Git 时报告 `git_not_initialized`，但 `pgk init` 不运行 `git init`；
- Agent 只有获得用户对 `git init` 的明确授权后，才能单独执行该命令；
- 初始化不创建业务 `REQ-*`，不伪造技术选型和验收结论。

### 2.2 standard profile 产物

```text
AGENTS.md
README.md
CONTRIBUTING.md
CHANGELOG.md
.gitignore
.project-governance.toml
docs/
├── INDEX.md
├── STATUS.md
├── WORKFLOW.md
├── templates/INDEX.md
├── requirements/INDEX.md
├── design/INDEX.md
├── decisions/INDEX.md
├── work/BOARD.md
├── work/tasks/INDEX.md
├── work/bugs/INDEX.md
├── reviews/INDEX.md
├── verification/INDEX.md
├── activity/ACTIVITY.md
└── operations/{runbooks,incidents,postmortems}/INDEX.md
```

`operations/` 是预建占位结构，实际运行服务或发生运维事件时才填充。`ACTIVITY.md`
记录治理节点，不记录程序运行日志；运行日志由项目自己的机制管理。

## 3. 记录模型

### 3.1 记录类型

| 类型 | 用途 | Git 字段 |
|---|---|---|
| REQ | 目标、范围、非范围、假设和验收 | N/A 或上游引用 |
| DES | 技术、数据、API、安全和界面设计 | N/A 或上游引用 |
| ADR | 长期架构或治理决策 | N/A 或上游引用 |
| TASK | 功能或工程实施任务 | branch/worktree/files/base/head |
| BUG | 复现问题及修复 | branch/worktree/files/base/head |
| REVIEW | 基线、目标、发现和评审结论 | 关联任务 Git 引用 |
| VER | 测试、检查和人工验收证据 | 关联任务/Review |

每条记录的 frontmatter 至少包含 `id`、`type`、`status`、`created`、`updated`、
`related`。任务、Bug、Review、Verification 还要在正文保留 owner、scope、evidence、
blocker 和 next action；不适用的 Git 字段填 `N/A`。

### 3.2 文档链

```text
功能：REQ → DES/ADR → TASK → CODE/TEST → REVIEW → VERIFICATION
Bug：BUG → CODE/TEST → REVIEW → VERIFICATION
```

索引只提供唯一链接，记录正文保存事实；计划、聊天和 handoff 不得替代已确认需求。

## 4. 项目阶段与记录状态

项目阶段只写入 `docs/STATUS.md`：`initialized`、`requirements_discussion`、
`requirements_review`、`active_development`、`maintenance`、`blocked`。

记录状态为 `draft`、`accepted`、`in_progress`、`in_review`、`blocked`、`verified`、
`done`、`rejected`、`superseded`。项目阶段描述全局位置，记录状态描述单条记录，
多个任务、Bug 和 worktree 可以并行。

## 5. Agent 工作协议

开始任何治理动作时，Agent 按顺序读取 `AGENTS.md`、`docs/INDEX.md`、`docs/STATUS.md`、
当前动作关联记录和 Git 状态。如果文档缺失、链接断开、状态冲突或上游需求未确认，
Agent 停止当前动作，在任务中记录 blocker 并请求用户。

需求先形成 `REQ-*` 草案，只有用户确认后才成为 `accepted`。实现前必须存在已接受
需求和适用设计，并创建 TASK/BUG，登记 owner、文件范围和分支。完成后必须保留测试、
Review、Verification 和 handoff 证据。

Kit 通过生成的 `AGENTS.md`、模板和 `pgk check` 提供规则与违规报告，但不能技术上
拦截完全忽略规则的外部 Agent；遵守集成协议的 Agent 必须在门禁不满足时停止。

## 6. Git 协同与授权

单 Agent 使用 `task/<TASK-ID>-<slug>` 或 `bug/<BUG-ID>-<slug>` 分支；v0.1 不要求额外
worktree。并行 Agent 使用 `.worktrees/<TASK-ID>` 或 `.worktrees/<BUG-ID>`、文件范围
冲突检查和自动协调均为后续扩展。任务记录仍可预留 `branch`、`worktree`、`owner`、
`files`、`base_commit` 和 `head_commit` 字段。

以下动作默认逐次需要用户明确确认：commit、push、Issue 创建/更新/关闭/回复、PR/MR
创建/更新/关闭/回复、merge、tag、release/公开发布以及删除分支或 worktree。

任务级或会话级授权只有在动作、目标、范围、期限和未撤销状态都明确时才有效。commit
授权不包含 push、PR 或 merge；没有匹配授权时只能准备命令、commit message 或 PR 草稿。
受保护动作完成后，必须记录授权依据、目标、时间、结果、提交/链接和后续验证。

## 7. 可视化

`docs/STATUS.md` 是全局状态唯一来源，至少展示阶段、当前重点、owner、阻塞、下一步
和更新时间。`docs/work/BOARD.md` 使用固定列：ID、type、status、owner、related、
branch/worktree、verification、blocker、next。

`docs/WORKFLOW.md` 保存包含 blocked 进入和恢复路径的 Mermaid 状态图。各目录 `INDEX.md`
保存唯一记录链接。`docs/activity/ACTIVITY.md` 使用
`timestamp | actor | action | record_id | git_ref | result` 记录重要节点。

Kit 生成的视图使用 `<!-- PGK_GENERATED: ... -->` 标记；只有带标记的视图可以自动更新，
项目自有未标记文件必须人工审查合并。

## 8. 模块和验证

模块边界为：`config` 配置、`frontmatter/models` 记录模型、`templates` 模板、`scaffold`
初始化、`records` 记录和索引、`checks` 文档/授权/范围检查、`git_context` Git 只读查询、
`handoff` 交接、`cli` 命令分发。

验证覆盖：空新项目、已有 Git、无 Git 且拒绝初始化、已有文件保护、七类记录生成、
需求未确认门禁、Review/Verification 记录、授权过期/撤销/动作不匹配、脏工作区和
`--json`/`--dry-run` 输出。并行 Agent 文件范围冲突属于后续扩展。核心 CLI 不执行受保护动作的验证以源码和命令
接口审查为依据；真实 Agent 是否遵守规则必须通过集成试验验证。

### 8.1 v0.1 实现边界

v0.1 的核心是初始化、文档链、状态/索引、任务和验证记录、跨会话交接以及用户授权
边界。多 Agent 并行调度、远程平台、Web 管理后台、模型调用和自动公开操作不属于
本版实现目标；治理等级的完整自动评估也延后，Agent 只需能够读取配置并提出变更提案。

## 9. 需求覆盖

| 需求 | 设计章节 |
|---|---|
| FR-01/02 | 2、5 |
| FR-03/04 | 3、7 |
| FR-05/06 | 6、8 |
| FR-07 | 3、4、5、7 |
| NFR-01 至 NFR-06 | 2 至 8 |
