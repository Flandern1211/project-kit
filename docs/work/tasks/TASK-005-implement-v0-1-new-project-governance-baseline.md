---
id: TASK-005
type: task
status: verified
created: 2026-09-04
updated: 2026-09-04
related:
  - REQ-001-ZH
  - DES-002-ZH
---
# Implement v0.1 new-project governance baseline

## Purpose

实现已确认的 v0.1 新项目初始化和文档驱动 Agent 开发基础，使新项目从第一天起
具备可追踪文档节点、Git 协同记录和用户授权门禁。

## Scope

- 按 DES-002-ZH 完善初始化文件树和占位视图；
- 增加 REVIEW 记录类型和模板；
- 增加项目阶段、看板、流程图和活动记录；
- 扩展检查器验证索引、关键字段、Git 状态和文件范围；
- 保持核心 CLI 不执行受保护 Git/远程操作；
- 通过空项目 fixture 和 Kit 自身验证。

## Acceptance

- 新项目初始化生成 requirements、design、decisions、work、reviews、verification、activity 和 operations 骨架；
- 生成的 AGENTS.md 明确 Agent 读取顺序、需求/设计门禁、交接和授权规则；
- REQ/DES/ADR/TASK/BUG/REVIEW/VER 记录可以创建并建立关联；
- STATUS、BOARD、WORKFLOW、INDEX、ACTIVITY 满足设计中的最小合同；
- 检查器能报告缺失索引、断链、非法状态、重复 ID、未登记文件范围和 Git 脏状态；
- 没有用户授权时，Kit 不执行 commit、push、Issue/PR、merge、tag、release 或删除；
- 测试和验证证据回写到本任务和 VER 记录。

## Evidence

Task 6 fixture acceptance and the baseline validation are recorded in
[VER-001](../../verification/VER-001-v0-1-new-project-baseline.md): the full
pytest suite, compileall, and diff check passed. The fixture created and
indexed all seven record types and TASK/BUG handoffs while preserving an
existing file and generating no business REQ. The shared checkout remains
dirty until a user-authorized commit, so its live `pgk check` reports that
expected state.

## Changes

已修改 `src/project_governance/records.py`、`src/project_governance/scaffold.py`、
`src/project_governance/checks.py` 及内置 Review 模板生成；Task 6 增加 fixture
acceptance tests、VER-001 和用户文档。实施计划见
`docs/superpowers/plans/2026-09-04-project-governance-kit-v0.1-baseline-implementation.md`。

## Blockers

无；真实外部 Agent、部署、性能、模型提供商和远程 API 仍未验收，受保护
Git/远程动作不在本任务授权范围内。

## Next action

保持 TASK-005 为 verified；后续范围须通过新的已接受任务进入。

## Owner

root

## Files

- `src/project_governance/`;
- `tests/`;
- `docs/verification/VER-001-v0-1-new-project-baseline.md`.

## Git

branch: codex/TASK-006-v01-baseline
worktree: repository checkout
base_commit: b086911
head_commit: working tree

## Handoff

<!-- PGK_HANDOFF_START -->
Status: verified
Branch: codex/TASK-006-v01-baseline
HEAD: working tree
Worktree: repository checkout
Dirty: true
Uncommitted: present
Verification: 86 tests passed; compileall, diff-check, and document validation passed
Blockers: protected Git/remote actions require user approval
Next action: review the v0.1 baseline and decide whether to authorize a commit
<!-- PGK_HANDOFF_END -->
