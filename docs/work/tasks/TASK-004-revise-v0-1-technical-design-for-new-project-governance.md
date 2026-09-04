---
id: TASK-004
type: task
status: verified
created: 2026-09-04
updated: 2026-09-04
related:
  - REQ-001-ZH
  - REQ-001
---
# Revise v0.1 technical design for new-project governance

## Purpose

根据已确认的 v0.1 需求，设计新项目初始化、文档驱动 Agent 开发、可视化、Git 协同
和用户授权门禁的实现边界。

## Scope

- 新增当前 v0.1 中文技术设计；
- 明确初始化文件树、记录模型、项目阶段和记录状态；
- 明确 Agent 读取顺序、状态门禁、Review/Verification 和 handoff；
- 明确 Git 分支/worktree、授权记录和保护动作；
- 明确 STATUS、BOARD、WORKFLOW、INDEX、ACTIVITY 的职责和更新规则；
- 不修改实现代码，等待设计审查后再更新实施计划。

## Acceptance

- 设计覆盖 REQ-001 的 FR/NFR/AC；
- 设计不引入需求之外的自动远程操作、模型调用或 Web 后台；
- 初始化、文档链、状态、可视化、Git 和授权边界可被实现和测试；
- 中文设计经用户确认后再同步英文设计并进入实现。

## Evidence

用户已确认 DES-002-ZH；当前设计基线已用于 TASK-005 实现和 VER-001 验收。

## Changes

- 新增 `docs/design/2026-09-04-project-governance-kit-v0.1-design.zh-CN.md`；
- 更新设计索引、项目状态和工作索引；
- 保留 `DES-001` 作为历史设计草案。

## Blockers

- 等待用户确认 DES-002-ZH；
- 设计确认前不修改实现代码或实施计划。

## Next action

请用户审查中文技术设计；确认后再同步英文设计、更新实施计划并开始实现。

## Owner

root

## Files

- `docs/design/2026-09-04-project-governance-kit-v0.1-design.zh-CN.md`;
- design index and linked requirements.

## Git

branch: codex/TASK-004-v01-design
worktree: repository checkout
base_commit: N/A
head_commit: N/A

## Handoff

<!-- PGK_HANDOFF_START -->
Status: verified
Branch: codex/TASK-004-v01-design
HEAD: N/A
Worktree: repository checkout
Dirty: true
Uncommitted: present
Verification: technical design review recorded
Blockers: none
Next action: implement the accepted design baseline
<!-- PGK_HANDOFF_END -->
