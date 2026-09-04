<!-- PGK_GENERATED: board -->
# Work board

| ID | type | status | owner | related | branch/worktree | verification | blocker | next |
|---|---|---|---|---|---|---|---|---|
| ADR-0001 | decision | accepted | N/A | N/A | N/A / N/A | N/A | N/A | N/A |
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
| VER-000 | verification | verified | root | TASK-000 | N/A / N/A | `py -3 -m pytest -o addopts='' -q` — 20 passed; | none | Use VER-001 for the current v0.1 baseline acceptance. |
| VER-001 | verification | verified | root | TASK-005, REQ-001-ZH, DES-002-ZH | N/A / N/A | `py -3 -m pytest -o addopts='' --basetemp D:\pgk-final-suite7 -ra` — full | The shared checkout is intentionally dirty until a user-authorized commit; | Review this baseline and decide whether to authorize a commit; remote |
