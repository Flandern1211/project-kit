---
id: TASK-003
type: task
status: verified
created: 2026-09-03
updated: 2026-09-03
related:
  - REQ-001-ZH
---
# Refine new-project governance requirements

## Purpose

把 Project Governance Kit v0.1 明确为面向新项目的文档驱动开发治理架构，并补充
Agent 行为、可视化、Git 协同和用户授权门禁。

## Scope

- 修订中文 v0.1 需求基线；
- 同步英文需求并标记旧技术设计待修订；
- 将用户确认的 commit/PR 等授权规则写入需求；
- 为后续设计审查保留明确的默认规则和边界。

## Acceptance

- 需求明确只面向新项目初始化；
- 初始化产物、文档节点、日志/活动记录、状态和可视化方式明确；
- Agent 每次开发的读取、记录、验证和交接步骤明确；
- Git 分支/worktree 和 commit、push、PR、merge、tag、release 授权规则明确；
- 需求草案被用户确认前不进入实现。

## Evidence

- 用户已确认中文 v0.1 需求基线；
- `pgk check --root . --json` 返回 `ok=true`，无问题；
- 项目文档校验返回 0 errors、0 warnings；
- 英文需求已同步，章节、FR、NFR、AC 和默认决策与中文基线一致。

## Changes

- 将中文需求文档标记为已确认基线；
- 同步英文需求文档；
- 补充新项目初始化目录和索引；
- 补充文档驱动生命周期、状态节点、活动记录和 Git 协同要求；
- 补充远程和不可逆 Git 操作的逐项用户确认门禁；
- 更新 README、文档索引和项目状态。

## Blockers

- 技术设计需要按已确认需求重新修订；
- 尚未开始实现。

## Next action

下一步创建技术设计修订草案，供用户单独审查。

## Owner

root

## Files

- `docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.md`;
- `docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.zh-CN.md`.

## Git

branch: codex/TASK-003-v01-requirements
worktree: repository checkout
base_commit: N/A
head_commit: N/A

## Handoff

<!-- PGK_HANDOFF_START -->
Status: verified
Branch: codex/TASK-003-v01-requirements
HEAD: N/A
Worktree: repository checkout
Dirty: true
Uncommitted: present
Verification: requirements review recorded
Blockers: none
Next action: create the technical design revision
<!-- PGK_HANDOFF_END -->
