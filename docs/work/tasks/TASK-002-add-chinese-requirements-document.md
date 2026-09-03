---
id: TASK-002
type: task
status: verified
created: 2026-09-03
updated: 2026-09-03
related:
---
# Add Chinese requirements document

## Purpose

让中文使用者可以直接阅读和审查 Project Governance Kit v0.1 的正式需求。

## Scope

- 保留英文需求原文；
- 新增内容一致的中文版；
- 在索引和中文、英文 README 中提供对应入口；
- 保留中英文文档之间的对应关系。

## Acceptance

- 中文文档覆盖英文原文的目标、范围、FR、NFR、非范围和 AC；
- 两个 README 和文档索引链接到中文版；
- `pgk check` 和项目文档校验通过；
- 不修改需求语义，不引入新的产品范围。

## Evidence

- `pgk check --root . --json` 返回 `ok=true`，无问题；
- `D:\skills\bootstrap-project-governance\scripts\validate_project_docs.py .`
  返回 0 errors、0 warnings；
- 中文文档保留 FR-01 至 FR-07、NFR、非范围和 AC-01 至 AC-08 编号；
- 中文和英文 README、英文原文及文档索引的语言链接已建立。

## Changes

- 新增 `docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.zh-CN.md`；
- 在英文原文中加入中文版本链接；
- 更新中英文 README 和 `docs/INDEX.md` 的需求入口；
- 更新工作索引和本任务记录。

## Blockers

无。

## Next action

审查中文版需求，确认后开始 TouzhiAgent 的第一次外部接入试验。

## Handoff

<!-- PGK_HANDOFF_START -->
Status: verified
Branch: codex/bootstrap-v0.1
HEAD: 573a208377a52e252299d8bafad400114987c8ce
Worktree: dirty
Verification: pgk check ok; document validator 0 errors
Blockers: none
Next action: review the Chinese requirements document
<!-- PGK_HANDOFF_END -->
