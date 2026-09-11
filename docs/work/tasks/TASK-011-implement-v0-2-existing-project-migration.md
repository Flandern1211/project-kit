---
id: TASK-011
type: task
status: verified
created: 2026-09-07
updated: 2026-09-08
related:
  - REQ-002-ZH
  - DES-003-ZH
---

# Implement v0.2 existing-project adoption and migration

## Purpose

在 v0.1 新项目初始化基础上实现已有项目的补齐模式和文档迁移 MVP，保持原文件、Git 和用户批准边界不变。

## Owner

root

## Scope

- 增加 `adoption_review` 阶段支持；
- 保持 `adopt` 只读并扩展候选扫描信息；
- 增加补齐模式参数和已有项目状态保护；
- 增加 `MIG-*` 记录模型、模板、索引和迁移方案；
- 支持 Markdown/纯文本治理副本；
- 实现批准门禁、幂等、来源哈希、冲突不覆盖和失败隔离；
- 扩展 `pgk check`、活动记录和验证测试；
- 不实现复杂格式转换、语义重写、代码重构或远程 Git 操作。

## Acceptance

- v0.2 需求和设计通过用户书面审查；
- 补齐模式不覆盖、移动、删除或合并已有文件；
- 迁移方案和副本具有稳定来源映射与逐项状态；
- 未批准条目不能应用；
- 重复、变化、冲突、敏感内容和失败继续均有确定性结果；
- 测试、编译检查、文档检查和迁移 fixture 验证通过；
- 受保护 Git/远程动作未被核心 CLI 执行。

## Evidence

用户已于 2026-09-07 确认 REQ-002-ZH 和 DES-003-ZH。代码实现和本地验证已完成，证据见 [VER-002](../../verification/VER-002-v0-2-migration-mvp.md)。

## Changes

当前分支已新增：

- `docs/requirements/2026-09-07-project-governance-kit-v0.2-migration-requirements.zh-CN.md`；
- `docs/design/2026-09-07-project-governance-kit-v0.2-migration-design.zh-CN.md`；
- 本任务记录。
- `docs/superpowers/plans/2026-09-07-project-governance-kit-v0.2-migration-implementation.md`。
- v0.2 运行时代码、测试、使用说明和 VER-002。

## Blockers

无。验证时的共享 worktree 状态已由后续合并收口；受保护 Git/远程动作仍需用户明确授权。

## Next action

实现已合并并由 VER-002 验证；后续改动须创建新的 TASK。

## Files

- `src/project_governance/`；
- `tests/`；
- `docs/requirements/`、`docs/design/`、`docs/migrations/`、`docs/templates/`；
- `docs/checks/`（如现有结构需要）。

## Git

branch: task/TASK-006-v02-migration
worktree: C:/Users/31800/.codex/worktrees/bc83/project-kit
base_commit: 94f663bb2445458e599ce18a72362355c011560a
head_commit: 8d57cd7

## Handoff

<!-- PGK_HANDOFF_START -->
Status: verified
Branch: task/TASK-006-v02-migration
HEAD: 94f663bb2445458e599ce18a72362355c011560a
Worktree: C:/Users/31800/.codex/worktrees/bc83/project-kit
Dirty: true
Uncommitted: none at the verification commit
Verification: 120 tests passed; compileall and git diff --check passed; merged-result verification is recorded in VER-002
Blockers: none; protected Git and remote actions still require explicit user authorization
Next action: use a new task record for subsequent migration changes
<!-- PGK_HANDOFF_END -->
