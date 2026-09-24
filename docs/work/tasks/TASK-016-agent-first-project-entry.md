---
id: TASK-016
type: task
status: verified
created: 2026-09-16
updated: 2026-09-17
related:
  - REQ-003-ZH
  - DES-004-ZH
  - ADR-0004
---

# TASK-016 实现 Agent-first 项目启动入口

## Purpose

提供一个 Codex Skill，让用户通过自然语言驱动现有 PGK 新项目初始化、已有项目接入预检
和已治理项目恢复流程。

## Owner

root

## Scope

- 新增仓库内 `project-governance-kit` Skill；
- 覆盖 new、existing、governed 三类项目和 unclear/非触发边界；
- 创建并由用户审核行为测试提示；
- 运行 with-skill/baseline 对照验证并根据反馈迭代；
- 同步 README、usage、STATUS、索引和验证证据；
- 不自动安装、不调用远程 API、不实现新的 CLI 业务逻辑。

## Files

- `skills/project-governance-kit/SKILL.md`
- `skills/project-governance-kit/evals/evals.json`
- `skills/project-governance-kit/agents/openai.yaml`
- `src/project_governance/checks.py`
- `tests/test_governance_checks.py`
- `docs/requirements/2026-09-16-agent-first-project-entry-requirements.zh-CN.md`
- `docs/design/2026-09-16-agent-first-project-entry-design.zh-CN.md`
- `docs/decisions/ADR-0004-roadmap-scope.md`
- `docs/STATUS.md`
- `README.md`
- `README.en.md`
- `docs/usage.md`
- 相关索引、活动和验证记录

## Acceptance

- Skill 只编排现有 PGK 能力并遵守目标仓库指令；
- `pgk check` 独立验证 Skill 元数据，不把 Skill 当作生命周期记录；
- 新项目停在需求确认门；已有项目停在接入方案确认门；
- 已治理项目不重复初始化；
- 受保护 Git/远程动作不被隐式授权；
- 测试提示经用户审核，对照验证完成并有证据。

## Evidence

- 用户已确认 `evals/evals.json` 中的三类测试提示；
- 第一轮对照评测：with-skill 15/15 断言通过，without-skill 12/15，通过率分别为
  100% 和 80%，delta `+0.20`；
- 新项目基线提前创建 TASK-001，Skill 正确停在 draft REQ-001；
- 已有项目基线未运行 doctor 并改用 supplement dry-run，Skill 正确执行 adopt/doctor；
- 已治理项目两组均 5/5，该场景验证安全恢复但当前区分度不足；
- 每个场景/配置只有一次运行，未采集可用 timing/token/tool-call 数据，不能据此判断方差
  或性能开销；
- `compileall` 和 Skill checker smoke test 通过；`pgk check` 除当前变更和既有 linked
  worktree 外无语义问题；
- 本地审阅页面：`skills/project-governance-kit-workspace/iteration-1/review.html`。
- 用户已审核并批准 iteration-1 结果；
- Codex 官方 `quick_validate.py`：Skill valid；
- Python 3.14 全量测试：`164 passed in 52.75s`；检查器专项测试：`31 passed in 16.69s`；
- 正式证据见 VER-004。
- 用户评测审核与代码/文档审查见 REVIEW-001。
- 2026-09-17 用户明确授权安装用户级 Skill 并执行本地 commit；
- 用户级 Skill 已安装到 `%USERPROFILE%\.codex\skills\project-governance-kit`，安装副本通过
  Codex 官方快速校验；
- 本次提交为最终任务提交，提交后按仓库规则只运行只读 clean-tree 检查。

## Changes

- 已建立 REQ-003-ZH 和 DES-004-ZH；
- 已创建 Skill 草案和评测场景；
- 已增加 Skill frontmatter 的窄范围检查与单元测试。
- 已完成第一轮 with-skill/baseline 执行、独立评分、聚合和静态审阅页面生成。
- 已生成 `agents/openai.yaml`，同步中英文 README、usage、CHANGELOG 和 VER-004。
- 已将 Markdown 枚举改为目录级剪枝，避免被忽略的 Skill workspace 拖慢 `pgk check`。
- 已记录 REVIEW-001，结论为通过且无实现 blocker。

## Blockers

无。既有 `strict-agent-guidance` linked worktree 中的 pytest 临时目录不属于本任务；
建议后续单独清理或由该任务所有者处理。

## Next action

任务已完成并提交；后续只规划的两个扩展需分别建立新的需求、设计和任务。

## Git

branch: codex/task-016-agent-first-entry
worktree: D:/Project/project-kit
base_commit: f4d81c9d57299b5ef5008986d4c9bcc8cd330540
head_commit: c80d82a
