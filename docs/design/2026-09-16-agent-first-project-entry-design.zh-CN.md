---
id: DES-004-ZH
type: design
status: accepted
created: 2026-09-16
updated: 2026-09-16
related:
  - REQ-003-ZH
  - ADR-0004
---

# Agent-first 项目启动入口设计

## 1. 设计结论

使用一个仓库内、可审查和可打包的 Codex Skill 作为自然语言入口。Skill 只编排现有
`pgk` CLI 和仓库治理流程，不复制 scaffold、adoption、migration 或 check 的实现，
也不调用模型提供商或远程 API。

```text
用户对话 → Codex Skill → pgk CLI → 项目治理文档与 Git 只读状态
```

## 2. 文件布局

```text
skills/project-governance-kit/
├── SKILL.md
└── evals/
    └── evals.json
```

`SKILL.md` 是运行时指令；`evals/evals.json` 保存可重复的行为验证场景。测试工作区和
打包产物属于本地生成物，不纳入权威治理记录。

Skill frontmatter 使用 Codex 支持的 `name`、`description` 等字段，不是 PGK 生命周期
frontmatter。`pgk check` 对精确路径 `skills/<name>/SKILL.md` 使用独立的 Skill 元数据
校验，并继续检查其中的 Markdown 链接；其他带 frontmatter 的 Markdown 不获得豁免。
`skills/*-workspace/` 是被 Git 忽略的生成评测目录，`pgk check` 不扫描其中的 fixture 和
输出，避免测试副本被误判为真实治理记录。检查器在目录遍历阶段剪枝 `.git`、worktree、
缓存和评测工作区，而不是遍历完成后再过滤，防止本地评测资产拖慢日常检查。

## 3. 状态分类

Skill 在任何写入前把目标分类为：

1. `governed`：存在 `.project-governance.toml` 和治理入口；读取并继续，不初始化；
2. `existing`：存在代码、文档或 Git 历史，但没有 PGK 配置；只读 adopt/doctor 后暂停；
3. `new`：空目录或用户明确指定的新目录；预览后初始化并创建 draft 需求；
4. `unclear`：路径、项目类型或写入目标不明确；提出一个最小澄清问题。

分类不能只依赖 Git 是否存在：空的已初始化 Git 仓库仍可属于新项目。

## 4. 命令编排

### 4.1 能力发现

优先运行 `pgk --help`；若命令未安装但当前仓库源码可用，可使用
`python -m project_governance --help`。两者均不可用时停止并报告安装步骤。

### 4.2 新项目

```text
pgk init --root <root> --project-name <name> --dry-run --json
pgk init --root <root> --project-name <name> [profile/collaboration/visibility]
pgk check --root <root> --json
pgk new requirement <next-id> <title> --root <root> --status draft --json
```

Agent 随后补充需求记录中的目标、范围、非范围、假设、问题和验收标准，但保持 `draft`。
如果没有 Git 仓库，只报告 `git_not_initialized`；执行 `git init` 仍需单独确认。

### 4.3 已有项目

```text
pgk adopt --root <root> --json
pgk doctor --root <root> --json
```

Agent 将结果翻译成简短接入提案，等待用户确认后才运行 supplement 或迁移流程。

### 4.4 已治理项目

按目标仓库 `AGENTS.md` 规定顺序读取入口、状态和关联记录；如果已有活动任务，先恢复
该任务，不创建重复记录。如果用户请求新功能，则按仓库规则创建新的需求或任务链。

## 5. 授权模型

- 用户明确要求“用 PGK 创建新项目”授权创建缺失治理文件和 draft 需求；
- 已有项目的 supplement、迁移批准和 apply 需要在展示方案后再次确认；
- Git init、commit、push、PR、merge、tag、release 和删除继续使用现有受保护动作规则；
- Skill 不把一个动作的授权扩展到另一个动作。

## 6. Skill 触发与输出

Skill 描述覆盖“创建/开始项目”“用 PGK 治理”“接入已有项目”“继续已治理项目”等自然
语言意图，同时排除纯咨询、工具比较和普通代码修改。每次运行的用户输出包含分类、
动作摘要、当前阶段、阻塞和唯一下一步。

## 7. 验证

第一轮至少包含三个真实场景：

- 空目录的新项目：应初始化、创建 draft REQ 并停在确认门；
- 有代码和文档的已有项目：应只读检查并停在接入方案确认；
- 已治理且有活动任务的项目：应恢复上下文，不重复初始化。

每个场景同时运行 with-skill 和 baseline，对是否正确分类、是否越权写入、是否遵守暂停点、
输出是否可恢复进行断言。用户先审核测试提示，再运行对照测试。

检查器单元测试覆盖合法 Skill frontmatter，以及缺少 description/目录名不匹配的错误。

## 8. 分发边界

仓库保存 Skill 源码和测试场景。打包或安装到用户级 Codex Skills 目录属于显式分发步骤，
不在创建源码时静默执行。OpenAI Skills API 是可选的远程分发机制，本设计不使用它。
