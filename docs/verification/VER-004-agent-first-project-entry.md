---
id: VER-004
type: verification
status: verified
created: 2026-09-17
updated: 2026-09-17
related:
  - TASK-016
  - REQ-003-ZH
  - DES-004-ZH
---

# Agent-first project entry verification

## Purpose

验证用户可以通过自然语言让 Agent 安全操作 PGK，而不需要先手工初始化项目，并确认
Skill 不会绕过需求确认、已有项目只读接入和 Git 受保护动作边界。

## Owner

root

## Scope

- `skills/project-governance-kit/` Skill、Codex UI 元数据和行为评测；
- Skill frontmatter 与生成评测工作区的 `pgk check` 处理；
- REQ-003-ZH / DES-004-ZH 的 new、existing、governed 三类流程；
- 中英文用户文档和安装边界。

## Acceptance

- 新项目预览并初始化，只创建 draft REQ，停在需求确认；
- 已有项目只运行 adopt/doctor，现有代码和文档保持不变；
- 已治理项目不重复初始化，恢复 STATUS 和活动任务；
- 三类流程均不隐式执行 Git 或远程受保护动作；
- Skill 通过 Codex 官方快速校验；
- 完整项目测试和语义检查无新增失败。

## Evidence

- 用户审核并批准三条 iteration-1 评测提示和静态评测结果；
- 独立 Agent 对照评测：with-skill 15/15（100%），without-skill 12/15
  （80%），delta `+0.20`；
- 新项目基线提前创建 TASK-001，Skill 只创建 draft REQ-001；
- 已有项目基线未运行 doctor，Skill 完成 adopt + doctor 且 fixture 哈希保持不变；
- 已治理项目两组均 5/5，证明恢复流程安全，但该场景不是区分性测试；
- 每个场景/配置仅运行一次，未据此声称性能或方差结论；
- Codex `skill-creator/scripts/quick_validate.py skills/project-governance-kit`：通过；
- `evals/evals.json` JSON 解析：通过；
- `python -m compileall -q src`：通过；
- Python 3.14 全量测试：`164 passed in 52.75s`；
- 检查器专项测试：`31 passed in 16.69s`；
- Skill checker smoke test：合法 frontmatter 通过，缺失 description/目录名不匹配正确报告；
- Markdown 检查在目录遍历阶段剪枝忽略目录，生成评测工作区不再造成递归扫描开销；
- `git diff --check`：通过；
- `pgk check` 在目录剪枝后约 2 秒完成，只报告当前 TASK-016 未提交状态，无新增语义问题。

## Changes

- Agent-first Skill 正确编排现有 CLI，没有新增远程服务或模型调用；
- 检查器只对 `skills/<name>/SKILL.md` 使用 Skill 元数据规则；
- `skills/*-workspace/` 作为被 Git 忽略的生成评测目录，不进入治理记录扫描；
- 用户文档明确 Skill 是推荐入口，CLI 是确定性执行层和手工备用入口。

## Blockers

Skill 尚未安装到用户全局 Codex Skill 目录；安装和仓库 commit 都需要单独明确授权。
既有 `strict-agent-guidance` linked worktree 仍包含 pytest 临时目录，与 TASK-016 无关。

## Next action

审阅 TASK-016 变更，并决定是否授权本地 commit；如需立即使用，再单独授权安装 Skill。
