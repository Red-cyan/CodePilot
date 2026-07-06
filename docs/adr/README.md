# 架构决策记录

ADR 用于记录 CodePilot 中重要技术取舍，帮助面试和后续维护时解释“为什么这样设计”。

## 决策列表

- [ADR 0001：采用离线优先的 Agent 运行策略](0001-offline-first-agent.md)
- [ADR 0002：MVP 阶段使用本地 JSON 持久化状态](0002-local-json-state.md)
- [ADR 0003：采用可选 API Key 保护写操作和 Agent 接口](0003-optional-api-key.md)

## 使用方式

面试讲解时可以把 ADR 作为“技术取舍证据”：

- 为什么没有强依赖真实模型。
- 为什么当前阶段没有直接把状态全部放进 PostgreSQL。
- 为什么鉴权是可选 API Key，而不是完整账号体系。

后续如果新增重大设计，例如异步索引、pgvector 迁移、前端工作台或 Tree-sitter 解析，也应该补充新的 ADR。
