---
id: TASK-012
type: task
status: verified
created: 2026-09-08
updated: 2026-09-08
related:
  - REQ-002-ZH
  - DES-003-ZH
  - TASK-011
---

# Fix relative links in migrated governance copies

## Purpose

修复 v0.2 迁移副本改变目录后导致 Markdown 相对链接失效的问题。

## Owner

root

## Scope

- 迁移到治理副本的目标文件，链接改写为目标治理副本路径；
- 未迁移但仍存在于源项目中的目标，链接改写为源项目目标的相对路径；
- 外部 URL、锚点、绝对路径和不存在的目标保持原样；
- 原文件不修改；
- 补充真实项目 fixture 和迁移检查测试。

## Acceptance

- 已迁移目标的相对链接在治理副本中可以解析；
- 未迁移但存在的源目标仍能从治理副本解析；
- 外部链接和锚点不被改写；
- TouzhiAgent 类似的 PRD/TSD/DESIGN 文档迁移后不因已存在的相对链接产生断链；
- v0.1、profile、visibility 和 v0.2 原有测试保持通过。

## Evidence

120 项主项目测试和链接专项测试通过；真实 TouzhiAgent clone 迁移后 `pgk check` 不再报告原有相对链接断链。

## Blockers

无。当前只在独立 worktree 工作，不修改 TouzhiAgent。

## Next action

TASK-012 已合并到本地 `main` 的 7ebef4c；push 仍需用户单独授权。

## Files

- `src/project_governance/migration.py`；
- `tests/test_migration_links.py`；
- `docs/usage.md`、迁移设计和验证记录。

## Git

branch: task/TASK-012-migration-relative-links
worktree: D:/Project/project-kit/.worktrees/touzhi-link-fix
base_commit: bcf8d1e
head_commit: 7ebef4c
