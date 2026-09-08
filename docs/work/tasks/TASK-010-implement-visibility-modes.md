---
id: TASK-010
type: task
status: verified
created: 2026-09-07
updated: 2026-09-07
related:
  - ADR-0003
  - REQ-001-ZH
  - DES-002-ZH
---

# Implement governance record visibility modes

## Purpose

实现 `team-private`、`hybrid`、`public` 三种治理记录可见性，支持团队私有 Git
协作与公开项目文档分离。

## Owner

root

## Scope

- 解析和校验 visibility 配置；
- 按可见性初始化治理目录和公开文档入口；
- 让记录、索引、交接和检查使用配置的治理目录；
- 检查公开文档路径中的治理记录泄漏；
- 不修改远程仓库权限，不迁移或删除已有文件。

## Files

- `src/project_governance/config.py`；
- `src/project_governance/scaffold.py`；
- `src/project_governance/records.py`；
- `src/project_governance/handoff.py`；
- `src/project_governance/checks.py`；
- `src/project_governance/cli.py`；
- `tests/test_visibility.py`；
- `README.md`；
- `README.en.md`；
- `docs/usage.md`。

## Acceptance

- team-private 在 `.pgk/` 生成完整治理记录，适用于私有团队仓库；
- hybrid 在 `.pgk/` 生成治理记录并创建 `docs/public/`；
- public 保持现有 `docs/` 布局；
- 记录创建、索引、交接和检查在非 public 路径正常工作；
- 公开路径中的治理记录被 `pgk check` 报告；
- 既有测试和真实项目测试不回归。

## Evidence

全量测试 101 passed；可见性专项测试 11 passed；compileall 和 `git diff --check`
通过。真实测试目录 `D:\Project\test\_project\visibility2` 中 team-private、
hybrid、public 初始化与 `pgk check` 均通过，team-private 需求记录创建通过。

## Changes

已实现配置、脚手架、记录、交接、检查和 CLI 的 visibility 基础支持，并同步中英文说明。

## Blockers

无。公开副本导出、仓库拆分、历史清理和远程权限修改属于延期范围。

## Next action

实现和真实验证已完成；公开副本导出、仓库拆分、历史清理和远程权限修改另立任务。

## Git

branch: task/TASK-009-visibility-modes
worktree: repository checkout
base_commit: e23fd9a
head_commit: working tree
