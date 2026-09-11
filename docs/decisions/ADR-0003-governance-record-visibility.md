---
id: ADR-0003
type: decision
status: accepted
created: 2026-09-07
updated: 2026-09-11
related:
  - ADR-0002
  - TASK-009
---

# ADR-0003 Governance record visibility

## Purpose

记录用户确认的方向：团队内部需要通过 Git 共享完整治理文档，但公开项目不应
暴露内部需求、设计过程、Agent 日志、Bug、Review 和交接记录。

## Scope

适用于 Project Governance Kit 的通用可见性架构；不改变业务项目内容，也不修改
已经合并的 PR #1。

## Acceptance

用户已确认采用团队私有仓库协作、公开发布时使用筛选后文档的方向，并同意先完成
规格，再实现 visibility 功能。

## Evidence

用户在 2026-09-07 会话中确认：团队内部使用完整文档，其他人无法查看；Kit 自身不
公开全部开发过程。

## Changes

具体模式和实现边界见
`docs/superpowers/specs/2026-09-07-governance-visibility-design.md`。

## Blockers

无。实现和验证已由 TASK-010 完成；公开副本导出、仓库拆分、历史清理和远程权限修改仍属延期范围。

## Next action

继续按 TASK-010、VER-002 和当前 `docs/STATUS.md` 维护已实现的可见性边界。
