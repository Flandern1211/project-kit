---
id: VER-003
type: verification
status: verified
created: 2026-09-08
updated: 2026-09-08
related:
  - TASK-012
  - REQ-002-ZH
  - DES-003-ZH
---

# Migration relative-link verification

## Purpose

验证迁移治理副本改变目录后，已有 Markdown 相对链接仍可解析。

## Owner

root

## Scope

TASK-012 的 Markdown 相对链接重写实现、单元测试和 TouzhiAgent 隔离 clone。

## Acceptance

- 已迁移目标链接改写到治理副本；
- 未迁移但存在的目标链接改写到源项目文件；
- 外部 URL 和锚点保持不变；
- 真实 TouzhiAgent clone 迁移后无 broken-link issue。

## Evidence

- 新增相对链接单元测试：已迁移目标、保留源文件目标和外部 URL；
- `py -3 -m pytest --basetemp <worktree-temp> -q`：139 passed；
- TouzhiAgent Git clone 真实项目流程：supplement、MIG plan、approve、apply；
- 4 个治理副本生成，原项目文件保持未修改；
- clone 上 `PYTHONPATH=<project-kit-src> py -3 -m project_governance check --root <clone> --json` 无 broken_link issue；
- Project Kit 全量测试和 TouzhiAgent 原项目业务测试分开验证。

## Result

已迁移目标被改写为治理副本路径，未迁移但存在的目标被改写为源项目相对路径，外部 URL 保持不变。

## Blockers

不存在的源链接仍保留并需要人工处理；Kit 不会猜测不存在的目标。

## Next action

将 TASK-012 合并回 `main` 后，再决定是否 push。
