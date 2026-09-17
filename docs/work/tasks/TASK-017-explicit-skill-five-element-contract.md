---
id: TASK-017
type: task
status: verified
created: 2026-09-17
updated: 2026-09-17
related:
  - REQ-003-ZH
  - DES-004-ZH
  - TASK-016
---

# TASK-017 明确 Skill 五要素契约

## Purpose

把触发场景、输入、流程、输出和验收五个要素直接写入运行时 `SKILL.md`，避免输入契约和
验收条件只隐含在流程或外部 eval 中。

## Owner

root

## Scope

- 重构 `skills/project-governance-kit/SKILL.md` 的章节层级；
- 保留 TASK-016 已验证的项目分类、确认门和授权边界；
- 同步 DES-004-ZH、CHANGELOG、STATUS、索引、活动和验证记录；
- 更新已安装的用户级 Skill 副本；
- 不改变 PGK CLI、记录模型或远程动作边界。

## Files

- `skills/project-governance-kit/SKILL.md`
- `skills/project-governance-kit/agents/openai.yaml`
- `docs/design/2026-09-16-agent-first-project-entry-design.zh-CN.md`
- `docs/verification/VER-005-skill-five-element-contract.md`
- `docs/STATUS.md`
- `CHANGELOG.md`
- 相关索引和活动记录

## Acceptance

- `SKILL.md` 使用中文明确包含触发场景、输入、流程、输出、验收标准；
- 输入区分必需、可选、默认和澄清条件；
- 验收覆盖分类、越权、覆盖保护和三类项目的停止条件；
- 原有行为评测断言仍被运行时契约覆盖；
- 仓库源码与用户级安装副本一致并通过 Codex Skill 校验。

## Evidence

- 仓库和已安装 Skill 均通过 Codex 官方快速校验；
- 五要素合同内容检查通过；
- 仓库源码与用户级安装副本逐文件 SHA-256 一致；
- 中文正文和中文 `agents/openai.yaml` 已同步到用户级安装位置；
- Windows 校验使用 `PYTHONUTF8=1` 读取 UTF-8 中文 Skill，官方校验结果为 `Skill is valid!`；
- frontmatter description 恢复为约 82 个字符，完整保留触发范围、核心能力和关键边界；
- 检查器专项测试 `31 passed in 22.22s`；
- `pgk index` 和 `git diff --check` 通过；
- `pgk check` 除当前未提交状态外无问题；
- 正式验证见 VER-005。
- 用户确认采用 82 字 description，并明确要求将最终 Skill 提交到 GitHub skills 仓库；

## Changes

- 已新增五要素一级章节；
- 已同步 DES-004-ZH、CHANGELOG、STATUS、索引和 VER-005；
- 已更新并验证用户级安装副本。
- 已将 Skill 正文和 Codex UI 提示本地化为中文；description 精简为一句触发与边界说明。

## Blockers

无。

## Next action

TASK-017 已完成；GitHub 发布由新的 TASK-018 跟踪。

## Git

branch: codex/task-017-skill-five-elements
worktree: D:/Project/project-kit
base_commit: c80d82a8a4dacca3cf35f0b1caebec6c49d3ab95
head_commit: final task commit
