---
id: VER-005
type: verification
status: verified
created: 2026-09-17
updated: 2026-09-17
related:
  - TASK-017
  - REQ-003-ZH
  - DES-004-ZH
---

# Skill five-element contract verification

## Purpose

验证 Project Governance Kit Skill 的运行时指令明确包含触发场景、输入、流程、输出和
验收五个要素，并保持 TASK-016 已验证的安全行为。

## Owner

root

## Scope

- 仓库和用户级安装位置的 `project-governance-kit/SKILL.md`；
- 五要素内容覆盖和 Codex Skill 格式；
- PGK 对 Skill frontmatter、链接和治理记录的一致性检查。

## Acceptance

- 五个中文要素均在运行时 `SKILL.md` 中直接可见；
- Inputs 明确写入前必需信息、可选信息、默认规则和最小澄清规则；
- Acceptance criteria 可以判断三类项目是否到达正确暂停点；
- 授权边界和禁止覆盖规则未弱化；
- 仓库与安装副本一致，检查通过。

## Evidence

- 运行时 `SKILL.md` 明确包含“触发场景、输入、流程、输出、验收标准”五个中文一级章节；
- 合同检查确认必需输入、可选输入、默认值、最小澄清、禁止覆盖和唯一下一步均已声明；
- 仓库 Skill 和用户级安装副本均通过 Codex 官方 `quick_validate.py`；
- Windows 环境以 `PYTHONUTF8=1` 运行官方校验器，避免系统默认 GBK 误读 UTF-8 中文文件；
- description 恢复为约 82 个字符，保留触发范围、核心能力和关键边界，不重复正文流程和验收内容；
- 仓库 `skills/project-governance-kit/` 与
  `%USERPROFILE%\.codex\skills\project-governance-kit` 逐文件 SHA-256 一致；
- 检查器专项回归：`31 passed in 22.22s`；
- `pgk index` 成功重建生成索引；
- `git diff --check` 通过；
- `pgk check` 只报告 TASK-017 当前未提交状态，无 Skill、链接、记录或状态语义错误。

## Changes

- 把原有触发边界从 frontmatter 提升为运行时显式章节；
- 增加写入前必需输入和可选输入契约；
- 保留原有分类、流程和授权门禁；
- 将输出契约重命名为明确的 Outputs；
- 增加三类项目可执行的完成验收和失败报告规则。
- 将 Skill 正文、UI 简介和默认提示本地化为中文，并把 frontmatter description 压缩为
  一句触发与边界说明；详细流程和验收只保留在正文。

## Blockers

无。

## Next action

TASK-017 已验证；GitHub 发布使用独立任务记录。
