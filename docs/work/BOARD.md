<!-- PGK_GENERATED: board -->
# Work board

| ID | type | status | owner | related | branch/worktree | verification | blocker | next |
|---|---|---|---|---|---|---|---|---|
| ADR-0001 | decision | accepted | N/A | N/A | N/A / N/A | N/A | N/A | N/A |
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
| TASK-006 | task | verified | root | REQ-002-ZH, DES-003-ZH | task/TASK-006-v02-migration / C:/Users/31800/.codex/worktrees/bc83/project-kit | 120 tests passed; compileall and git diff --check passed; worktree-local pgk check has only shared-worktree dirty/unregistered-branch findings | shared Git worktree state requires maintainer review; protected Git and remote actions still require explicit user authorization | review the complete diff and authorize any specific Git action |
| VER-000 | verification | verified | root | TASK-000 | N/A / N/A | `py -3 -m pytest -o addopts='' -q` — 20 passed; | none | Use VER-001 for the current v0.1 baseline acceptance. |
| VER-001 | verification | verified | root | TASK-005, REQ-001-ZH, DES-002-ZH | N/A / N/A | `py -3 -m pytest -o addopts='' --basetemp D:\pgk-final-suite13 -ra` — full | The shared checkout is intentionally dirty until a user-authorized commit; | Review this baseline and decide whether to authorize a commit; remote |
| VER-002 | verification | verified | root | REQ-002-ZH, DES-003-ZH, TASK-006 | N/A / N/A | ```text | 无代码阻塞。共享 Git 工作区的脏状态和其他未登记分支需要仓库维护者在合并前按其所属任务处理。 | 审查本分支完整 diff；获得明确授权后再决定是否 commit、push 或创建 PR。 |
