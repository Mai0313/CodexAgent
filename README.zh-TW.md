<center>

# CodexAgent — GitHub/Gitea AI 程式協作 Agent

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

用一句提及，就能讓 AI 幫你在 GitHub/Gitea 上自動改碼、提交、並建立 PR。CodexAgent 監聽 Issues/PR 的留言中對 `@{settings.app_slug}` 的提及，將任務交給 Claude Code 完成，並支援在 PR 討論中持續迭代。

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## ✨ 核心特色（支援 GitHub / Gitea）

- **提及觸發**：在 Issue 或 PR 對話中 `@{settings.app_slug} <任務>` 即可觸發 AI 協助
- **自動化開發流程**：自動 clone、建立分支、AI 改碼、commit 變更
- **PR 內續作**：在同一個 PR 中再次 `@{settings.app_slug}` 可要求持續修改，結果會 push 到同一分支
- **產生 PR 內容**：在 PR 文字中輸入 `@{settings.app_slug} generate commit message`，會分析改動並更新 PR 內容
- **安全與審計**：以 GitHub App 權限與 Webhook Secret 驗證事件；所有更動以分支/PR 形式可審核

> 註：以下描述的是完整功能設計。實作現況請見文末「目前進度與 Roadmap」。

## 🧠 它如何運作

當使用者在目標 repo 的 Issue 或 PR 留言中提到 `@{settings.app_slug}` 時，CodexAgent 會按以下流程執行：

### 🔄 完整工作流程

1. **接收與驗證事件**

    - 透過 FastAPI Webhook 接收 GitHub/Gitea 的 `issue_comment` 事件
    - 檢查留言內容是否包含 `@{settings.app_slug}` 提及
    - 驗證事件簽章（GitHub `X-Hub-Signature-256` / Gitea Secret）

2. **解析任務上下文**

    - 取得儲存庫 clone URL、Issue/PR 資訊、留言作者與內容
    - 判斷是「新任務」或「延續同一 PR 的任務」
    - 提取使用者指定的具體任務內容

3. **準備工作區**

    - **新任務**：`git clone <repo>` 到 `./workspaces/<repo_name>`，建立新分支 `codex-agent/<短uuid>`
    - **續作任務**：切換到現有 PR 對應的分支（`head`），pull 最新變更

4. **AI 執行任務（Claude Code）**

    - 載入系統提示模板（`./prompts/system_prompt.md`）與任務模板（`./prompts/template.md`）
    - 在工作區中執行 Claude Code，具備完整的 shell/git/檔案系統操作權限
    - 優先以最小必要修改達成目標，自動執行格式化/測試（如專案有設定）

5. **提交與建立/更新 PR**

    - **新任務**：產生語義化的 commit message，建立新 PR 對預設分支
    - **續作任務**：將新 commit push 至現有分支，在 PR 中回報進度
    - PR 描述包含改動摘要、影響範圍與測試建議

6. **持續迭代協作**

    - 在 PR 討論中再次 `@{settings.app_slug} <新指令>` 可持續修改同一 PR
    - 使用 `@{settings.app_slug} generate commit message` 可重新分析改動並更新 PR 描述

## 💬 互動指南（留言語法）

### 📝 新任務（Issue 或 PR 中首次提及）

在任何 Issue 或 PR 留言中提及 `@{settings.app_slug}` 並描述任務：

```
@{settings.app_slug} 修復 tests/test_*.py 的失敗案例
```

```
@{settings.app_slug} 實作 README 中的安裝章節與範例代碼
```

```
@{settings.app_slug} 重構 src/utils.py 中的重複代碼，提取共用函數
```

**觸發效果**：AI 會自動 clone 專案到 `./workspaces/<repo_name>`，建立新分支，完成任務後建立 PR

### 🔄 續作任務（在現有 PR 中再次留言）

在已由 CodexAgent 建立的 PR 中再次提及，可要求持續修改：

```
@{settings.app_slug} 調整變更範圍，只修改 src/core/ 與 tests/ 目錄
```

```
@{settings.app_slug} 增加型別註解並修正 mypy 報告的錯誤
```

```
@{settings.app_slug} 根據 code review 建議重構 database 連接邏輯
```

**觸發效果**：AI 會切換到 PR 對應的分支，執行新任務後 push 到同一分支

### 📄 產生 PR 內容

在 PR 描述或留言中使用特殊指令：

```
@{settings.app_slug} generate commit message
```

**觸發效果**：分析所有檔案變更，自動生成結構化的 PR 描述，包含：

- 改動摘要與影響範圍
- 測試建議與注意事項
- 變更清單與相關 Issue 連結

## 🔗 支援事件與平台

- GitHub

    - 事件：`issue_comment`（PR 對話也屬此事件）
    - 權限（最低建議）：Contents: Read/Write、Pull requests: Read/Write、Issues: Read、Metadata: Read
    - Webhook：`POST https://<your-host>/github/webhook`

- Gitea

    - 事件：Issue/PR 留言（相當於 `issue_comment`）
    - Webhook：`POST https://<your-host>/gitea/webhook`

## ⚙️ 安裝與部署

本機開發（uv）：

```bash
make uv-install
uv sync
uv run codex_agent   # 啟動 FastAPI（uvicorn）在 0.0.0.0:8000
```

Docker（Compose）：

```bash
docker compose up -d app
```

設定公開可回呼的 URL（如 ngrok/Cloudflare Tunnel），將 `https://<your-host>/github/webhook` 或 `.../gitea/webhook` 設為 Webhook 目標。

## 🔑 環境變數

將下列變數放入 `.env` 或部署平台的環境設定中：

- `GITHUB_APP_SLUG`：你的 GitHub App slug（留言提及用，對應 `settings.app_slug`）
- `GITHUB_APP_WEBHOOK_SECRET`：Webhook Secret（GitHub 驗簽用）
- `GITHUB_APP_ID`：GitHub App ID
- `GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET`：OAuth 用（可支援安裝/授權流程）
- `GITHUB_PRIVATE_KEY_PATH`：GitHub App 私鑰路徑（PEM，預設 `./configs/app.pem`）
- （選用）`CONTEXT7_API_KEY`：Claude Code MCP 外掛示例所需的 API Key

私鑰請放在 `./configs/app.pem`，並確保不外洩。

## 🧭 Webhook 與權限設定（GitHub）

1. 建立 GitHub App（建議安裝到目標組織/個人）

    - Webhook URL：`https://<your-host>/github/webhook`
    - Webhook Secret：自訂一組並填入環境變數
    - 事件訂閱：至少 `Issue comment`
    - 權限：Contents(R/W)、Pull requests(R/W)、Issues(R)、Metadata(R)

2. 下載私鑰（PEM）並放置於 `GITHUB_PRIVATE_KEY_PATH`

3. 安裝 App 至目標 Repository 或 Organization

4. 進階（選用）

    - OAuth 回呼：`GET /github/auth?code=<code>&state=<state>`（示範流程）
    - 取得 Installation Token：`GET /github/token/{installation_id}`（示範用途）

## 🧩 API 一覽

- `GET /`：健康檢查（返回訊息）
- `POST /github/webhook`：GitHub Webhook 入口
- `POST /gitea/webhook`：Gitea Webhook 入口
- `GET /github/auth`：GitHub OAuth 回呼示範
- `GET /github/token/{installation_id}`：交換 Installation Token 示範

## 📁 專案結構（節選）

```
src/codex_agent/
  app/api.py                 # FastAPI app 與路由掛載
  app/v1/github.py           # GitHub Webhook + 授權/Token 範例
  app/v1/gitea.py            # Gitea Webhook
  utils/claude_code.py       # Claude Code 執行與 workspace 準備
  utils/settings.py          # 讀取 GitHub App 設定
  utils/gen_jwt.py           # 產生 GitHub App JWT
  types/                     # Webhook/Headers Pydantic 型別
prompts/                     # 系統提示與任務模板
```

工作目錄預設：`./workspaces/<repo_name>`（第一次觸發會自動 `git clone`）。

## 📌 目前進度與 Roadmap

### ✅ 已完成（可用功能）

- **Webhook 接收與解析**：GitHub/Gitea `issue_comment` 事件接收與基本驗證
- **提及偵測**：檢測留言中的 `@{settings.app_slug}` 標記
- **工作區管理**：自動 `git clone` 到 `./workspaces/<repo_name>`
- **Claude Code 整合**：系統提示載入、任務模板注入、工作目錄執行
- **基礎設定管理**：透過 `Settings` 類別載入環境變數
- **GitHub App 認證**：JWT 生成、Installation Token 取得、OAuth 流程

### 🚧 進行中（部分實現）

- **任務執行流程**：Claude Code 被觸發但尚未實際執行（`claude.task` 目前只是 print）
- **分支管理**：工作區 clone 完成，但分支建立與切換邏輯待實現
- **錯誤處理**：基本的 webhook 驗證，但詳細的錯誤回饋機制待加強

### 📋 待完善（設計已定，將逐步補齊）

- **自動 PR 建立/更新**：完成任務後自動建立 PR 或更新現有 PR
- **PR 內續作支援**：檢測是否為續作任務，切換到正確分支繼續工作
- **Webhook 簽章驗證**：完整的 GitHub/Gitea webhook 安全驗證
- **Commit message 生成**：自動分析變更內容並生成語義化提交訊息
- **PR 描述生成**：`generate commit message` 功能實現
- **測試與格式化整合**：自動執行專案的 lint/test 命令
- **多 AI 模型支援**：除 Claude Code 外支援其他 AI 編程助手
- **審計與日誌**：完整的操作記錄與權限管理

## 🤝 貢獻

- 歡迎提交 Issue/PR
- 請遵循程式風格（ruff、型別）與語義化提交
- PR 標題建議採用 Conventional Commits

## 📄 授權

MIT — 詳見 `LICENSE`。
