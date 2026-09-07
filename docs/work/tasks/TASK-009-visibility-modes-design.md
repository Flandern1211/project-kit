---
id: TASK-009
type: task
status: verified
created: 2026-09-07
updated: 2026-09-07
related:
  - ADR-0003
  - REQ-001-ZH
---

# Design governance record visibility modes

## Purpose

将团队私有协作、公开项目文档和治理记录可见性分离，形成可审核的实现规格。

## Owner

root

## Scope

- 编写治理记录可见性设计规格；
- 定义 `team-private`、`hybrid`、`public`；
- 明确与 profile、协作模式和 Git 远程权限的边界；
- 暂不修改运行时代码。

## Files

- `docs/superpowers/specs/2026-09-07-governance-visibility-design.md`；
- `docs/decisions/ADR-0003-governance-record-visibility.md`；
- 需求、设计和索引文档将在规格批准后同步。

## Acceptance

- 规格明确团队私有仓库与公开发布的边界；
- 规格明确三种 visibility 模式；
- 规格明确 Git 历史隐私风险和不自动删除原则；
- 用户审核规格后才能进入实现计划。

## Evidence

用户已审核并批准书面规格。

## Changes

已创建并批准书面设计规格；实现由 TASK-010 完成。

## Blockers

规格已获用户批准；实现由 TASK-010 执行。

## Next action

规格已审核通过；继续执行 TASK-010。

## Git

branch: task/TASK-009-visibility-modes
worktree: repository checkout
base_commit: e23fd9a
head_commit: working tree
