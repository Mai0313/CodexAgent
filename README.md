<center>

# CodexAgent — GitHub/Gitea AI Code Collaboration Agent

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

Just mention it once, and AI will automatically modify code, commit, and create PRs on GitHub/Gitea. CodexAgent listens for `@{GITHUB_APP_SLUG}` mentions in Issues/PR comments, delegates tasks to Claude Code / OpenAI Codex, and supports continuous iteration in PR discussions.

[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## ✨ Core Features (GitHub / Gitea Support)

- **Mention Trigger**: Simply `@{GITHUB_APP_SLUG} <task>` in Issue or PR comments to trigger
- **Automated Development Workflow**: clone, create/switch branch, AI code modification, testing, commit, create/update PR
- **Continuous PR Work**: Mention `@{GITHUB_APP_SLUG}` again in the same PR for continuous modifications, results pushed to the same branch
- **Generate PR Content**: Use `@{GITHUB_APP_SLUG} generate commit message` in PR text to analyze changes and update PR content
- **Security & Audit**: Validated with GitHub App permissions and Webhook Secret verification; all changes reviewable via branch/PR format

> Note: The following describes the complete feature design. For current implementation status, see "Current Progress & Roadmap" at the end.

## 🧠 How It Works

When users mention `@{GITHUB_APP_SLUG}` in Issue or PR comments in target repos, CodexAgent executes the following workflow:

1. **Event Reception**
   - Receive GitHub/Gitea `issue_comment` events via FastAPI Webhook
   - Verify signatures (GitHub `X-Hub-Signature-256` / Gitea Secret) and event types

2. **Context Parsing** 
   - Extract repository URL, Issue/PR info, comment author and content
   - Determine if it's a "new task" or "continuation of existing PR task"

3. **Workspace Preparation**
   - For new tasks: `git clone <repo>` to `./workspaces/<repo_name>`, create branch `codex-agent/<short-uuid>`
   - For continuations: switch to PR's corresponding branch (`head`), update to latest

4. **AI Code Modification (Claude Code / OpenAI Codex)**
   - Inject system prompts and task templates (`./prompts/*.md`), provide complete working directory
   - Execute in tool mode (allows shell/git/fs operations), complete development work in workspace
   - Prioritize minimal necessary changes to achieve goals, attempt formatting/testing (if available)

5. **Commit & Create/Update PR**
   - Generate semantic commit messages, push to remote branch
   - New tasks: create PR against default branch, attach summary and impact in PR description
   - Continuations: push new commits to same branch, report progress in PR comments

6. **User Iteration**
   - Mention `@{GITHUB_APP_SLUG} <new command>` again in PR discussions for continuous modification of same PR
   - Use `@{GITHUB_APP_SLUG} generate commit message` to rewrite PR original content (description/checklist)

## 💬 Interaction Guide (Comment Syntax)

- **New Tasks (Issue or PR)**
  - `@{GITHUB_APP_SLUG} Fix failing test cases in tests/test_*.py`
  - `@{GITHUB_APP_SLUG} Implement installation section and examples in README`

- **Continuations (Comment again in existing PR)**
  - `@{GITHUB_APP_SLUG} Adjust change scope, only modify abc/ and tests/`
  - `@{GITHUB_APP_SLUG} Add type annotations and fix mypy reports`

- **Generate PR Content**
  - `@{GITHUB_APP_SLUG} generate commit message`
  - Will generate organized descriptions, impact scope, testing suggestions based on file differences, and update PR description

## 🔗 Supported Events & Platforms

- **GitHub**
  - Events: `issue_comment` (PR conversations also belong to this event)
  - Permissions (minimum recommended): Contents: Read/Write, Pull requests: Read/Write, Issues: Read, Metadata: Read
  - Webhook: `POST https://<your-host>/github/webhook`

- **Gitea**
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

Set up publicly accessible callback URL (like ngrok/Cloudflare Tunnel), configure `https://<your-host>/github/webhook` or `.../gitea/webhook` as Webhook target.

## 🔑 Environment Variables

Place the following variables in `.env` or your deployment platform's environment configuration:

- `GITHUB_APP_SLUG`: Your GitHub App slug (for comment mentions)
- `GITHUB_APP_WEBHOOK_SECRET`: Webhook Secret (for GitHub signature verification)
- `GITHUB_APP_ID`: GitHub App ID
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`: OAuth use (can support installation/authorization flow)
- `GITHUB_PRIVATE_KEY_PATH`: GitHub App private key path (PEM, default `./configs/app.pem`)
- (Optional) `CONTEXT7_API_KEY`: API Key required for Claude Code MCP plugin example

Place private key at `./configs/app.pem` and ensure it's not exposed.

## 🧭 Webhook & Permission Setup (GitHub)

1. **Create GitHub App** (recommended to install to target organization/personal)
   - Webhook URL: `https://<your-host>/github/webhook`
   - Webhook Secret: Custom set and fill into environment variables
   - Event subscriptions: At least `Issue comment`
   - Permissions: Contents(R/W), Pull requests(R/W), Issues(R), Metadata(R)

2. **Download private key (PEM)** and place at `GITHUB_PRIVATE_KEY_PATH`

3. **Install App** to target Repository or Organization

4. **Advanced (Optional)**
   - OAuth callback: `GET /github/auth?code=<code>&state=<state>` (demo flow)
   - Get Installation Token: `GET /github/token/{installation_id}` (demo purposes)

## 🧩 API Overview

- `GET /`: Health check (returns message)
- `POST /github/webhook`: GitHub Webhook entry point
- `POST /gitea/webhook`: Gitea Webhook entry point
- `GET /github/auth`: GitHub OAuth callback demo
- `GET /github/token/{installation_id}`: Exchange Installation Token demo

## 📁 Project Structure (Selected)

```
src/codex_agent/
  app/api.py                 # FastAPI app and route mounting
  app/v1/github.py           # GitHub Webhook + auth/Token examples
  app/v1/gitea.py            # Gitea Webhook
  utils/claude_code.py       # Claude Code execution and workspace preparation
  utils/settings.py          # Read GitHub App settings
  utils/gen_jwt.py           # Generate GitHub App JWT
  types/                     # Webhook/Headers Pydantic types
prompts/                     # System prompts and task templates
```

Working directory default: `./workspaces/<repo_name>` (first trigger will automatically `git clone`).

## 📌 Current Progress & Roadmap

**Completed (Available):**

- GitHub/Gitea Webhook entry points and event parsing (`issue_comment`)
- Mention detection: `@{GITHUB_APP_SLUG}`
- Workspace creation and repo clone (`./workspaces/<repo>`)
- Claude Code execution framework (system prompt/template injection, tool mode, working directory)
- GitHub OAuth/Installation Token example endpoints

**To be Enhanced (Design finalized, will be gradually completed):**

- GitHub/Gitea signature verification and enhanced error handling
- Automatic PR creation/update, branch naming strategy and protection rule integration
- Complete "continuation" workflow in PR (checkout, conflict handling, status replies)
- Automatic commit message/PR description generation and overwriting
- Built-in testing/formatting auto-execution and reporting
- Multi-model provider selection (Claude Code / OpenAI Codex etc.) and key management
- More comprehensive permission/audit logging

## 🤝 Contributing

- Welcome to submit Issue/PR
- Please follow coding style (ruff, types) and semantic commits
- Recommended PR titles adopt Conventional Commits

## 📄 License

MIT — see `LICENSE`.
