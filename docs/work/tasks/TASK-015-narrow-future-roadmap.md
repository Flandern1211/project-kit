---
id: TASK-015
type: task
status: verified
created: 2026-09-16
updated: 2026-09-16
related:
  - ADR-0004
  - REQ-001-ZH
  - DES-002-ZH
---

# TASK-015 收口未来功能路线图

## Purpose

把用户确认的未来功能范围同步到权威记录和当前用户文档，消除“非范围等于未来待办”
的歧义。

## Owner

root

## Scope

- 新增 ADR-0004，记录唯一两个后续扩展和明确非目标；
- 同步中英文需求、设计、STATUS、README 和使用说明；
- 更新索引、工作板和活动记录；
- 不实现新功能，不改变版本和配置。

## Files

- `docs/decisions/ADR-0004-roadmap-scope.md`
- `docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements*.md`
- `docs/design/2026-09-04-project-governance-kit-v0.1-design.zh-CN.md`
- `docs/STATUS.md`
- `docs/usage.md`
- `README.md`
- `README.en.md`
- 相关索引、工作板和活动记录

## Acceptance

- 当前文档只把并行 Agent 协作安全/worktree 管理和受授权本地自动 commit 列为后续扩展；
- 其他讨论过的候选能力明确为 non-goal，不再写成延期路线图；
- 历史 ADR、任务和验证证据保留；
- 文档链接和治理检查完成。

## Evidence

- `pgk index --root . --json`：成功重建决策、任务、工作板和其他生成索引；
- `pgk check --root . --json`：未发现链接、frontmatter、ID、索引、版本或授权问题；
  只报告当前任务未提交，以及既有 `strict-agent-guidance` worktree 的 pytest 临时目录；
- `git diff --check`：通过；
- 路线图措辞检查：当前需求、设计、STATUS、README 和 usage 只保留两个 planned 扩展。
- 2026-09-16 用户明确授权本任务执行本地 commit。

## Changes

- 新增 ADR-0004，明确 planned 与 non-goal 边界；
- 同步中英文需求、已接受设计、状态和用户文档；
- 修订 ADR-0002、ADR-0003 及相关历史任务的当前 Blockers/Next action，保留历史正文；
- 重建生成索引和工作板。

## Blockers

无。项目级 `pgk check` 仍会独立报告既有 `strict-agent-guidance` worktree 中的 pytest
临时目录；该目录不属于本任务变更。

## Next action

任务已验证；后续实现两个扩展中的任一项时创建新的需求、设计和任务。

## Git

branch: codex/task-015-roadmap-scope
worktree: D:/Project/project-kit
base_commit: 2d6acf7095b45c2bff9af727c21b8ae3f0b9072c
head_commit: f4d81c9
