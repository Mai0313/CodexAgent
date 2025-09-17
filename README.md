<center>

# CodexAgent — GitHub/Gitea AI Programming Collaboration Agent

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

Just mention once, and let AI automatically code, commit, and create PRs for you on GitHub/Gitea. CodexAgent listens for `@{settings.app_slug}` mentions in Issues/PR comments, delegates tasks to Claude Code, and supports continuous iteration within PR discussions.

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## ✨ Core Features (GitHub / Gitea Support)

- **Mention Trigger**: Simply `@{settings.app_slug} <task>` in Issue or PR comments to trigger AI assistance
- **Automated Development Workflow**: Auto clone, create branches, AI coding, commit changes
- **PR Continuation**: Re-mention `@{settings.app_slug}` in the same PR for continuous modifications, results push to the same branch
- **Generate PR Content**: Use `@{settings.app_slug} generate commit message` in PR text to analyze changes and update PR content
- **Security & Audit**: Event verification via GitHub App permissions and Webhook Secret; all changes reviewable through branches/PRs

> Note: The following describes the complete functional design. For current implementation status, see "Current Progress & Roadmap" at the end.

## 🧠 How It Works

When users mention `@{settings.app_slug}` in Issue or PR comments in the target repo, CodexAgent executes the following workflow:

### 🔄 Complete Workflow

1. **Receive & Verify Events**

    - Receive GitHub/Gitea `issue_comment` events via FastAPI Webhook
    - Check if comment content contains `@{settings.app_slug}` mention
    - Verify event signatures (GitHub `X-Hub-Signature-256` / Gitea Secret)

2. **Parse Task Context**

    - Get repository clone URL, Issue/PR info, comment author and content
    - Determine if it's a "new task" or "continuation of the same PR task"
    - Extract specific task content specified by the user

3. **Prepare Workspace**

    - **New Task**: `git clone <repo>` to `./workspaces/<repo_name>`, create new branch `codex-agent/<short-uuid>`
    - **Continuation Task**: Switch to existing PR's corresponding branch (`head`), pull latest changes

4. **AI Task Execution (Claude Code)**

    - Load system prompt template (`./prompts/system_prompt.md`) and task template (`./prompts/template.md`)
    - Execute Claude Code in workspace with full shell/git/filesystem operation permissions
    - Prioritize minimal necessary changes to achieve goals, auto-execute formatting/testing (if project configured)

5. **Commit & Create/Update PR**

    - **New Task**: Generate semantic commit message, create new PR against default branch
    - **Continuation Task**: Push new commits to existing branch, report progress in PR
    - PR description includes change summary, impact scope, and testing recommendations

6. **Continuous Iterative Collaboration**

    - Re-mention `@{settings.app_slug} <new-command>` in PR discussions for continuous modifications to the same PR
    - Use `@{settings.app_slug} generate commit message` to re-analyze changes and update PR description

## 💬 Interaction Guide (Comment Syntax)

### 📝 New Tasks (First Mention in Issue or PR)

Mention `@{settings.app_slug}` in any Issue or PR comment and describe the task:

```
@{settings.app_slug} Fix failing test cases in tests/test_*.py
```

```
@{settings.app_slug} Implement installation section and example code in README
```

```
@{settings.app_slug} Refactor duplicate code in src/utils.py, extract common functions
```

**Trigger Effect**: AI will automatically clone the project to `./workspaces/<repo_name>`, create a new branch, complete the task, and create a PR

### 🔄 Continuation Tasks (Re-mention in Existing PR)

Re-mention in PRs already created by CodexAgent to request continuous modifications:

```
@{settings.app_slug} Adjust change scope, only modify src/core/ and tests/ directories
```

```
@{settings.app_slug} Add type annotations and fix mypy reported errors
```

```
@{settings.app_slug} Refactor database connection logic based on code review suggestions
```

**Trigger Effect**: AI will switch to the PR's corresponding branch, execute new tasks, and push to the same branch

### 📄 Generate PR Content

Use special commands in PR description or comments:

```
@{settings.app_slug} generate commit message
```

**Trigger Effect**: Analyze all file changes and automatically generate structured PR description, including:

- Change summary and impact scope
- Testing recommendations and considerations
- Change list and related Issue links

## 🔗 Supported Events & Platforms

- GitHub

    - Events: `issue_comment` (PR conversations also belong to this event)
    - Permissions (minimum recommended): Contents: Read/Write, Pull requests: Read/Write, Issues: Read, Metadata: Read
    - Webhook: `POST https://<your-host>/github/webhook`

- Gitea

    - Events: Issue/PR comments (equivalent to `issue_comment`)
    - Webhook: `POST https://<your-host>/gitea/webhook`

## ⚙️ Installation & Deployment

Local development (uv):

```bash
make uv-install
uv sync
uv run codex_agent   # Start FastAPI (uvicorn) on 0.0.0.0:8000
```

Docker (Compose):

```bash
docker compose up -d app
```

Configure a publicly accessible callback URL (like ngrok/Cloudflare Tunnel), set `https://<your-host>/github/webhook` or `.../gitea/webhook` as the Webhook target.

## 🔑 Environment Variables

Place the following variables in `.env` or your deployment platform's environment settings:

- `GITHUB_APP_SLUG`: Your GitHub App slug (for comment mentions, corresponds to `settings.app_slug`)
- `GITHUB_APP_WEBHOOK_SECRET`: Webhook Secret (for GitHub signature verification)
- `GITHUB_APP_ID`: GitHub App ID
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`: For OAuth (can support installation/authorization flow)
- `GITHUB_PRIVATE_KEY_PATH`: GitHub App private key path (PEM, default `./configs/app.pem`)
- (Optional) `CONTEXT7_API_KEY`: API Key required for Claude Code MCP plugin example

Place the private key at `./configs/app.pem` and ensure it's not exposed.

## 🧭 Webhook & Permission Setup (GitHub)

1. Create GitHub App (recommended to install to target organization/personal account)

    - Webhook URL: `https://<your-host>/github/webhook`
    - Webhook Secret: Create a custom secret and fill in environment variables
    - Event subscriptions: At least `Issue comment`
    - Permissions: Contents(R/W), Pull requests(R/W), Issues(R), Metadata(R)

2. Download private key (PEM) and place at `GITHUB_PRIVATE_KEY_PATH`

3. Install App to target Repository or Organization

4. Advanced (Optional)

    - OAuth callback: `GET /github/auth?code=<code>&state=<state>` (demo flow)
    - Get Installation Token: `GET /github/token/{installation_id}` (demo usage)

## 🧩 API Overview

- `GET /`: Health check (returns message)
- `POST /github/webhook`: GitHub Webhook entry point
- `POST /gitea/webhook`: Gitea Webhook entry point
- `GET /github/auth`: GitHub OAuth callback demo
- `GET /github/token/{installation_id}`: Exchange Installation Token demo

## 📁 Project Structure (Excerpt)

```
src/codex_agent/
  app/api.py                 # FastAPI app and route mounting
  app/v1/github.py           # GitHub Webhook + auth/token examples
  app/v1/gitea.py            # Gitea Webhook
  utils/claude_code.py       # Claude Code execution and workspace preparation
  utils/settings.py          # Read GitHub App settings
  utils/gen_jwt.py           # Generate GitHub App JWT
  types/                     # Webhook/Headers Pydantic types
prompts/                     # System prompts and task templates
```

Default workspace directory: `./workspaces/<repo_name>` (automatically `git clone` on first trigger).

## 📌 Current Progress & Roadmap

### ✅ Completed (Available Features)

- **Webhook Reception & Parsing**: GitHub/Gitea `issue_comment` event reception and basic verification
- **Mention Detection**: Detect `@{settings.app_slug}` tags in comments
- **Workspace Management**: Auto `git clone` to `./workspaces/<repo_name>`
- **Claude Code Integration**: System prompt loading, task template injection, workspace execution
- **Basic Settings Management**: Load environment variables via `Settings` class
- **GitHub App Authentication**: JWT generation, Installation Token acquisition, OAuth flow

### 🚧 In Progress (Partially Implemented)

- **Task Execution Flow**: Claude Code triggered but not actually executed (`claude.task` currently just prints)
- **Branch Management**: Workspace clone completed, but branch creation and switching logic pending
- **Error Handling**: Basic webhook verification, but detailed error feedback mechanisms need strengthening

### 📋 To Be Completed (Design Finalized, Will Be Gradually Implemented)

- **Auto PR Creation/Update**: Automatically create PR or update existing PR after task completion
- **PR Continuation Support**: Detect continuation tasks, switch to correct branch to continue work
- **Webhook Signature Verification**: Complete GitHub/Gitea webhook security verification
- **Commit Message Generation**: Auto-analyze change content and generate semantic commit messages
- **PR Description Generation**: Implement `generate commit message` functionality
- **Testing & Formatting Integration**: Auto-execute project's lint/test commands
- **Multi AI Model Support**: Support other AI programming assistants beyond Claude Code
- **Audit & Logging**: Complete operation records and permission management

## 🤝 Contributing

- Welcome Issues/PRs
- Follow coding style (ruff, type hints) and semantic commits
- PR titles should follow Conventional Commits

## 📄 License

MIT — see `LICENSE`.
