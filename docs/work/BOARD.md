<!-- PGK_GENERATED: board -->
# Work board

| ID | type | status | owner | related | branch/worktree | verification | blocker | next |
|---|---|---|---|---|---|---|---|---|
| ADR-0001 | decision | accepted | N/A | N/A | N/A / N/A | N/A | N/A | N/A |
| ADR-0002 | decision | accepted | N/A | REQ-001-ZH, DES-002-ZH | N/A / N/A | 本 ADR 对应 2026-09-07 会话中用户对治理等级、协作模式、v0.1 延期范围和 | 无。并行协作和外部集成仍明确延期，不阻塞 v0.1 文档治理基础。 | 按 TASK-006 完成文档同步并运行 `pgk check`；后续实现变更须创建新的已接受任务。 |
| ADR-0003 | decision | accepted | N/A | ADR-0002, TASK-009 | N/A / N/A | 用户在 2026-09-07 会话中确认：团队内部使用完整文档，其他人无法查看；Kit 自身不 | 无。实现和验证已由 TASK-010 完成；公开副本导出、仓库拆分、历史清理和远程权限修改仍属延期范围。 | 继续按 TASK-010、VER-002 和当前 `docs/STATUS.md` 维护已实现的可见性边界。 |
| DES-001 | design | draft | N/A | REQ-001 | N/A / N/A | N/A | N/A | N/A |
| DES-002-ZH | design | accepted | N/A | REQ-001-ZH, REQ-001 | N/A / N/A | N/A | N/A | N/A |
| DES-003-ZH | design | accepted | N/A | REQ-002-ZH, REQ-001-ZH | N/A / N/A | N/A | N/A | N/A |
| REQ-001 | requirement | accepted | N/A | REQ-001-ZH | N/A / N/A | N/A | N/A | N/A |
| REQ-001-ZH | requirement | accepted | N/A | REQ-001 | N/A / N/A | N/A | N/A | N/A |
| REQ-002-ZH | requirement | accepted | N/A | REQ-001-ZH, DES-003-ZH | N/A / N/A | N/A | N/A | N/A |
| TASK-000 | task | verified | root | REQ-001, DES-001 | codex/bootstrap-v0.1 / dirty | 20 tests passed; pgk check ok; document validator 0 errors | none | review and approve the first TouzhiAgent external trial |
| TASK-001 | task | verified | root | N/A | codex/bootstrap-v0.1 / dirty | 20 tests passed; pgk check ok; document validator 0 errors | none | review the usage guide and begin the TouzhiAgent trial |
| TASK-002 | task | verified | root | N/A | codex/bootstrap-v0.1 / dirty | pgk check ok; document validator 0 errors | none | review the Chinese requirements document |
| TASK-003 | task | verified | root | REQ-001-ZH | codex/TASK-003-v01-requirements / repository checkout | requirements review recorded | none | create the technical design revision |
| TASK-004 | task | verified | root | REQ-001-ZH, REQ-001 | codex/TASK-004-v01-design / repository checkout | technical design review recorded | none | implement the accepted design baseline |
| TASK-005 | task | verified | root | REQ-001-ZH, DES-002-ZH | codex/TASK-006-v01-baseline / repository checkout | 86 tests passed; compileall, diff-check, and document validation passed | protected Git/remote actions require user approval | review the v0.1 baseline and decide whether to authorize a commit |
| TASK-006 | task | verified | root | ADR-0002, REQ-001-ZH, DES-002-ZH | N/A / N/A | 已运行 `py -3 -c "import sys; from project_governance.cli import main; sys.exit(main(['check','--root','.','--json']))"`。 | 无。 | TASK-006 已验证；profile 运行时行为由后续 TASK-007 实现，并行协作仍属延期范围。 |
| TASK-007 | task | verified | root | ADR-0002, REQ-001-ZH, DES-002-ZH | task/TASK-007-governance-profiles / N/A | `py -3 -m pytest --basetemp D:\pgk-full-final -q`：92 passed。 | 无。并行 Agent 协作和自动治理等级评估属于延期范围。 | 验证完成；Lite/Standard/Strict 和 single/sequential 配置基础行为已实现。 |
| TASK-008 | task | verified | root | ADR-0002, TASK-007 | task/TASK-007-governance-profiles / repository checkout | 已检查中英文段落和命令示例；`git diff --check` 通过。 | 无。 | 任务已验证；README 的当前版本声明由 `pyproject.toml`、`.project-governance.toml` |
| TASK-009 | task | verified | root | ADR-0003, REQ-001-ZH | task/TASK-009-visibility-modes / repository checkout | 用户已审核并批准书面规格。 | 无。规格已获用户批准，实现由 TASK-010 完成。 | 规格已审核通过，TASK-010 已完成实现与验证。 |
| TASK-010 | task | verified | root | ADR-0003, REQ-001-ZH, DES-002-ZH | task/TASK-009-visibility-modes / repository checkout | 全量测试 101 passed；可见性专项测试 11 passed；compileall 和 `git diff --check` | 无。公开副本导出、仓库拆分、历史清理和远程权限修改属于延期范围。 | 实现和真实验证已完成；公开副本导出、仓库拆分、历史清理和远程权限修改另立任务。 |
| TASK-011 | task | verified | root | REQ-002-ZH, DES-003-ZH | task/TASK-006-v02-migration / C:/Users/31800/.codex/worktrees/bc83/project-kit | 120 tests passed; compileall and git diff --check passed; merged-result verification is recorded in VER-002 | none; protected Git and remote actions still require explicit user authorization | use a new task record for subsequent migration changes |
| TASK-012 | task | verified | root | REQ-002-ZH, DES-003-ZH, TASK-011 | task/TASK-012-migration-relative-links / D:/Project/project-kit/.worktrees/touzhi-link-fix | 120 项主项目测试和链接专项测试通过；真实 TouzhiAgent clone 迁移后 `pgk check` 不再报告原有相对链接断链。 | 无。当前只在独立 worktree 工作，不修改 TouzhiAgent。 | TASK-012 已合并到本地 `main` 的 8098a4c；push 仍需用户单独授权。 |
| TASK-014 | task | verified | root | REQ-001-ZH, DES-002-ZH, REQ-002-ZH, DES-003-ZH | task/TASK-014-document-consistency / D:/Project/project-kit/.worktrees/document-consistency | 已完成当前工作树验证：`py -3 -m pytest -o addopts="" --basetemp .pytest-tmp-task014-final6 -q`： | 无。 | 后续行为或当前状态文档变更须创建新的 TASK。 |
| VER-000 | verification | verified | root | TASK-000 | N/A / N/A | `py -3 -m pytest -o addopts='' -q` — 20 passed; | none | Use VER-001 for the current v0.1 baseline acceptance. |
| VER-001 | verification | verified | root | TASK-005, REQ-001-ZH, DES-002-ZH | N/A / N/A | `py -3 -m pytest -o addopts='' --basetemp D:\pgk-final-suite13 -ra` — full | The shared checkout is intentionally dirty until a user-authorized commit; | Review this baseline and decide whether to authorize a commit; remote |
| VER-002 | verification | verified | root | REQ-002-ZH, DES-003-ZH, TASK-011 | N/A / N/A | ```text | 无代码阻塞。验证记录中的 worktree 状态是当时的历史快照，当前状态以 `docs/STATUS.md` 和最新 Git 检查为准。 | 后续迁移变更使用新的 TASK，并重新生成迁移和验证证据。 |
| VER-003 | verification | verified | root | TASK-012, REQ-002-ZH, DES-003-ZH | N/A / N/A | 新增相对链接单元测试：已迁移目标、保留源文件目标和外部 URL； | 不存在的源链接仍保留并需要人工处理；Kit 不会猜测不存在的目标。 | TASK-012 已合并到本地 `main` 的 8098a4c；push 仍需用户单独授权。 |
