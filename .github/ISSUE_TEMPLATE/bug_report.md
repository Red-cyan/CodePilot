---
name: Bug 报告
about: 记录 CodePilot 的可复现问题
title: "Bug："
labels: bug
assignees: ""
---

## 问题描述

请简要说明出现了什么问题。

## 复现步骤

1. 启动服务：
2. 调用接口：
3. 输入参数：
4. 实际结果：

## 期望结果

请说明你期望系统返回什么结果。

## 环境信息

- 启动方式：本地 uvicorn / Docker Compose
- Python 版本：
- 是否配置 `DEEPSEEK_API_KEY`：
- 是否配置 `CODEPILOT_API_KEY`：

## 日志和响应

请粘贴关键响应、错误日志或 `X-Request-Id`。

## 已尝试的检查

- [ ] `uv run ruff check .`
- [ ] `uv run pyright`
- [ ] `uv run pytest`
- [ ] `docker compose config --quiet`
