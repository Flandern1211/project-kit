---
id: VER-002
type: verification
status: verified
created: 2026-09-07
updated: 2026-09-08
related:
  - REQ-002-ZH
  - DES-003-ZH
  - TASK-006
---

# v0.2 migration MVP verification

## Purpose

验证已有项目补齐与文档迁移 MVP 的本地行为、非破坏边界、迁移状态和 CLI 流程。

## Owner

root

## Scope

`task/TASK-006-v02-migration` worktree 中的 v0.2 代码、测试和治理文档。

## Acceptance

- 补齐模式保留已有文件和已有 `STATUS.md` 状态；
- `MIG-*` 方案支持候选、批准、排除和逐项状态；
- 未批准条目不生成治理副本；
- Markdown/纯文本副本保留来源路径和 SHA-256，原文件不变；
- 敏感内容、生成治理目录、越界路径和不支持格式不会被自动复制；
- 源文件变化、目标冲突、失败和重复运行可确定性报告；
- `adoption_review` 和 MIG 索引/检查均可识别；
- 核心 CLI 未增加 Git/远程受保护动作。

## Evidence

```text
py -3 -m pytest --basetemp .pytest-tmp-count -q
120 passed

py -3 -m compileall -q src
exit 0

git diff --check
exit 0

py -3 -m project_governance check --root . --json
```

迁移验收 fixture、扫描、方案、批准、应用、冲突、幂等和 CLI 测试均通过。系统 pytest 临时目录曾返回 Windows `WinError 5`，验证使用 worktree 内 `--basetemp` 完成。

使用当前 worktree 源码运行 `PYTHONPATH=src py -3 -m project_governance check --root . --json` 的治理结果不是 clean：它只报告当前 worktree 的未提交修改，以及共享仓库中未登记的其他 `task/*` 分支。直接使用已安装模块可能解析到其他 checkout，因此验收命令显式绑定本 worktree 的 `src`。这些共享环境状态未被本任务擅自清理；本任务自身没有执行 commit、push、PR、merge、tag、release 或删除。

## Changes

实现包含：

- `migration` 记录模型、模板、索引和来源哈希；
- `init --mode supplement` 与 `adoption_review`；
- `pgk migrate plan/approve/apply`；
- Markdown/纯文本非破坏治理副本；
- MIG 来源、目标、状态、索引和冲突检查；
- 中英文 README、使用说明和 v0.2 版本号。

## Blockers

无代码阻塞。共享 Git 工作区的脏状态和其他未登记分支需要仓库维护者在合并前按其所属任务处理。

## Next action

审查本分支完整 diff；获得明确授权后再决定是否 commit、push 或创建 PR。
