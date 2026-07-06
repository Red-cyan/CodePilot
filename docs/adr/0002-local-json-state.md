# ADR 0002：MVP 阶段使用本地 JSON 持久化状态

## 状态

已采纳

## 背景

CodePilot 需要持久化仓库元数据、索引结果和 Agent 运行历史。项目已经在配置和 Docker Compose 中预留 PostgreSQL、pgvector 和 Redis，但当前阶段的重点是保证后端 MVP 快速可演示、可测试、易理解。

如果过早引入完整数据库模型、迁移和异步任务，会增加演示和本地启动成本，也会让项目主线从 Agent 闭环转向基础设施搭建。

## 决策

MVP 阶段使用本地 JSON 文件保存状态：

- `storage/repositories.json` 保存仓库元数据、chunk、符号和检索向量。
- `storage/runs.json` 保存 Agent 运行历史。
- `storage/` 被 `.gitignore` 排除，避免提交本地路径和私有索引数据。
- Docker Compose 中 API 容器使用 volume 保存运行状态。

## 后果

优点：

- 本地启动简单，不强依赖数据库。
- 测试可以直接验证持久化和恢复逻辑。
- 数据结构直观，便于面试时解释状态流转。

代价：

- 不适合大规模仓库和并发写入。
- 缺少数据库查询、事务和索引能力。
- pgvector 还只是生产化预留，尚未承载核心检索状态。

## 后续演进

后续生产化方向是把 repository、chunk、symbol、run 迁移到 PostgreSQL，并将向量写入 pgvector；Redis 可用于索引任务队列、缓存或异步任务状态。
