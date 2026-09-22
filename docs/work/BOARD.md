<!-- PGK_GENERATED: board -->
# Work board

| ID | type | status | owner | related | branch/worktree | verification | blocker | next |
|---|---|---|---|---|---|---|---|---|
| ADR-0001 | decision | accepted | N/A | N/A | N/A / N/A | N/A | N/A | N/A |
| ADR-0002 | decision | accepted | N/A | REQ-001-ZH, DES-002-ZH | N/A / N/A | 本 ADR 对应 2026-09-07 会话中用户对治理等级、协作模式、v0.1 延期范围和 | 无。未来路线图已由 ADR-0004 收口；本记录中的原延期表述保留为 2026-09-07 的历史决策。 | 按 ADR-0004 执行：只有并行 Agent/worktree 安全和受授权本地自动 commit 保留为后续扩展。 |
| ADR-0003 | decision | accepted | N/A | ADR-0002, TASK-009 | N/A / N/A | 用户在 2026-09-07 会话中确认：团队内部使用完整文档，其他人无法查看；Kit 自身不 | 无。实现和验证已由 TASK-010 完成；ADR-0004 已将公开副本自动导出、仓库拆分、 | 继续维护已实现的可见性边界；公开内容由用户审查和发布，不新增自动导出能力。 |
| ADR-0004 | decision | accepted | N/A | ADR-0002, ADR-0003, REQ-001-ZH, DES-002-ZH | N/A / N/A | 2026-09-16 用户在现状与路线图讨论后确认：“这两个作为后续的功能扩展，剩下都可以 | 无。两个后续扩展尚未进入设计或实现，开始前仍需分别建立被接受的需求、设计和任务。 | 保持当前实现稳定；只有用户决定启动其中一个扩展时，才创建对应需求和设计记录。 |
| DES-001 | design | draft | N/A | REQ-001 | N/A / N/A | N/A | N/A | N/A |
| DES-002-ZH | design | accepted | N/A | REQ-001-ZH, REQ-001 | N/A / N/A | N/A | N/A | N/A |
| DES-003-ZH | design | accepted | N/A | REQ-002-ZH, REQ-001-ZH | N/A / N/A | N/A | N/A | N/A |
| DES-004-ZH | design | accepted | N/A | REQ-003-ZH, ADR-0004 | N/A / N/A | N/A | N/A | N/A |
| REQ-001 | requirement | accepted | N/A | REQ-001-ZH | N/A / N/A | N/A | N/A | N/A |
| REQ-001-ZH | requirement | accepted | N/A | REQ-001 | N/A / N/A | N/A | N/A | N/A |
| REQ-002-ZH | requirement | accepted | N/A | REQ-001-ZH, DES-003-ZH | N/A / N/A | N/A | N/A | N/A |
| REQ-003-ZH | requirement | accepted | N/A | ADR-0004 | N/A / N/A | N/A | N/A | N/A |
| REVIEW-001 | review | verified | root；行为输出由用户审核。 | TASK-016, REQ-003-ZH, DES-004-ZH, VER-004 | N/A / N/A | iteration-1：with-skill 15/15，without-skill 12/15； | 无实现 blocker。commit 和用户级安装尚未授权。 | 用户决定是否授权本地 commit，以及是否将 Skill 安装到当前 Codex 用户目录。 |
| REVIEW-002 | review | verified | Codex | TASK-019 | N/A / N/A | AC-1: Inspected generated AGENTS.md and scaffold closure rules. | None. | Review is complete; await the repository commit decision. |
| TASK-000 | task | verified | root | REQ-001, DES-001 | codex/bootstrap-v0.1 / dirty | 20 tests passed; pgk check ok; document validator 0 errors | none | review and approve the first TouzhiAgent external trial |
| TASK-001 | task | verified | root | N/A | codex/bootstrap-v0.1 / dirty | 20 tests passed; pgk check ok; document validator 0 errors | none | review the usage guide and begin the TouzhiAgent trial |
| TASK-002 | task | verified | root | N/A | codex/bootstrap-v0.1 / dirty | pgk check ok; document validator 0 errors | none | review the Chinese requirements document |
| TASK-003 | task | verified | root | REQ-001-ZH | codex/TASK-003-v01-requirements / repository checkout | requirements review recorded | none | create the technical design revision |
| TASK-004 | task | verified | root | REQ-001-ZH, REQ-001 | codex/TASK-004-v01-design / repository checkout | technical design review recorded | none | implement the accepted design baseline |
| TASK-005 | task | verified | root | REQ-001-ZH, DES-002-ZH | codex/TASK-006-v01-baseline / repository checkout | 86 tests passed; compileall, diff-check, and document validation passed | protected Git/remote actions require user approval | review the v0.1 baseline and decide whether to authorize a commit |
| TASK-006 | task | verified | root | ADR-0002, REQ-001-ZH, DES-002-ZH | N/A / N/A | 已运行 `py -3 -c "import sys; from project_governance.cli import main; sys.exit(main(['check','--root','.','--json']))"`。 | 无。 | TASK-006 已验证；profile 运行时行为由 TASK-007 实现。未来范围现由 ADR-0004 管理， |
| TASK-007 | task | verified | root | ADR-0002, REQ-001-ZH, DES-002-ZH | task/TASK-007-governance-profiles / N/A | `py -3 -m pytest --basetemp D:\pgk-full-final -q`：92 passed。 | 无。ADR-0004 保留并行 Agent/worktree 安全为后续扩展，并将自动治理等级评估改为非目标。 | 验证完成；Lite/Standard/Strict 和 single/sequential 配置基础行为已实现。未来路线图 |
| TASK-008 | task | verified | root | ADR-0002, TASK-007 | task/TASK-007-governance-profiles / repository checkout | 已检查中英文段落和命令示例；`git diff --check` 通过。 | 无。 | 任务已验证；README 的当前版本声明由 `pyproject.toml`、`.project-governance.toml` |
| TASK-009 | task | verified | root | ADR-0003, REQ-001-ZH | task/TASK-009-visibility-modes / repository checkout | 用户已审核并批准书面规格。 | 无。规格已获用户批准，实现由 TASK-010 完成。 | 规格已审核通过，TASK-010 已完成实现与验证。 |
| TASK-010 | task | verified | root | ADR-0003, REQ-001-ZH, DES-002-ZH | task/TASK-009-visibility-modes / repository checkout | 全量测试 101 passed；可见性专项测试 11 passed；compileall 和 `git diff --check` | 无。ADR-0004 已将公开副本自动导出、仓库拆分、历史清理和远程权限修改改为非目标。 | 实现和真实验证已完成；继续维护现有可见性模式，不为上述非目标另立实现任务。 |
| TASK-011 | task | verified | root | REQ-002-ZH, DES-003-ZH | task/TASK-006-v02-migration / C:/Users/31800/.codex/worktrees/bc83/project-kit | 120 tests passed; compileall and git diff --check passed; merged-result verification is recorded in VER-002 | none; protected Git and remote actions still require explicit user authorization | use a new task record for subsequent migration changes |
| TASK-012 | task | verified | root | REQ-002-ZH, DES-003-ZH, TASK-011 | task/TASK-012-migration-relative-links / D:/Project/project-kit/.worktrees/touzhi-link-fix | 120 项主项目测试和链接专项测试通过；真实 TouzhiAgent clone 迁移后 `pgk check` 不再报告原有相对链接断链。 | 无。当前只在独立 worktree 工作，不修改 TouzhiAgent。 | TASK-012 已合并到本地 `main` 的 8098a4c；push 仍需用户单独授权。 |
| TASK-014 | task | verified | root | REQ-001-ZH, DES-002-ZH, REQ-002-ZH, DES-003-ZH | task/TASK-014-document-consistency / D:/Project/project-kit/.worktrees/document-consistency | 已完成当前工作树验证：`py -3 -m pytest -o addopts="" --basetemp .pytest-tmp-task014-final6 -q`： | 无。 | 后续行为或当前状态文档变更须创建新的 TASK。 |
| TASK-015 | task | verified | root | ADR-0004, REQ-001-ZH, DES-002-ZH | codex/task-015-roadmap-scope / D:/Project/project-kit | `pgk index --root . --json`：成功重建决策、任务、工作板和其他生成索引； | 无。项目级 `pgk check` 仍会独立报告既有 `strict-agent-guidance` worktree 中的 pytest | 任务已验证；后续实现两个扩展中的任一项时创建新的需求、设计和任务。 |
| TASK-016 | task | verified | root | REQ-003-ZH, DES-004-ZH, ADR-0004 | codex/task-016-agent-first-entry / D:/Project/project-kit | 用户已确认 `evals/evals.json` 中的三类测试提示； | 无。既有 `strict-agent-guidance` linked worktree 中的 pytest 临时目录不属于本任务； | 任务已完成并提交；后续只规划的两个扩展需分别建立新的需求、设计和任务。 |
| TASK-017 | task | verified | root | REQ-003-ZH, DES-004-ZH, TASK-016 | codex/task-017-skill-five-elements / D:/Project/project-kit | 仓库和已安装 Skill 均通过 Codex 官方快速校验； | 无。 | TASK-017 已完成；GitHub 发布由新的 TASK-018 跟踪。 |
| TASK-018 | task | verified | root | TASK-017, VER-005 | codex/task-018-publish-skill / D:/Project/project-kit | GitHub 登录账号：`Flandern1211`；目标仓库：`Flandern1211/skills`；base：`main`； | 无发布 blocker。PR 仍待用户审查和决定是否合并。 | 审查 PR #1；合并属于独立远程动作，尚未执行。 |
| TASK-019 | task | verified | Codex | REQ-001-ZH, DES-002-ZH | codex/task-019-terminal-gates / C:/Users/31800/.codex/worktrees/task-019-terminal-gates/project-kit | VER-006 completed all eight acceptance checks. | None. | Review the AC-8 evidence and decide whether to authorize the repository commit. |
| VER-000 | verification | verified | root | TASK-000 | N/A / N/A | `py -3 -m pytest -o addopts='' -q` — 20 passed; | none | Use VER-001 for the current v0.1 baseline acceptance. |
| VER-001 | verification | verified | root | TASK-005, REQ-001-ZH, DES-002-ZH | N/A / N/A | `py -3 -m pytest -o addopts='' --basetemp D:\pgk-final-suite13 -ra` — full | The shared checkout is intentionally dirty until a user-authorized commit; | Review this baseline and decide whether to authorize a commit; remote |
| VER-002 | verification | verified | root | REQ-002-ZH, DES-003-ZH, TASK-011 | N/A / N/A | ```text | 无代码阻塞。验证记录中的 worktree 状态是当时的历史快照，当前状态以 `docs/STATUS.md` 和最新 Git 检查为准。 | 后续迁移变更使用新的 TASK，并重新生成迁移和验证证据。 |
| VER-003 | verification | verified | root | TASK-012, REQ-002-ZH, DES-003-ZH | N/A / N/A | 新增相对链接单元测试：已迁移目标、保留源文件目标和外部 URL； | 不存在的源链接仍保留并需要人工处理；Kit 不会猜测不存在的目标。 | TASK-012 已合并到本地 `main` 的 8098a4c；push 仍需用户单独授权。 |
| VER-004 | verification | verified | root | TASK-016, REQ-003-ZH, DES-004-ZH | N/A / N/A | 用户审核并批准三条 iteration-1 评测提示和静态评测结果； | Skill 尚未安装到用户全局 Codex Skill 目录；安装和仓库 commit 都需要单独明确授权。 | 审阅 TASK-016 变更，并决定是否授权本地 commit；如需立即使用，再单独授权安装 Skill。 |
| VER-005 | verification | verified | root | TASK-017, REQ-003-ZH, DES-004-ZH | N/A / N/A | 运行时 `SKILL.md` 明确包含“触发场景、输入、流程、输出、验收标准”五个中文一级章节； | 无。 | TASK-017 已验证；GitHub 发布使用独立任务记录。 |
| VER-006 | verification | verified | Codex | TASK-019 | N/A / N/A | AC-1: `AGENTS.md`, generated scaffold text, and Skill guidance inspected; generated guidance states the closure protocol. | None. | Verification complete; the remaining protected action is the repository commit decision. |
