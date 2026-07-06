# CodePilot - AI Software Engineering Agent

## 1. 项目简介

CodePilot 是一个面向软件研发团队的 AI Software Engineering Agent。

项目目标不是实现一个普通聊天机器人，而是构建一个能够理解整个代码仓库、分析项目架构、定位 Bug、Review Pull Request、生成代码、生成文档以及回答开发问题的智能研发助手。

重点展示：

- LangChain 企业级开发
- Tool Calling
- Workflow
- RAG
- Repository Index
- 多阶段推理
- 工程化架构

---

# 2. 项目目标

打造一个真正可以辅助开发的软件工程 Agent。

支持：

- Repository Index
- Code Search
- Architecture Analysis
- Bug Analysis
- PR Review
- README Generator
- API Generator
- Unit Test Generator
- Code Explanation
- 技术问答

---

# 3. 技术栈

## Backend

Python 3.13

FastAPI

LangChain

LangSmith

Pydantic

SQLAlchemy

PostgreSQL

pgvector

Redis

Celery（可选）

Docker

---

## AI

DeepSeek-V4-Flash API

LangChain LCEL

PromptTemplate

Runnable

Retriever

Tool Calling

Memory

Output Parser

Embeddings

RAG

Conversation Memory

---

## Code Parsing

GitPython

Tree-sitter

AST Parser

DirectoryLoader

RecursiveCharacterTextSplitter

---

## Frontend

Next.js

React

TypeScript

TailwindCSS

Monaco Editor

Shadcn UI

---

# 4. 系统架构

User

↓

Next.js Frontend

↓

FastAPI API

↓

LangChain Workflow

↓

Planner

↓

Task Router

↓

Retriever

↓

Tool Executor

↓

LLM

↓

Response Builder

↓

Frontend

---

# 5. 核心模块

## Repository Loader

功能：

导入 Github Repository

支持：

- Local Repository
- Git Clone
- Branch

输出：

Repository Metadata

---

## Repository Parser

扫描：

Python

Java

Go

C++

JavaScript

TypeScript

解析：

- Classes
- Functions
- Imports
- Dependencies

---

## Vector Index

建立：

Repository Embedding

支持：

- Chroma

或

- pgvector

---

## Code Retriever

实现：

语义检索

文件检索

Symbol 检索

Class 检索

Function 检索

---

## Project Analyzer

分析：

项目结构

模块关系

架构模式

输出：

Architecture Report

---

## Bug Analyzer

输入：

错误日志

Stack Trace

功能：

定位：

相关代码

可能原因

修复建议

---

## PR Review Agent

输入：

Git Diff

输出：

Bug

Style

Security

Performance

Maintainability

评分

---

## README Generator

自动生成：

README

安装

部署

API

项目结构

License

---

## API Generator

根据需求：

生成：

Controller

Service

Repository

Schema

Test

---

## Unit Test Generator

支持：

pytest

自动生成：

Test Case

Mock

Assertions

---

# 6. LangChain Workflow

Question

↓

Intent Detection

↓

Task Planner

↓

Retriever

↓

Tool Calling

↓

Context Builder

↓

LLM

↓

Output Parser

↓

Response

---

# 7. Tool 列表

Repository Tool

Git Tool

Filesystem Tool

Search Tool

Symbol Search Tool

Diff Tool

Terminal Tool（受限）

Markdown Tool

Architecture Tool

Embedding Tool

---

# 8. Prompt 设计

包括：

System Prompt

Planner Prompt

Reviewer Prompt

Generator Prompt

Bug Analyzer Prompt

Architecture Prompt

---

# 9. 数据库设计

repositories

documents

embeddings

chat_sessions

messages

tool_logs

analysis_reports

review_reports

---

# 10. API

POST /repository/import

POST /repository/index

POST /chat

POST /review

POST /analyze

POST /generate/readme

POST /generate/api

POST /generate/test

GET /repository/list

GET /analysis/{id}

---

# 11. 前端页面

Dashboard

Repository Manager

Chat

Architecture

Code Viewer

Review Result

README Preview

Tool Logs

Settings

---

# 12. 项目亮点

- LangChain LCEL Workflow
- 多 Tool Calling
- RAG + Repository Index
- Tree-sitter 代码解析
- Git 仓库理解
- PR 自动 Review
- Bug 智能分析
- README 自动生成
- API 自动生成
- Unit Test 自动生成
- Monaco 在线代码查看
- Docker 一键部署

---

# 13. 开发阶段

## Phase 1
项目初始化、仓库导入、代码解析。

## Phase 2
向量索引、代码检索、RAG 问答。

## Phase 3
Bug 分析、架构分析、README 生成。

## Phase 4
PR Review、API 生成、单元测试生成。

## Phase 5
前端完善、Docker 化、性能优化。

---

# 14. 最终成果

实现一个具备企业级工程实践的 AI Software Engineering Agent，可作为秋招 AI Agent / 大模型应用开发岗位的核心项目展示，突出 LangChain、Tool Calling、Workflow、RAG 与代码理解能力。