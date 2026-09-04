---
id: REQ-001-ZH
type: requirement
status: accepted
created: 2026-09-02
updated: 2026-09-03
related:
  - REQ-001
---

# Project Governance Kit v0.1 需求规格

> 本文已由用户于 2026-09-03 确认，是 v0.1 的中文需求基线。[English](2026-09-02-project-governance-kit-v0.1-requirements.md) 为同步翻译；若两种语言出现差异，以本文为准。

- 文档状态：已确认
- Kit 版本：0.1
- 修订日期：2026-09-03

## 1. 产品目标

Project Governance Kit 是一套以项目文档为核心的通用开发治理架构。它为新项目
初始化一套完整、可追踪、可协同的文档和 Git 骨架，让用户、不同 Agent 和不同
会话根据同一套规则进行需求讨论、设计、实现、验证、交接和维护。

它解决的不是某个业务领域的问题，而是减少以下开发风险：上下文丢失、重复实现、
范围漂移、未确认的设计被当成事实、代码与文档不一致、缺少测试证据以及 Agent
之间无法可靠交接。

## 2. v0.1 范围

### 2.1 目标项目

v0.1 只要求支持新项目初始化。已有项目迁移、合并和历史文档自动整理不属于
第一版验收范围，可以作为后续能力。

### 2.2 文档驱动开发

初始化后，用户先与 Agent 讨论项目需求。需求、设计、任务、Bug、Review、验证
和交接都必须沉淀为项目仓库中的版本化文档。文档是跨 Agent、跨会话和跨人员
协作的共同上下文，不依赖某一次聊天记录。

### 2.3 可视化方式

v0.1 使用 Git 可追踪的 Markdown 表格、索引和 Mermaid 图展示项目状态、任务节点、
文档关系和流程，不建立 Web 管理后台或托管式协作服务。

### 2.4 Git 协同

项目必须使用 Git 保存代码和治理文档。一个可实施任务默认对应一个任务分支；
并行 Agent 默认使用独立 worktree，并在任务记录中登记分支、worktree、负责人
和文件范围。

## 3. 初始化产物

在新项目根目录执行初始化后，Kit 至少创建以下文件和目录。目录可以只有索引或
占位内容，但不能因为 Git 不保存空目录而消失：

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
├── templates/
│   ├── INDEX.md
│   ├── requirement.md
│   ├── design.md
│   ├── decision.md
│   ├── task.md
│   ├── bug.md
│   ├── review.md
│   └── verification.md
├── requirements/
│   └── INDEX.md
├── design/
│   └── INDEX.md
├── decisions/
│   └── INDEX.md
├── work/
│   ├── BOARD.md
│   ├── tasks/
│   │   └── INDEX.md
│   └── bugs/
│       └── INDEX.md
├── reviews/
│   └── INDEX.md
├── verification/
│   └── INDEX.md
├── activity/
│   └── ACTIVITY.md
└── operations/
    ├── runbooks/
    │   └── INDEX.md
    ├── incidents/
    │   └── INDEX.md
    └── postmortems/
        └── INDEX.md
```

`operations/` 是预建的占位结构；只有项目实际运行服务或发生运维事件时才需要
填充记录。运行时日志由项目自己的日志系统管理，不与开发活动记录混用。

初始化只负责建立骨架和规则入口，不自动编造项目业务需求、技术选型或验收结论。

### 3.1 Git 初始化路径

- 已有 Git 仓库：Kit 创建治理文件，文件由用户按正常 Git 流程提交；Kit 不自动提交；
- 没有 Git 仓库：Kit 先报告 `git_not_initialized`，Agent 必须获得用户确认后才能执行
  `git init`；确认后仍不能自动 commit；
- 用户拒绝 `git init`：Kit 可以创建文档骨架，但状态必须保留为 `git_not_initialized`
  并阻止进入可验证的开发阶段。

核心 `pgk init` 命令默认不执行 `git init`、commit、push、merge 或远程操作。

## 4. 文档记录和权威关系

### 4.1 记录类型

- `REQ-*`：用户目标、范围、非范围、假设和验收标准；
- `DES-*`：技术、数据、API、安全或界面设计；
- `ADR-*`：影响长期实现的架构或治理决策；
- `TASK-*`：功能或工程任务；
- `BUG-*`：可复现的问题、影响、复现和修复；
- `REVIEW-*`：代码/文档审查、评审人、基线与目标提交、发现和结论；
- `VER-*`：测试、检查、人工验收和外部验证证据。

所有记录至少包含 `id`、`type`、`status`、`created`、`updated` 和 `related`。任务、
Bug、Review 和验证记录还必须包含适用的负责人、范围、证据、Git 引用、阻塞和下一步。

### 4.2 活动记录

`docs/activity/ACTIVITY.md` 记录重要治理动作和状态转换，固定格式为：

```text
timestamp | actor | action | record_id | git_ref | result
```

它记录“创建需求、确认需求、开始任务、提交审查、验证通过、交接、关闭”等节点，
不记录思维链、完整聊天、每条命令或原始终端输出。

## 5. Agent 开发规则

### 5.1 开始任何治理动作

Agent 必须按以下顺序读取：

1. `AGENTS.md`；
2. `docs/INDEX.md`；
3. `docs/STATUS.md`；
4. 与当前动作关联的需求、设计、TASK/BUG、Review 和验证记录；
5. Git 当前分支、HEAD、工作区状态和文件所有权。

如果必要文件缺失、链接断开、状态冲突或上游记录未确认，Agent 必须停止当前动作，
在任务中记录 blocker 并请求用户处理，不能静默继续。

### 5.2 需求讨论和确认

- 用户和 Agent 的需求讨论形成 `REQ-*` 草案；
- 草案标记范围、非范围、假设、待确认事项和验收标准；
- 用户确认后才能标记为 `accepted`；
- 未确认的需求不得作为实现依据；
- 需求变化必须更新原记录或建立明确修订记录，不得只修改聊天内容。

### 5.3 设计、任务和实现

- 新功能链路为 `REQ → DESIGN/ADR → TASK → CODE/TEST → REVIEW → VERIFICATION`；
- Bug 可以从 `BUG → CODE/TEST → REVIEW → VERIFICATION` 开始，必要时再关联 REQ/DES；
- 涉及架构、API、数据或安全边界时，必须先有设计或 ADR；
- 每个代码或治理文档变更必须关联 TASK/BUG，或明确属于需求/设计审查动作；
- Agent 不得把计划、猜测或临时方案伪装成已确认设计。

### 5.4 验证、交接和关闭

- 任务进入 `verified` 或 `done` 前必须有可重运行的测试、检查或人工验收证据；
- Review 记录必须说明基线提交、目标提交、评审结果、未解决发现和证据；
- 交接必须写入当前工作、已完成内容、未完成内容、分支、HEAD、工作区状态、
  未提交改动、阻塞和唯一下一步动作；
- 新 Agent 应只依赖项目文档和 Git 状态即可恢复工作，不要求读取前一轮完整对话。

### 5.5 规则的执行边界

Kit 通过项目内 `AGENTS.md`、模板、状态约束和 `pgk check` 提供规范和违规报告，
但无法从技术上拦截一个完全忽略规则的外部 Agent 或用户。

遵守 Kit 集成协议的 Agent 必须在不符合状态或缺少授权时停止并请求确认；未安装
集成的 Agent 至少可以被文档检查发现违规，不能声称 Kit 已经强制阻止了所有外部命令。

## 6. Git 协作和用户授权

### 6.1 本地分支和 worktree

- 任务确认后，Agent 可以创建并登记本地任务分支；
- 默认分支命名为 `task/<TASK-ID>-<slug>`，Bug 分支命名为 `bug/<BUG-ID>-<slug>`，
  具体前缀可在项目配置中调整；
- 并行 Agent 使用独立 worktree，默认目录为项目 `.worktrees/` 下的任务目录；
- 单 Agent 串行开发可以使用任务分支，不强制额外 worktree；
- 任务记录必须登记 `branch`、`worktree`、`owner`、`files`；文件范围冲突时必须报告并停止；
- 非实施类记录的 branch/worktree/HEAD 可以填 `N/A` 或继承上游引用，不要求虚构 Git 绑定。

### 6.2 受保护动作授权

以下动作默认逐次需要用户明确确认：

- `git commit`；
- `git push`；
- 创建、更新、关闭或回复 GitHub/GitLab/Plane Issue；
- 创建、更新、关闭或回复 Pull Request/Merge Request；
- `merge`；
- 创建或推送 tag；
- 发布 release、包或其他公开产物；
- 删除分支、worktree 或其他可能造成历史/数据丢失的操作。

如果用户明确授予任务级或会话级授权，只有同时满足以下条件才可免逐次确认：

1. 授权明确写出动作；
2. 授权明确写出目标仓库、分支、Issue/PR 或发布对象；
3. 授权有有效期限或明确的任务/会话范围；
4. 授权未被用户撤销；
5. 当前动作不超出授权。

没有匹配授权时，Agent 只能准备命令、提交内容或 PR 草稿，不能执行。commit 的授权
不自动包含 push、PR 或 merge；授权一个任务也不自动授权其他任务。

### 6.3 公开动作证据

受保护动作完成后，必须在任务或 Review 记录中登记动作、目标、授权依据、时间、结果、
提交或链接及后续验证。核心 CLI 不直接调用远程平台；只有取得匹配授权的 Agent 集成
才能执行对应公开动作。

## 7. 状态和节点可视化

项目阶段和单条记录状态分开管理：

- 项目阶段：`initialized`、`requirements_discussion`、`requirements_review`、
  `active_development`、`maintenance`、`blocked`；
- 记录状态：至少支持 `draft`、`accepted`、`in_progress`、`in_review`、`blocked`、
  `verified`、`done`、`rejected`、`superseded`；不同记录类型可以限制可用子集。

项目可以同时存在多个任务、Bug 和 worktree；`STATUS.md` 只描述全局阶段和当前重点，
`BOARD.md` 展示全部记录。

### 7.1 可视化最小合同

- `docs/STATUS.md`：唯一的全局当前状态，至少包含项目阶段、当前需求/设计/任务、
  owner、阻塞、下一步和更新时间；
- `docs/work/BOARD.md`：至少包含 `ID`、`type`、`status`、`owner`、`related`、
  `branch/worktree`、`verification`、`blocker`、`next`；
- `docs/WORKFLOW.md`：包含状态流转 Mermaid 图，并明确 `blocked` 的进入和恢复路径；
- `docs/INDEX.md` 及各目录 `INDEX.md`：提供唯一记录链接，不复制正文；
- 每次记录创建、状态变更、交接、Review 或验证完成后，相关索引和活动记录必须更新；
- `pgk check` 应检查记录是否被索引、链接是否有效、关键字段是否完整；
- 非实施类节点的 Git 字段可填 `N/A` 或上游引用，不能伪造分支和提交。

## 8. 功能需求

### FR-01 新项目初始化

Kit 应能为新项目创建第 3 节定义的目录、索引、模板入口、配置、状态文件和 Agent
规则文件。已有文件默认不覆盖。

### FR-02 Agent 规则入口

Kit 应生成或提供 `AGENTS.md` 和 Agent 集成说明，使不同 Agent 知道必须读取项目文档、
遵守状态门禁、登记任务、保存验证证据并在受保护动作前请求授权。

### FR-03 需求到验收的文档链

Kit 应支持并检查功能链路 `REQ → DESIGN/ADR → TASK → CODE/TEST → REVIEW → VERIFICATION`，
以及 Bug 链路 `BUG → CODE/TEST → REVIEW → VERIFICATION`。

### FR-04 记录和活动索引

Kit 应提供需求、设计、决策、任务、Bug、Review、验证和重要活动的索引；索引只导航，
活动日志只保留关键治理事件。

### FR-05 Git 协同

Kit 应记录任务与分支、worktree、提交、Review、合并和公开动作证据之间的关系，并能
报告脏工作区、未登记分支、文件范围冲突或缺少关联记录。

### FR-06 用户授权门禁

Kit 应提供可被 Agent 集成执行的授权规则和检查结果：无匹配授权时，Agent 集成必须
停止受保护动作；核心 CLI 不执行这些动作。

### FR-07 结果可读和可恢复

任何人或 Agent 仅通过项目文档和 Git 状态，都应能够理解当前阶段、当前节点、已完成
工作、阻塞问题、授权状态和下一步动作。

## 9. 非功能需求

- 文档和 Git 是长期权威来源，不依赖聊天上下文；
- 文档、索引、状态、授权和活动记录具有稳定、可检查的格式；
- 初始化和检查过程不覆盖已有文件、不删除历史；
- 适用于 Python、Go、Node、Java 等不同技术栈；
- 生成内容适合人阅读，也适合 Agent 解析；
- 同一状态重复检查应得到确定性结果；
- 不将密钥、密码、私有数据、完整模型载荷或思维链写入仓库；
- 运行日志与开发记录分离；
- 所有重要结论能够追溯到需求、设计、记录、提交、测试或人工验收证据。

## 10. v0.1 验收标准

- AC-01：在空的新项目目录执行初始化，所有必需目录通过索引或占位文件可被 Git 追踪；
- AC-02：已有 Git 的新项目初始化后不自动 commit，生成的 `AGENTS.md` 能指导 Agent 开始工作；
- AC-03：无 Git 的新项目在用户同意时可由 Agent 执行 `git init`，在用户拒绝时保留
  `git_not_initialized` 并阻止进入可验证开发阶段；
- AC-04：初始化后的项目阶段为 `requirements_discussion`，没有伪造的业务需求；
- AC-05：需求草案经用户确认后才能作为设计和实现依据；
- AC-06：用户和 Agent 可以创建 REQ、DES、ADR、TASK、BUG、REVIEW 和 VER 记录，并保持关联；
- AC-07：Agent 在开始实现前能检查上游记录和状态，缺少确认时会停止并记录 blocker；
- AC-08：STATUS、BOARD、WORKFLOW 和 ACTIVITY 按第 7.1 节最小合同展示节点和状态；
- AC-09：任务与 Git 分支/worktree/提交关系可追踪，文件范围冲突可以被发现；
- AC-10：没有匹配用户授权时，Agent 集成不执行 commit、push、Issue/PR、merge、tag、
  release 或删除操作；核心 CLI 不执行这些动作；
- AC-11：任务交接记录足以让新 Agent 在没有前一轮聊天记录的情况下继续工作；
- AC-12：Review 和验证记录包含基线/目标、结论、发现和证据；
- AC-13：Kit 仓库本身使用同样的文档、任务、验证和 Git 协作规范；
- AC-14：对一个新建的试验项目可以执行初始化和只读验证，不导入具体业务规则。

## 11. 已确定的默认决策

- v0.1 只做新项目初始化，已有项目接入延后；
- 可视化只使用 Git 可追踪的 Markdown、索引和 Mermaid，不做 Web 后台；
- `pgk init` 默认只创建文件，不执行 `git init`、commit、push、merge 或远程操作；
- 无 Git 时必须先获得用户确认，Agent 才能执行 `git init`；
- 任务确认后可以创建本地分支，只有并行开发才默认创建独立 worktree；
- commit、push、Issue/PR、merge、tag、release 和删除默认逐次确认；明确的任务级/会话级
  授权必须包含动作、目标和期限，且不自动扩大到相邻动作；
- 活动日志记录治理节点而不是每条命令或每段对话；
- `operations/` 目录预建但按项目实际需要使用；
- 现有 TouzhiAgent 属于已有项目，不作为 v0.1 新项目初始化验收对象。
