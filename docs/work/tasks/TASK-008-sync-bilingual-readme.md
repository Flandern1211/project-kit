---
id: TASK-008
type: task
status: verified
created: 2026-09-07
updated: 2026-09-07
related:
  - ADR-0002
  - TASK-007
---

# Sync bilingual README documentation

## Purpose

同步中文版和英文版 README，说明治理 profile、协作模式和 v0.1 的使用边界。

## Owner

root

## Scope

- 更新 `README.md` 和 `README.en.md`；
- 保持命令、profile、协作模式和延期范围语义一致；
- 不修改代码或运行时行为。

## Files

- `README.md`；
- `README.en.md`；
- `docs/work/tasks/TASK-008-sync-bilingual-readme.md`。

## Acceptance

- 中英文 README 都说明 Lite/Standard/Strict；
- 中英文 README 都说明 single-agent/sequential-agents；
- 中英文 README 都包含初始化命令示例；
- 两份 README 都明确并行 Agent 协作暂不属于 v0.1。

## Evidence

已检查中英文段落和命令示例；`git diff --check` 通过。

## Changes

已同步 profile、协作模式和初始化命令说明。

## Blockers

无。

## Next action

任务已验证；如需发布文档更新，使用现有任务分支提交并推送。

## Git

branch: task/TASK-007-governance-profiles
worktree: repository checkout
base_commit: 4e6294b
head_commit: working tree
