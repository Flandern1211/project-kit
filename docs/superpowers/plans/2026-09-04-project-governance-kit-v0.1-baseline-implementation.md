# Project Governance Kit v0.1 新项目治理基线实施计划

> **For agentic workers:** 本计划执行时按仓库 `AGENTS.md` 工作；每个任务都必须先测试、再实现、再验证。commit、push、PR、merge、tag、release 和删除操作不在本计划授权范围内，需用户另行明确确认。

**目标：** 实现已确认 v0.1 需求和 DES-002-ZH 定义的新项目初始化、文档链、可视化、Git 协同记录和 Agent 门禁基础。

**架构：** 保留 Python 标准库 CLI 和普通 Markdown/TOML 文件作为项目自包含的核心。脚手架负责初始文件树和视图，记录服务负责类型/关联/索引，检查器负责结构与 Git 证据，Agent 规则写入目标项目的 `AGENTS.md`。

**技术栈：** Python 3.11+、`argparse`、`tomllib`、标准库文件系统和 `subprocess` 只读 Git 查询、pytest。

**规范：** `docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.zh-CN.md`、`docs/design/2026-09-04-project-governance-kit-v0.1-design.zh-CN.md`。

## 全局约束

- 目标项目只支持新项目初始化；已有项目迁移不是本计划范围。
- 生成文件不得覆盖、删除或重命名已有文件。
- `pgk init` 不执行 `git init`、commit、push、merge、tag、release 或远程 API。
- 所有受保护动作默认需要用户逐次确认；本计划不执行这些动作。
- 核心 CLI 不调用模型提供商或其他网络服务。
- 项目阶段和记录状态分开保存；所有视图必须可由 Git 追踪。
- 活动日志记录重要治理节点，不记录思维链、完整聊天或原始终端输出。
- 每个任务必须运行覆盖测试、`compileall` 和 `git diff --check`；提交由用户另行授权。

---

## Task 1：记录模型、状态和模板

**文件：**

- 修改 `src/project_governance/models.py`：增加 `REVIEW` 类型、`in_review` 和 `superseded` 状态。
- 修改 `src/project_governance/templates.py`：允许 `review` 模板。
- 新增 `src/project_governance/templates/review.md`：包含 Purpose、Scope、Acceptance、Evidence、Changes、Blockers、Next action、Authorization、base/head 和 verdict 区域。
- 修改 `tests/test_records.py`：覆盖新类型、状态和模板。

**接口：**

- `RecordType.REVIEW` 和 `Status.IN_REVIEW/SUPERSEDED` 供记录、检查和 CLI 使用。
- `render_template("review", metadata, {"title": title})` 生成合法 Review 文档。

**验证：**

- 先添加新枚举和模板的失败测试并确认失败；
- 实现最小模型和模板支持；
- 运行记录测试、全量测试、编译和 diff 检查；
- 更新 `TASK-005` 的证据，不执行 commit。

## Task 2：新项目完整脚手架

**文件：**

- 修改 `src/project_governance/scaffold.py`：扩展 standard profile 文件树、Git 状态报告和初始化阶段。
- 修改 `tests/test_scaffold.py`：覆盖空目录、已有文件、不覆盖、已有 Git、无 Git 和 dry-run。

**接口：**

- `init_project(root, project_name=None, profile="standard", dry_run=False)` 返回 `created`、`skipped`、`git_state` 和 `project_stage`。
- 初始化创建 requirements/design/decisions/templates/work/reviews/verification/activity/operations 的索引或占位文件。
- 初始 `STATUS.md` 为 `project_stage: requirements_discussion`，无业务需求记录。
- 初始 `AGENTS.md` 写入读取顺序、状态门禁、交接和受保护动作授权规则。

**验证：**

- 先添加文件树和 Git 状态断言并确认失败；
- 实现只创建缺失文件的脚手架；
- 检查初始化不会执行 `git init` 或 commit；
- 运行脚手架测试、全量测试、编译和 diff 检查；
- 不提交，记录未提交文件和测试结果。

## Task 3：记录创建、索引、看板和活动记录

**文件：**

- 修改 `src/project_governance/records.py`：支持 REQ/DES/ADR/TASK/BUG/REVIEW/VER，维护对应目录索引、`BOARD.md` 和 `ACTIVITY.md`。
- 修改 `src/project_governance/scaffold.py`：初始化 `WORKFLOW.md`、`BOARD.md`、`ACTIVITY.md` 和各目录索引的固定内容。
- 新增 `tests/test_views.py`：覆盖唯一链接、固定看板列、Mermaid blocked 路径和活动格式。
- 修改 `tests/test_records_commands.py`：覆盖 Review 创建、关联和重复 ID。

**接口：**

- `create_record(root, kind, record_id, title, status, related, dry_run)` 支持 Review。
- `update_indexes(root)` 只更新带 `PGK_GENERATED` 标记的视图；项目自有未标记视图拒绝覆盖。
- `append_activity(root, actor, action, record_id, git_ref, result)` 追加一条固定格式事件。

**验证：**

- 先添加 Review/视图失败测试；
- 实现记录目录、索引、看板和活动更新；
- 使用空项目 fixture 验证所有链接可解析；
- 运行视图、记录、全量测试、编译和 diff 检查；
- 不提交，记录视图生成结果。

## Task 4：治理检查、授权和文件范围

**文件：**

- 修改 `src/project_governance/checks.py`：检查 required views、索引覆盖、关键字段、项目阶段、授权格式、任务 Git 字段和活动记录格式。
- 修改 `src/project_governance/git_context.py`：补充 worktree 列表和只读分支信息。
- 新增 `src/project_governance/authorization.py`：解析动作/目标/范围/期限/状态并判断是否匹配。
- 新增 `tests/test_governance_checks.py`：覆盖缺索引、缺字段、过期/撤销/动作不匹配授权、脏工作区和文件范围冲突。

**接口：**

- `run_checks(root)` 返回确定性、JSON 可序列化的 issues；发现错误返回 `ok=False`。
- `inspect_git(root)` 只读返回 branch/head/dirty/recent commits/worktrees。
- `authorization_matches(record, action, target, at)` 仅检查文档授权，不执行动作。

**验证：**

- 先添加各类违规 fixture 并确认失败；
- 实现最小结构和授权检查；
- 确认检查器不运行 commit/push/远程 API；
- 运行检查器、全量测试、编译和 diff 检查；
- 不提交，记录无法技术拦截外部 Agent 的边界。

## Task 5：CLI、Agent 入口和交接

**文件：**

- 修改 `src/project_governance/cli.py`：支持 Review 创建、初始化报告、视图索引和授权检查 JSON 输出。
- 修改 `src/project_governance/handoff.py`：写入 TASK/BUG 的完整交接字段和未提交状态。
- 修改 `src/project_governance/__main__.py`：保持模块入口。
- 修改 `tests/test_cli.py`、`tests/test_handoff.py`：覆盖命令参数、退出码、dry-run、JSON 和门禁报告。

**接口：**

- `pgk init/adopt/doctor/check/new/index/handoff` 保持人类输出和稳定 `--json`。
- 核心 CLI 不新增 commit、push、merge、Issue/PR 或 release 命令。
- 无匹配授权时，CLI 只输出阻塞/预览信息，不执行受保护动作。

**验证：**

- 先添加新命令和门禁失败测试；
- 实现最小 CLI 变更；
- 运行 CLI、交接、全量测试、编译和 diff 检查；
- 不执行 commit、push、PR、merge、tag、release 或删除。

## Task 6：Kit 自验证和新项目验收

**文件：**

- 修改 `docs/STATUS.md`、`docs/work/INDEX.md`、`docs/work/tasks/TASK-005-implement-v0-1-new-project-governance-baseline.md`。
- 修改 `docs/verification/VER-001-v0-1-new-project-baseline.md`；
- 新增 `tests/fixtures/new-project/` 作为空新项目 fixture；
- 更新 `README.md`、`README.en.md` 和 `docs/usage.md` 的新项目流程。

**接口：**

- 自验证通过 `pgk check`、项目测试和文档校验完成；
- fixture 验证 initialized → requirements_discussion，且不生成业务 REQ。

**验证：**

- 在 fixture 执行初始化、检查、六/七类记录生成、视图更新和 handoff；
- 运行全量测试、编译、`pgk check` 和项目文档校验；
- 记录所有未验收边界；
- 只在用户明确确认后提交或公开发布。
