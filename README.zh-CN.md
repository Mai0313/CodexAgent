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

用一句提及，就能让 AI 帮你在 GitHub/Gitea 上自动改码、提交、并建立 PR。CodexAgent 监听 Issues/PR 的留言中对 `@{GITHUB_APP_SLUG}` 的提及，将任务交给 Claude Code / OpenAI Codex 完成，并支持在 PR 讨论中持续迭代。

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## ✨ 核心特色（支持 GitHub / Gitea）

- **提及触发**：在 Issue 或 PR 对话中 `@{GITHUB_APP_SLUG} <任务>` 即可触发
- **自动化开发流程**：clone、建立/切换分支、AI 改码、测试、commit、建立/更新 PR
- **PR 内续作**：在同一个 PR 中再次 `@{GITHUB_APP_SLUG}` 可要求持续修改，结果会 push 到同一分支
- **生成 PR 内容**：在 PR 文字中输入 `@{GITHUB_APP_SLUG} generate commit message`，会分析改动并更新 PR 内容
- **安全与审计**：以 GitHub App 权限与 Webhook Secret 验证事件；所有更动以分支/PR 形式可审核

> 注：以下描述的是完整功能设计。实现现况请见文末「目前进度与 Roadmap」。

## 🧠 它如何运作

当用户在目标 repo 的 Issue 或 PR 留言中提到 `@{GITHUB_APP_SLUG}` 时，CodexAgent 会按以下流程执行：

1. **接收事件**
   - 通过 FastAPI Webhook 接收 GitHub/Gitea 的 `issue_comment` 事件
   - 验证签名（GitHub `X-Hub-Signature-256` / Gitea Secret）与事件类型

2. **解析上下文**
   - 获取仓库 URL、Issue/PR 信息、留言作者与内容
   - 判断是「新任务」或「延续同一 PR 的任务」

3. **准备工作区**
   - 若为新任务：`git clone <repo>` 到 `./workspaces/<repo_name>`，建立分支 `codex-agent/<短uuid>`
   - 若为续作：切换到 PR 对应的分支（`head`），更新到最新

4. **AI 改码（Claude Code / OpenAI Codex）**
   - 注入系统提示与任务模板（`./prompts/*.md`），提供完整工作目录
   - 以工具模式执行（允许 shell/git/fs 操作），在工作区内完成开发工作
   - 优先以最小必要修改达成目标，并尝试执行格式化/测试（如有）

5. **提交与建立/更新 PR**
   - 生成语义化的 commit message，推送到远程分支
   - 新任务：对预设分支建立 PR，并在 PR 描述附上摘要与影响
   - 续作：将新的 commit push 至同一分支，于 PR 留言回报进度

6. **与用户迭代**
   - 在 PR 讨论中再次 `@{GITHUB_APP_SLUG} <新的指令>` 可持续修改同一 PR
   - 使用 `@{GITHUB_APP_SLUG} generate commit message` 可重写 PR 原始内容（描述/清单）

## 💬 交互指南（留言语法）

- **新任务（Issue 或 PR）**
  - `@{GITHUB_APP_SLUG} 修复 tests/test_*.py 的失败案例`
  - `@{GITHUB_APP_SLUG} 实现 README 中的安装章节与范例`

- **续作（在现有 PR 中再次留言）**
  - `@{GITHUB_APP_SLUG} 调整变更范围，只修改 abc/ 与 tests/`
  - `@{GITHUB_APP_SLUG} 增加类型注释并修正 mypy 报告`

- **生成 PR 内容**
  - `@{GITHUB_APP_SLUG} generate commit message`
  - 会根据文件差异生成条理化说明、影响范围、测试建议，并更新 PR 描述

## 🔗 支持事件与平台

- **GitHub**
  - 事件：`issue_comment`（PR 对话也属此事件）
  - 权限（最低建议）：Contents: Read/Write、Pull requests: Read/Write、Issues: Read、Metadata: Read
  - Webhook：`POST https://<your-host>/github/webhook`

- **Gitea**
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

设定公开可回调的 URL（如 ngrok/Cloudflare Tunnel），将 `https://<your-host>/github/webhook` 或 `.../gitea/webhook` 设为 Webhook 目标。

## 🔑 环境变量

将下列变量放入 `.env` 或部署平台的环境设定中：

- `GITHUB_APP_SLUG`：你的 GitHub App slug（留言提及用）
- `GITHUB_APP_WEBHOOK_SECRET`：Webhook Secret（GitHub 验签用）
- `GITHUB_APP_ID`：GitHub App ID
- `GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET`：OAuth 用（可支持安装/授权流程）
- `GITHUB_PRIVATE_KEY_PATH`：GitHub App 私钥路径（PEM，默认 `./configs/app.pem`）
- （选用）`CONTEXT7_API_KEY`：Claude Code MCP 插件示例所需的 API Key

私钥请放在 `./configs/app.pem`，并确保不外泄。

## 🧭 Webhook 与权限设置（GitHub）

1. **创建 GitHub App**（建议安装到目标组织/个人）
   - Webhook URL：`https://<your-host>/github/webhook`
   - Webhook Secret：自定一组并填入环境变量
   - 事件订阅：至少 `Issue comment`
   - 权限：Contents(R/W)、Pull requests(R/W)、Issues(R)、Metadata(R)

2. **下载私钥（PEM）**并放置于 `GITHUB_PRIVATE_KEY_PATH`

3. **安装 App** 至目标 Repository 或 Organization

4. **进阶（选用）**
   - OAuth 回调：`GET /github/auth?code=<code>&state=<state>`（示范流程）
   - 获取 Installation Token：`GET /github/token/{installation_id}`（示范用途）

## 🧩 API 一览

- `GET /`：健康检查（返回讦息）
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
  utils/settings.py          # 读取 GitHub App 设定
  utils/gen_jwt.py           # 生成 GitHub App JWT
  types/                     # Webhook/Headers Pydantic 型别
prompts/                     # 系统提示与任务模板
```

工作目录默认：`./workspaces/<repo_name>`（第一次触发会自动 `git clone`）。

## 📌 目前进度与 Roadmap

**已完成（可用）：**

- GitHub/Gitea Webhook 入口与事件解析（`issue_comment`）
- 提及检测：`@{GITHUB_APP_SLUG}`
- 工作区创建与 repo clone（`./workspaces/<repo>`）
- Claude Code 执行框架（系统提示/模板注入、工具模式、工作目录）
- GitHub OAuth/Installation Token 示例端点

**待完善（设计已定，将逐步补齐）：**

- GitHub/Gitea 签名验证与错误处理强化
- 自动创建/更新 PR、分支命名策略与保护规则整合
- PR 内「续作」全流程（checkout、冲突处理、状态回复）
- commit message/PR 描述自动生成与覆写
- 内建测试/格式化自动执行与回报
- 多模型供应商选择（Claude Code / OpenAI Codex 等）与密钥管理
- 更完整的权限/审计日志

## 🤝 贡献

- 欢迎提交 Issue/PR
- 请遵循编程风格（ruff、类型）与语义化提交
- 建议 PR 标题采用 Conventional Commits

## 📄 授权

MIT — 详见 `LICENSE`。
