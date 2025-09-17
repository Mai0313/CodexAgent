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

用一句提及，就能讓 AI 幫你在 GitHub/Gitea 上自動改碼、提交、並建立 PR。CodexAgent 監聽 Issues/PR 的留言中對 `@{GITHUB_APP_SLUG}` 的提及，將任務交給 Claude Code / OpenAI Codex 完成，並支援在 PR 討論中持續迭代。

其他語言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## ✨ 核心特色（支援 GitHub / Gitea）

- 提及觸發：在 Issue 或 PR 對話中 `@{GITHUB_APP_SLUG} <任務>` 即可觸發
- 自動化開發流程：clone、建立/切換分支、AI 改碼、測試、commit、建立/更新 PR
- PR 內續作：在同一個 PR 中再次 `@{GITHUB_APP_SLUG}` 可要求持續修改，結果會 push 到同一分支
- 產生 PR 內容：在 PR 文字中輸入 `@{GITHUB_APP_SLUG} generate commit message`，會分析改動並更新 PR 內容
- 安全與審計：以 GitHub App 權限與 Webhook Secret 驗證事件；所有更動以分支/PR 形式可審核

> 註：以下描述的是完整功能設計。實作現況請見文末「目前進度與 Roadmap」。

## 🧠 它如何運作

當使用者在目標 repo 的 Issue 或 PR 留言中提到 `@{GITHUB_APP_SLUG}` 時，CodexAgent 會按以下流程執行：

1. 接收事件

    - 透過 FastAPI Webhook 接收 GitHub/Gitea 的 `issue_comment` 事件
    - 驗證簽章（GitHub `X-Hub-Signature-256` / Gitea Secret）與事件類型

2. 解析上下文

    - 取得儲存庫 URL、Issue/PR 資訊、留言作者與內容
    - 判斷是「新任務」或「延續同一 PR 的任務」

3. 準備工作區

    - 若為新任務：`git clone <repo>` 到 `./workspaces/<repo_name>`，建立分支 `codex-agent/<短uuid>`
    - 若為續作：切換到 PR 對應的分支（`head`），更新到最新

4. AI 改碼（Claude Code / OpenAI Codex）

    - 注入系統提示與任務模板（`./prompts/*.md`），提供完整工作目錄
    - 以工具模式執行（允許 shell/git/fs 操作），在工作區內完成開發工作
    - 優先以最小必要修改達成目標，並嘗試執行格式化/測試（如有）

5. 提交與建立/更新 PR

    - 產生語義化的 commit message，推送到遠端分支
    - 新任務：對預設分支建立 PR，並在 PR 描述附上摘要與影響
    - 續作：將新的 commit push 至同一分支，於 PR 留言回報進度

6. 與使用者迭代

    - 在 PR 討論中再次 `@{GITHUB_APP_SLUG} <新的指令>` 可持續修改同一 PR
    - 使用 `@{GITHUB_APP_SLUG} generate commit message` 可重寫 PR 原始內容（描述/清單）

## 💬 互動指南（留言語法）

- 新任務（Issue 或 PR）

    - `@{GITHUB_APP_SLUG} 修復 tests/test_*.py 的失敗案例`
    - `@{GITHUB_APP_SLUG} 實作 README 中的安裝章節與範例`

- 續作（在現有 PR 中再次留言）

    - `@{GITHUB_APP_SLUG} 調整變更範圍，只修改 abc/ 與 tests/`
    - `@{GITHUB_APP_SLUG} 增加型別註解並修正 mypy 報告`

- 產生 PR 內容

    - `@{GITHUB_APP_SLUG} generate commit message`
    - 會根據檔案差異生成條理化說明、影響範圍、測試建議，並更新 PR 描述

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

- `GITHUB_APP_SLUG`：你的 GitHub App slug（留言提及用）
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

已完成（可用）：

- GitHub/Gitea Webhook 入口與事件解析（`issue_comment`）
- 提及偵測：`@{GITHUB_APP_SLUG}`
- 工作區建立與 repo clone（`./workspaces/<repo>`）
- Claude Code 執行骨架（系統提示/模板注入、工具模式、工作目錄）
- GitHub OAuth/Installation Token 範例端點

待完善（設計已定，將逐步補齊）：

- GitHub/Gitea 簽章驗證與錯誤處理強化
- 自動建立/更新 PR、分支命名策略與保護規則整合
- PR 內「續作」全流程（checkout、衝突處理、狀態回覆）
- commit message/PR 描述自動生成與覆寫
- 內建測試/格式化自動執行與回報
- 多模型供應商選擇（Claude Code / OpenAI Codex 等）與金鑰管理
- 更完整的權限/審計日誌

## 🤝 貢獻

- 歡迎提交 Issue/PR
- 請遵循程式風格（ruff、型別）與語義化提交
- PR 標題建議採用 Conventional Commits

## 📄 授權

MIT — 詳見 `LICENSE`。
