---
id: TASK-018
type: task
status: verified
created: 2026-09-17
updated: 2026-09-17
related:
  - TASK-017
  - VER-005
---

# TASK-018 发布 Project Governance Kit Skill 到 GitHub

## Purpose

把已验证的 `project-governance-kit` Skill 发布到用户的公开仓库
`Flandern1211/skills`，遵循该仓库的英文规范入口和中文本地化约定。

## Owner

root

## Scope

- 确认 GitHub 账号、目标仓库、默认分支和发布规则；
- 在目标仓库创建 `feat/project-governance-kit` 分支；
- 发布英文 `SKILL.md`、中文 `SKILL.zh-CN.md` 和 `agents/openai.yaml`；
- 更新目标仓库中英文 README；
- 校验 Skill、链接、YAML、敏感信息和 Git 差异；
- 推送功能分支并创建面向 `main` 的 PR；
- 不直接推送或合并 `main`。

## Files

- 外部仓库 `Flandern1211/skills` 中的 `skills/project-governance-kit/`；
- 外部仓库 `README.md` 和 `README.zh-CN.md`；
- 本任务、STATUS、活动和生成索引。

## Acceptance

- 目标仓库和来源账号准确；
- 英文规范入口和中文完整版均通过格式与五要素检查；
- README 链接有效，UI YAML 可解析；
- 无凭据或机器私有数据；
- 功能分支基于最新 `origin/main`；
- PR 已创建且 base/head 准确，未直接修改远程 `main`。

## Evidence

- GitHub 登录账号：`Flandern1211`；目标仓库：`Flandern1211/skills`；base：`main`；
- 目标仓库无 CONTRIBUTING、Issue/PR 模板、分支保护或历史 PR；历史样本数量为 0，
  明确标记 sample insufficient；
- 英文规范入口通过 Codex `quick_validate.py`；中文本地化 frontmatter 和五要素检查通过；
- README 相对链接与 `agents/openai.yaml` 解析通过；敏感信息扫描无匹配；
- `git diff --check` 通过；发布差异为 5 个文件、331 行新增；
- 分支在 `origin/main@8c0f186` 更新后通过普通 merge 同步，无冲突；
- 远程分支 `feat/project-governance-kit` 已推送，HEAD
  `db524943069f3c4d1e8ff554eba174242efac085`；
- PR [#1 Add project-governance-kit skill](https://github.com/Flandern1211/skills/pull/1)
  已创建：`OPEN`、非 draft、`MERGEABLE/CLEAN`、base=`main`、head=`feat/project-governance-kit`；
- PR 当前没有 CI check；未执行 merge。

## Changes

- 已确认目标为 `Flandern1211/skills`，默认分支 `main`；
- 已读取仓库 README 语言和目录约定；
- 已发布英文入口、中文完整版、Codex UI 元数据并更新中英文 README；
- 已推送功能分支并创建 PR #1。

## Blockers

无发布 blocker。PR 仍待用户审查和决定是否合并。

## Next action

审查 PR #1；合并属于独立远程动作，尚未执行。

## Git

branch: codex/task-018-publish-skill
worktree: D:/Project/project-kit
base_commit: ca2a64a
head_commit: 12c2714
