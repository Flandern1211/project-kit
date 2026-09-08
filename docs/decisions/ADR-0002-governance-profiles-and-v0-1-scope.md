---
id: ADR-0002
type: decision
status: accepted
created: 2026-09-07
updated: 2026-09-07
related:
  - REQ-001-ZH
  - DES-002-ZH
---

# ADR-0002 治理等级、协作模式与 v0.1 范围修订

## Purpose

记录 2026-09-07 讨论中对 Project Governance Kit 通用治理架构和 v0.1
范围的确认，作为旧版需求和设计中并行协作表述的修订依据。

## Scope

本决策适用于 Kit 的通用治理模型和 v0.1 基础实现，不引入业务项目规则。

## Acceptance

用户已确认以下决策：

- 治理等级分为 Lite、Standard、Strict；等级表示文档和检查深度，不表示
  是否支持某项运行或集成功能；
- Agent 协作模式与治理等级分离，分为 single-agent、sequential-agents 和
  parallel-agents；
- v0.1 只实现 single-agent 和 sequential-agents；并行 Agent、worktree
  协调、文件锁定和自动合并延期；
- GitHub/Issue、Web 后台、模型调用、自动 commit/push/PR/release 等属于
  后续可选扩展，不属于 v0.1 核心；
- Agent 可以提出治理等级或模块调整，但不能静默修改；治理变更须有提案、
  影响分析、用户确认和历史保留；
- 讨论阶段的内容不是权威依据，讨论收敛后才同步到正式需求、设计、状态和索引；
- 用户最新明确确认优先于较早确认，旧记录通过修订或 superseded 保留，不直接删除。

## Evidence

本 ADR 对应 2026-09-07 会话中用户对治理等级、协作模式、v0.1 延期范围和
文档沉淀流程的连续确认。具体同步由 TASK-006 完成。

## Changes

- REQ-001-ZH/REQ-001 增加治理等级和 v0.1 范围修订；
- DES-002-ZH/ DES-001 增加分层模型、协作模式分离和变更提案边界；
- STATUS、INDEX、BOARD 和 ACTIVITY 更新当前基线。

## Blockers

无。并行协作和外部集成仍明确延期，不阻塞 v0.1 文档治理基础。

## Next action

按 TASK-006 完成文档同步并运行 `pgk check`；后续实现变更须创建新的已接受任务。
