---
id: TASK-006
type: task
status: verified
created: 2026-09-07
updated: 2026-09-07
related:
  - ADR-0002
  - REQ-001-ZH
  - DES-002-ZH
---

# Record governance profile and v0.1 scope revision

## Purpose

将 2026-09-07 已确认的治理等级、Agent 协作模式分离和 v0.1 延期范围同步到
权威需求、设计、状态和索引文档。

## Owner

root

## Scope

- 更新中英文需求和设计基线；
- 新增 ADR-0002；
- 更新状态、索引、看板和活动记录；
- 不修改业务实现代码；
- 不执行 commit、push、merge 或远程平台操作。

## Files

- `docs/requirements/`；
- `docs/design/`；
- `docs/decisions/ADR-0002-governance-profiles-and-v0-1-scope.md`；
- `docs/STATUS.md`；
- `docs/INDEX.md`；
- `docs/work/INDEX.md`；
- `docs/work/BOARD.md`；
- `docs/activity/ACTIVITY.md`。

## Acceptance

- 最新确认内容有唯一可追溯记录；
- 旧版并行 Agent 范围被明确标记为 v0.1 延期；
- Lite/Standard/Strict 与协作模式分离；
- 文档索引、状态和看板保持一致；
- `pgk check` 无新增文档结构错误。

## Evidence

已运行 `py -3 -c "import sys; from project_governance.cli import main; sys.exit(main(['check','--root','.','--json']))"`。
治理检查不再报告本任务引入的断链或字段错误；剩余报告为既有脏工作区、已存在的
链接 worktree 脏状态和未登记的 `task/TASK-006-v02-migration` 分支。

## Changes

已同步 ADR-0002、需求、设计、状态、索引、看板和活动记录；未修改业务实现代码。
Lite/Standard/Strict 的运行时 profile 行为和协作模式配置仍需后续实现任务，不能
以本任务的文档同步作为代码功能已实现的证据。

## Blockers

无。

## Next action

TASK-006 已验证；profile 运行时行为由后续 TASK-007 实现，并行协作仍属延期范围。

## Git

branch: N/A
worktree: N/A
base_commit: N/A
head_commit: N/A
