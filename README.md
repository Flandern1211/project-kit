# Project Governance Kit

中文 | [English](README.en.md)

Project Governance Kit（`pgk`）是一套面向 Agent、同时方便人阅读的项目治理工具包。
它帮助项目沉淀需求、设计、任务、Bug、验收、Git 状态和跨会话交接信息。

工具包与项目的编程语言、框架、Issue 平台和模型提供商无关。它生成普通的
Markdown/TOML 文件，并提供离线检查能力。

## v0.1 范围

- 初始化或检查项目治理结构；
- 创建需求、设计、决策、任务、Bug 和验收记录；
- 检查文档元数据、ID、状态和本地链接；
- 输出适合人和 Agent 使用的文本或 JSON；
- 读取 Git 分支、提交和工作区状态；
- 更新任务的跨会话交接区。

GitHub Issue 和 Pull Request 作为讨论、评审和合并入口；仓库 Markdown 是长期记录的权威来源。

## 开发

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python -m project_governance --help
```

常用命令：

```text
pgk init       初始化缺失的治理文件
pgk adopt      只读分析已有项目
pgk doctor     检查项目治理状态
pgk check      检查文档、链接和状态
pgk new        创建治理记录
pgk index      更新工作索引
pgk handoff    更新任务交接信息
```

## 当前状态

当前版本为预发布版本 `0.1.0.dev0`。工具包仓库自身使用这套治理架构进行开发和验证，
TouzhiAgent 是第一个外部试验项目。

## 文档

- [项目文档索引](docs/INDEX.md)
- [v0.1 需求](docs/requirements/2026-09-02-project-governance-kit-v0.1-requirements.md)
- [v0.1 设计](docs/design/2026-09-02-project-governance-kit-v0.1-design.md)
- [验收记录](docs/verification/VER-000-bootstrap.md)
