<!-- PGK_GENERATED: board -->
# Work board

| ID | type | status | owner | related | branch/worktree | verification | blocker | next |
|---|---|---|---|---|---|---|---|---|
| ADR-0001 | decision | accepted | N/A | N/A | N/A / N/A | N/A | N/A | N/A |
| ADR-0002 | decision | accepted | N/A | REQ-001-ZH, DES-002-ZH | N/A / N/A | 本 ADR 对应 2026-09-07 会话中用户对治理等级、协作模式、v0.1 延期范围和 | 无。并行协作和外部集成仍明确延期，不阻塞 v0.1 文档治理基础。 | 按 TASK-006 完成文档同步并运行 `pgk check`；后续实现变更须创建新的已接受任务。 |
| DES-001 | design | draft | N/A | REQ-001 | N/A / N/A | N/A | N/A | N/A |
| DES-002-ZH | design | accepted | N/A | REQ-001-ZH, REQ-001 | N/A / N/A | N/A | N/A | N/A |
| REQ-001 | requirement | accepted | N/A | REQ-001-ZH | N/A / N/A | N/A | N/A | N/A |
| REQ-001-ZH | requirement | accepted | N/A | REQ-001 | N/A / N/A | N/A | N/A | N/A |
| TASK-000 | task | verified | root | REQ-001, DES-001 | codex/bootstrap-v0.1 / dirty | 20 tests passed; pgk check ok; document validator 0 errors | none | review and approve the first TouzhiAgent external trial |
| TASK-001 | task | verified | root | N/A | codex/bootstrap-v0.1 / dirty | 20 tests passed; pgk check ok; document validator 0 errors | none | review the usage guide and begin the TouzhiAgent trial |
| TASK-002 | task | verified | root | N/A | codex/bootstrap-v0.1 / dirty | pgk check ok; document validator 0 errors | none | review the Chinese requirements document |
| TASK-003 | task | verified | root | REQ-001-ZH | codex/TASK-003-v01-requirements / repository checkout | requirements review recorded | none | create the technical design revision |
| TASK-004 | task | verified | root | REQ-001-ZH, REQ-001 | codex/TASK-004-v01-design / repository checkout | technical design review recorded | none | implement the accepted design baseline |
| TASK-005 | task | verified | root | REQ-001-ZH, DES-002-ZH | codex/TASK-006-v01-baseline / repository checkout | 86 tests passed; compileall, diff-check, and document validation passed | protected Git/remote actions require user approval | review the v0.1 baseline and decide whether to authorize a commit |
| TASK-006 | task | verified | root | ADR-0002, REQ-001-ZH, DES-002-ZH | N/A / N/A | 已运行 `py -3 -c "import sys; from project_governance.cli import main; sys.exit(main(['check','--root','.','--json']))"`。 | 无。 | 保持任务为 verified；后续如需实现 profile 运行时行为或并行协作，应创建新的任务。 |
| TASK-007 | task | verified | root | ADR-0002, REQ-001-ZH, DES-002-ZH | N/A / N/A | `py -3 -m pytest --basetemp D:\pgk-full-final -q`：92 passed。 | 无。并行 Agent 协作和自动治理等级评估属于延期范围。 | 验证完成；Lite/Standard/Strict 和 single/sequential 配置基础行为已实现。 |
| TASK-008 | task | verified | root | ADR-0002, TASK-007 | task/TASK-007-governance-profiles / repository checkout | bilingual README profile/mode usage synchronized; diff-check passed | none | commit and push documentation sync |
| TASK-009 | task | verified | root | ADR-0003 | task/TASK-009-visibility-modes / repository checkout | visibility specification approved and implemented by TASK-010 | none | review TASK-010 evidence |
| TASK-010 | task | verified | root | ADR-0003, REQ-001-ZH, DES-002-ZH | task/TASK-009-visibility-modes / repository checkout | 101 tests; real team-private/hybrid/public validation; compileall and diff-check passed | none | review implementation; create publication/export task if needed |
| TASK-011 | task | verified | root | REQ-002-ZH, DES-003-ZH | main / D:/Project/project-kit | 120 tests; compileall, diff-check and pgk check ok on 8d57cd7 | none; push remains user-controlled | review merge commit and decide whether to push main |
| VER-000 | verification | verified | root | TASK-000 | N/A / N/A | `py -3 -m pytest -o addopts='' -q` — 20 passed; | none | Use VER-001 for the current v0.1 baseline acceptance. |
| VER-001 | verification | verified | root | TASK-005, REQ-001-ZH, DES-002-ZH | N/A / N/A | `py -3 -m pytest -o addopts='' --basetemp D:\pgk-final-suite13 -ra` — full | The shared checkout is intentionally dirty until a user-authorized commit; | Review this baseline and decide whether to authorize a commit; remote |
