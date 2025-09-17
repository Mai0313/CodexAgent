<center>

# CodexAgent — GitHub/Gitea AI 程序协作 Agent

[![PyPI version](https://img.shields.io/pypi/v/CodexAgent.svg)](https://pypi.org/project/CodexAgent/)
[![python](https://img.shields.io/badge/-Python_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/CodexAgent/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/CodexAgent/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/CodexAgent/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/CodexAgent/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/CodexAgent/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/CodexAgent/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/CodexAgent.svg)](https://github.com/Mai0313/CodexAgent/graphs/contributors)

</center>

用一句提及，就能让 AI 帮你在 GitHub/Gitea 上自动改码、提交、并建立 PR。CodexAgent 监听 Issues/PR 的留言中对 `@{settings.app_slug}` 的提及，将任务交给 Claude Code 完成，并支持在 PR 讨论中持续迭代。

[English](README.md) | [繁体中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## ✨ 核心特色（支持 GitHub / Gitea）

- **提及触发**：在 Issue 或 PR 对话中 `@{settings.app_slug} <任务>` 即可触发 AI 协助
- **自动化开发流程**：自动 clone、建立分支、AI 改码、commit 变更
- **PR 内续作**：在同一个 PR 中再次 `@{settings.app_slug}` 可要求持续修改，结果会 push 到同一分支
- **生成 PR 内容**：在 PR 文字中输入 `@{settings.app_slug} generate commit message`，会分析改动并更新 PR 内容
- **安全与审计**：以 GitHub App 权限与 Webhook Secret 验证事件；所有更动以分支/PR 形式可审核

> 注：以下描述的是完整功能设计。实作现况请见文末「目前进度与 Roadmap」。

## 🧠 它如何运作

当用户在目标 repo 的 Issue 或 PR 留言中提到 `@{settings.app_slug}` 时，CodexAgent 会按以下流程执行：

### 🔄 完整工作流程

1. **接收与验证事件**

    - 通过 FastAPI Webhook 接收 GitHub/Gitea 的 `issue_comment` 事件
    - 检查留言内容是否包含 `@{settings.app_slug}` 提及
    - 验证事件签名（GitHub `X-Hub-Signature-256` / Gitea Secret）

2. **解析任务上下文**

    - 取得存储库 clone URL、Issue/PR 信息、留言作者与内容
    - 判断是「新任务」或「延续同一 PR 的任务」
    - 提取用户指定的具体任务内容

3. **准备工作区**

    - **新任务**：`git clone <repo>` 到 `./workspaces/<repo_name>`，建立新分支 `codex-agent/<短uuid>`
    - **续作任务**：切换到现有 PR 对应的分支（`head`），pull 最新变更

4. **AI 执行任务（Claude Code）**

    - 载入系统提示模板（`./prompts/system_prompt.md`）与任务模板（`./prompts/template.md`）
    - 在工作区中执行 Claude Code，具备完整的 shell/git/文件系统操作权限
    - 优先以最小必要修改达成目标，自动执行格式化/测试（如项目有设置）

5. **提交与建立/更新 PR**

    - **新任务**：生成语义化的 commit message，建立新 PR 对默认分支
    - **续作任务**：将新 commit push 至现有分支，在 PR 中回报进度
    - PR 描述包含改动摘要、影响范围与测试建议

6. **持续迭代协作**

    - 在 PR 讨论中再次 `@{settings.app_slug} <新指令>` 可持续修改同一 PR
    - 使用 `@{settings.app_slug} generate commit message` 可重新分析改动并更新 PR 描述

## 💬 互动指南（留言语法）

### 📝 新任务（Issue 或 PR 中首次提及）

在任何 Issue 或 PR 留言中提及 `@{settings.app_slug}` 并描述任务：

```
@{settings.app_slug} 修复 tests/test_*.py 的失败案例
```

```
@{settings.app_slug} 实作 README 中的安装章节与示例代码
```

```
@{settings.app_slug} 重构 src/utils.py 中的重复代码，提取共用函数
```

**触发效果**：AI 会自动 clone 项目到 `./workspaces/<repo_name>`，建立新分支，完成任务后建立 PR

### 🔄 续作任务（在现有 PR 中再次留言）

在已由 CodexAgent 建立的 PR 中再次提及，可要求持续修改：

```
@{settings.app_slug} 调整变更范围，只修改 src/core/ 与 tests/ 目录
```

```
@{settings.app_slug} 增加类型注解并修正 mypy 报告的错误
```

```
@{settings.app_slug} 根据 code review 建议重构 database 连接逻辑
```

**触发效果**：AI 会切换到 PR 对应的分支，执行新任务后 push 到同一分支

### 📄 生成 PR 内容

在 PR 描述或留言中使用特殊指令：

```
@{settings.app_slug} generate commit message
```

**触发效果**：分析所有文件变更，自动生成结构化的 PR 描述，包含：

- 改动摘要与影响范围
- 测试建议与注意事项
- 变更清单与相关 Issue 链接

## 🔗 支持事件与平台

- GitHub

    - 事件：`issue_comment`（PR 对话也属此事件）
    - 权限（最低建议）：Contents: Read/Write、Pull requests: Read/Write、Issues: Read、Metadata: Read
    - Webhook：`POST https://<your-host>/github/webhook`

- Gitea

    - 事件：Issue/PR 留言（相当于 `issue_comment`）
    - Webhook：`POST https://<your-host>/gitea/webhook`

## ⚙️ 安装与部署

本机开发（uv）：

```bash
make uv-install
uv sync
uv run codex_agent   # 启动 FastAPI（uvicorn）在 0.0.0.0:8000
```

Docker（Compose）：

```bash
docker compose up -d app
```

设置公开可回调的 URL（如 ngrok/Cloudflare Tunnel），将 `https://<your-host>/github/webhook` 或 `.../gitea/webhook` 设为 Webhook 目标。

## 🔑 环境变量

将下列变量放入 `.env` 或部署平台的环境设置中：

- `GITHUB_APP_SLUG`：你的 GitHub App slug（留言提及用，对应 `settings.app_slug`）
- `GITHUB_APP_WEBHOOK_SECRET`：Webhook Secret（GitHub 验签用）
- `GITHUB_APP_ID`：GitHub App ID
- `GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET`：OAuth 用（可支持安装/授权流程）
- `GITHUB_PRIVATE_KEY_PATH`：GitHub App 私钥路径（PEM，默认 `./configs/app.pem`）
- （选用）`CONTEXT7_API_KEY`：Claude Code MCP 外挂示例所需的 API Key

私钥请放在 `./configs/app.pem`，并确保不外泄。

## 🧭 Webhook 与权限设置（GitHub）

1. 建立 GitHub App（建议安装到目标组织/个人）

    - Webhook URL：`https://<your-host>/github/webhook`
    - Webhook Secret：自定一组并填入环境变量
    - 事件订阅：至少 `Issue comment`
    - 权限：Contents(R/W)、Pull requests(R/W)、Issues(R)、Metadata(R)

2. 下载私钥（PEM）并放置于 `GITHUB_PRIVATE_KEY_PATH`

3. 安装 App 至目标 Repository 或 Organization

4. 进阶（选用）

    - OAuth 回调：`GET /github/auth?code=<code>&state=<state>`（示范流程）
    - 取得 Installation Token：`GET /github/token/{installation_id}`（示范用途）

## 🧩 API 一览

- `GET /`：健康检查（返回消息）
- `POST /github/webhook`：GitHub Webhook 入口
- `POST /gitea/webhook`：Gitea Webhook 入口
- `GET /github/auth`：GitHub OAuth 回调示范
- `GET /github/token/{installation_id}`：交换 Installation Token 示范

## 📁 项目结构（节选）

```
src/codex_agent/
  app/api.py                 # FastAPI app 与路由挂载
  app/v1/github.py           # GitHub Webhook + 授权/Token 范例
  app/v1/gitea.py            # Gitea Webhook
  utils/claude_code.py       # Claude Code 执行与 workspace 准备
  utils/settings.py          # 读取 GitHub App 设置
  utils/gen_jwt.py           # 生成 GitHub App JWT
  types/                     # Webhook/Headers Pydantic 类型
prompts/                     # 系统提示与任务模板
```

工作目录默认：`./workspaces/<repo_name>`（第一次触发会自动 `git clone`）。

## 📌 目前进度与 Roadmap

### ✅ 已完成（可用功能）

- **Webhook 接收与解析**：GitHub/Gitea `issue_comment` 事件接收与基本验证
- **提及检测**：检测留言中的 `@{settings.app_slug}` 标记
- **工作区管理**：自动 `git clone` 到 `./workspaces/<repo_name>`
- **Claude Code 整合**：系统提示载入、任务模板注入、工作目录执行
- **基础设置管理**：通过 `Settings` 类别载入环境变量
- **GitHub App 认证**：JWT 生成、Installation Token 取得、OAuth 流程

### 🚧 进行中（部分实现）

- **任务执行流程**：Claude Code 被触发但尚未实际执行（`claude.task` 目前只是 print）
- **分支管理**：工作区 clone 完成，但分支建立与切换逻辑待实现
- **错误处理**：基本的 webhook 验证，但详细的错误回馈机制待加强

### 📋 待完善（设计已定，将逐步补齐）

- **自动 PR 建立/更新**：完成任务后自动建立 PR 或更新现有 PR
- **PR 内续作支持**：检测是否为续作任务，切换到正确分支继续工作
- **Webhook 签名验证**：完整的 GitHub/Gitea webhook 安全验证
- **Commit message 生成**：自动分析变更内容并生成语义化提交消息
- **PR 描述生成**：`generate commit message` 功能实现
- **测试与格式化整合**：自动执行项目的 lint/test 命令
- **多 AI 模型支持**：除 Claude Code 外支持其他 AI 编程助手
- **审计与日志**：完整的操作记录与权限管理

## 🤝 贡献

- 欢迎提交 Issue/PR
- 请遵循程序风格（ruff、类型）与语义化提交
- PR 标题建议采用 Conventional Commits

## 📄 授权

MIT — 详见 `LICENSE`。
