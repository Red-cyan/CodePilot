# CodePilot 开发规范

这份文档用于约束后续维护方式，重点是让项目在本地、CI 和 GitHub 上保持稳定可读。

## 提交原则

- Git 提交信息使用中文。
- 每次提交只覆盖一个清晰主题，例如“文档打磨”“测试修复”“工程配置”。
- 不提交 `.env`、本地索引数据、运行历史或私有仓库路径。
- 不为了展示效果临时跳过测试或静态检查。

## 编码和换行

项目通过 `.editorconfig` 和 `.gitattributes` 约束：

- 文本文件使用 UTF-8。
- 默认使用 LF 换行。
- 文件末尾保留一个换行。
- Markdown 文件允许保留行尾空格，避免破坏有意编写的换行格式。

如果 PowerShell 直接 `Get-Content` 中文出现乱码，优先用 `rg`、编辑器或 GitHub 页面确认内容；不要在未确认文件真实编码前批量重写文档。

## 本地验证

改动提交前至少运行：

```powershell
uv run ruff check .
uv run pyright
uv run pytest
docker compose config --quiet
```

如果只改 Markdown，可以不跑完整测试，但提交前仍建议至少检查：

```powershell
git diff --check
```

## GitHub 协作

仓库提供了 GitHub 模板：

- `.github/pull_request_template.md`：用于说明变更类型、验证结果、演示影响和安全检查。
- `.github/ISSUE_TEMPLATE/bug_report.md`：用于记录可复现 Bug。
- `.github/ISSUE_TEMPLATE/task.md`：用于记录文档、测试、工程配置等小范围质量改进。

提交 PR 前需要明确本次改动是否影响演示流程。如果影响接口、启动方式或鉴权方式，必须同步更新 README 或 `docs/`。

## 密钥处理

- `.env.example` 只保留空值或示例值。
- `.env` 不提交。
- `DEEPSEEK_API_KEY` 只放在本地环境或部署环境。
- `CODEPILOT_API_KEY` 用于保护写操作和 Agent 接口，不写进 README 的真实值。
- 诊断接口只能展示“是否配置”，不能返回密钥内容。

## 演示前流程

演示前先看：

- `docs/project-status.md`：确认当前能力和边界。
- `docs/demo-checklist.md`：按清单检查环境和接口顺序。
- `docs/interview-guide.md`：准备项目讲解和常见追问。

建议演示前保留一次完整验证输出：

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

## 不建议的改动方向

当前阶段不建议继续堆零散接口。更有价值的改动是：

- 修复真实 bug。
- 提升测试稳定性。
- 改善 README 和演示材料。
- 补齐 CI、配置、部署和安全边界。
- 对已有模块做小范围清理，但不要引入大规模重构。
