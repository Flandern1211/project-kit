---
id: TASK-007
type: task
status: verified
created: 2026-09-07
updated: 2026-09-07
related:
  - ADR-0002
  - REQ-001-ZH
  - DES-002-ZH
---

# Implement governance profiles and collaboration mode baseline

## Purpose

实现 ADR-0002 确认的 Lite/Standard/Strict profile 基础行为，以及 v0.1 支持的
single-agent/sequential-agents 协作模式配置。

## Owner

root

## Scope

- profile 配置解析和校验；
- Lite、Standard、Strict 初始化产物差异；
- 协作模式配置和 v0.1 并行模式拒绝；
- `pgk check` 按 profile 检查必需产物；
- 不实现并行调度、worktree 协调、自动评估、远程集成或自动 Git 公开操作。

## Files

- `src/project_governance/config.py`；
- `src/project_governance/scaffold.py`；
- `src/project_governance/checks.py`；
- `src/project_governance/records.py`；
- `src/project_governance/cli.py`；
- `tests/test_profiles.py`。

## Acceptance

- Lite、Standard、Strict 初始化产物符合已确认 profile 约束；
- single-agent 和 sequential-agents 可写入配置；parallel-agents 在 v0.1 被拒绝；
- profile 缺失产物由 `pgk check` 报告；
- 既有测试不回归。

## Evidence

`py -3 -m pytest --basetemp D:\pgk-full-final -q`：92 passed。
`py -3 -m compileall -q src tests`：passed。
`git diff --check`：passed。
`pgk check` 文档/link 检查通过；剩余 dirty worktree 和未登记的
`task/TASK-006-v02-migration` 属于现有工作区状态，按用户说明不处理。

## Changes

已实现配置校验、profile 文件选择、协作模式参数、profile-aware checks、Lite 禁止
未启用记录类型和相关测试。

## Blockers

无。并行 Agent 协作和自动治理等级评估属于延期范围。

## Next action

验证完成；Lite/Standard/Strict 和 single/sequential 配置基础行为已实现。
自动 profile 评估、parallel-agents 和远程集成仍为延期范围。

## Git

branch: task/TASK-007-governance-profiles
worktree: N/A
base_commit: N/A
head_commit: N/A
