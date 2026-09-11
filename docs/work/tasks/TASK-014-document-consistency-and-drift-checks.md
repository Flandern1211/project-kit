---
id: TASK-014
type: task
status: verified
created: 2026-09-11
updated: 2026-09-11
related:
  - REQ-001-ZH
  - DES-002-ZH
  - REQ-002-ZH
  - DES-003-ZH
---
# Document consistency and drift checks

## Purpose

修正文档、版本配置和当前实现之间的漂移，并让 `pgk check` 自动阻止同类问题再次进入交接或发布。

## Owner

root

## Scope

- 统一 Project Governance Kit 当前版本、STATUS 和中英文 README；
- 删除 STATUS 中已过时的“尚未实现”和旧提交/推送表述；
- 为 Kit 自身增加版本一致性检查；
- 让已合并到当前 HEAD 的历史任务分支不再触发未登记分支错误；
- 把文档一致性要求写入 Agent 指令、约定和工作流；
- 在使用说明中维护可人工审查的当前能力矩阵；
- 不改变业务项目自身版本与 Kit 版本的独立性。

## Files

- `.project-governance.toml`、`pyproject.toml`；
- `README.md`、`README.en.md`；
- `AGENTS.md`、`docs/STATUS.md`、`docs/WORKFLOW.md`、`docs/project-conventions.md`；
- `src/project_governance/version.py`、`src/project_governance/checks.py`、`src/project_governance/scaffold.py`；
- 相关测试、索引和活动记录。

## Acceptance

- Kit 当前版本只由代码中的单一版本模块定义，构建配置引用该版本；
- `.project-governance.toml`、STATUS 和双语 README 均声明 `0.2.0.dev0`；
- STATUS 不再把已实现的 profile/visibility/migration 写成未实现；
- `pgk check` 能报告 Kit 版本漂移，但不比较业务项目版本；
- 已合并历史任务分支不触发 `unregistered_branch`；
- 当前能力矩阵覆盖真实 CLI 的全部顶层命令；
- 工作索引按 active/planned/completed 分组，不把已验证任务伪装成 active；
- 聚焦测试、全量测试、compileall、diff-check、`pgk check` 和 `pgk doctor` 有新鲜证据。

## Evidence

已完成当前工作树验证：`py -3 -m pytest -o addopts="" --basetemp .pytest-tmp-task014-final6 -q`：
`161 passed in 70.46s`；
`py -3 -m compileall -q src tests` 通过；`git diff --check` 通过；使用当前 worktree
源码运行 `PYTHONPATH=src py -3 -m project_governance check --root . --json` 只报告本任务
未提交导致的 dirty worktree；`doctor --json` 报告 Python、pytest、Git、仓库和临时目录预检可用。
`PYTHONPATH=src py -3` 导出的 Kit 版本为 `0.2.0.dev0`。

## Changes

已实现版本单一来源、版本漂移检查、STATUS 引用和上游关联检查、未知配置字段检查、
已合并分支过滤、当前分支登记检查、当前能力矩阵和当前文档同步。`uv build --wheel`
成功生成 `project_governance_kit-0.2.0.dev0-py3-none-any.whl`；系统 Python 缺少独立
`build`/`setuptools` 模块，因此构建验证使用已安装的 `uv` 隔离构建环境完成。

## Blockers

无。

## Next action

后续行为或当前状态文档变更须创建新的 TASK。

## Git
branch: task/TASK-014-document-consistency
worktree: D:/Project/project-kit/.worktrees/document-consistency
base_commit: 3c56b49
head_commit: this commit

## Handoff

<!-- PGK_HANDOFF_START -->
<!-- PGK_HANDOFF_END -->
