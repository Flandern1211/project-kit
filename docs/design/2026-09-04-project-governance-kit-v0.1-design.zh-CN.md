---
id: DES-002-ZH
type: design
status: accepted
created: 2026-09-04
updated: 2026-09-22
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
- v0.1 只实现单 Agent 和跨会话顺序交接；后续只规划并行 Agent 协作安全、
  worktree 生命周期、文件范围和冲突预检，不规划自动合并；
- Agent 可以生成治理变更提案，但治理配置只有在用户确认后才能修改；
- 另一个后续扩展是经任务级明确授权的本地自动 commit；Web、模型调用、通用外部
  平台集成和自动公开操作均为产品非目标。

本节由 [ADR-0002](../decisions/ADR-0002-governance-profiles-and-v0-1-scope.md)
记录，优先于旧版并行协作表述；未来路线图由
[ADR-0004](../decisions/ADR-0004-roadmap-scope.md) 收口。

### 1.2 治理记录可见性（2026-09-07）

治理记录可见性独立于 profile 和协作模式，支持 `team-private`、`hybrid`、`public`。
完整设计和实现边界见 [ADR-0003](../decisions/ADR-0003-governance-record-visibility.md)
及 [可见性规格](../superpowers/specs/2026-09-07-governance-visibility-design.md)。
核心 Kit 不修改远程仓库权限、不重写历史，也不自动迁移已有文件。

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

### 4.1 确定性状态迁移与终态合同（2026-09-22 修订）

正式状态通过 `pgk transition <ID> <status>` 更新。`lifecycle` 按记录类型声明可用状态和合法迁移；命令在写入前完成门禁检查，并同步重建生成视图、追加活动记录。`pgk check` 仍保留只读检查，因此手工编辑或外部工具造成的非法状态也会被发现。

新建 TASK、BUG 和 VER 使用 `<!-- PGK_CONTRACT: terminal-v2 -->` 标记。TASK/BUG 的每条验收标准使用稳定 `AC-*` ID；终态要求已接受的上游记录、存在的字面文件路径、可追踪的 Git 提交，以及 reciprocal 终态 VER 中同 ID 的结果和证据。Lite 与 Standard 要求 VER；Strict 还要求 reciprocal 终态 REVIEW。实际提交哈希必须存在于当前仓库；当任务记录和收尾代码位于同一次提交时，可先写 `record-commit`，提交前由该记录的修改状态解析，提交后由包含该记录的最近提交解析。

没有 terminal-v2 标记的历史记录继续可读和可检查，不要求全库迁移；只有它们再次通过正式命令进入 TASK/BUG/VER 终态时才需要升级合同。该兼容策略不提升仓库 schema 版本。Kit 只判断结构、引用、文件、状态和 Git 等确定事实；未执行的人工验收、外部运行效果、性能或业务含义由 `AGENTS.md` 约束 Agent，不由核心 CLI 猜测。

### 4.2 受控 Kit 升级（2026-09-22 修订）

已治理项目通过 `pgk upgrade` 获取新版 Kit 合同。命令默认只生成升级提案，列出来源版本、
目标版本、逐文件变更、未变更项和冲突；只有显式 `--apply` 才写入。升级使用版本化迁移，
只修改 Kit 管理的段落、模板和生成视图，保留项目自定义段落和历史生命周期记录。缺少受管
标记、模板已自定义、版本路径未知或任何文件无法安全合并时，升级整体拒绝，不更新
`kit_version`。写入使用同目录临时文件替换；发生失败时回滚本次已写文件，配置版本最后更新。

v0.2.0.dev0 到 v0.2.0.dev1 的迁移更新 Agent 终态协议、WORKFLOW、项目约定、TASK/BUG/VER
模板和生成视图。旧记录保持 legacy 合同，新建记录使用 terminal-v2。核心 Kit 不下载版本、
不调用远程服务，也不运行项目业务迁移。

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
和冲突预检属于已规划扩展；自动协调和自动合并不是产品目标。任务记录仍可预留 `branch`、`worktree`、`owner`、
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
项目自有未标记文件必须人工审查合并。`pgk check` 将当前记录重新渲染为规范内容并与 INDEX/BOARD 逐字比较；差异报告为 `stale_generated_view`，由 `pgk index` 修复。

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
边界。后续只规划并行 Agent 协作安全/worktree 管理和受授权本地自动 commit。
远程平台自动化、Web 管理后台、模型调用、复杂格式转换、语义改写、历史清理、自动
治理等级评估和自动公开操作是产品非目标；Agent 仍只需读取治理等级配置并提出变更提案。

## 9. 需求覆盖

| 需求 | 设计章节 |
|---|---|
| FR-01/02 | 2、5 |
| FR-03/04 | 3、7 |
| FR-05/06 | 6、8 |
| FR-07 | 3、4、5、7 |
| NFR-01 至 NFR-06 | 2 至 8 |
