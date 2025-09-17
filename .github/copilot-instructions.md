# CodexAgent Developer Instructions

This document provides detailed technical information about CodexAgent for developers contributing to the project.

## Architecture Overview

CodexAgent is built with:
- **FastAPI**: Web framework for webhook endpoints
- **Pydantic**: Data validation and settings management
- **Claude Code SDK**: AI code generation and modification
- **asyncio/httpx**: Async HTTP operations
- **Rich**: Terminal output and logging

## Key Components

### 1. Webhook Handlers (`src/codex_agent/app/v1/`)

#### GitHub Handler (`github.py`)
- **Route**: `POST /github/webhook`
- **Event**: `issue_comment`
- **Validation**: Uses `GitHubWebhookHeaders` and `GithubWebhookPayload` Pydantic models
- **Mention Detection**: Checks for `@{settings.app_slug}` in comment body (case-insensitive)
- **Action Filter**: Only processes `created` events with valid comments

#### Gitea Handler (`gitea.py`)  
- **Route**: `POST /gitea/webhook`
- **Event**: Issue/PR comments (equivalent to GitHub's `issue_comment`)
- **Validation**: Uses `GiteaWebhookHeaders` and `GiteaWebhookPayload` Pydantic models
- **Similar processing logic to GitHub handler

### 2. Claude Code Integration (`src/codex_agent/utils/claude_code.py`)

#### `ClaudeCodeHandler` Class
- **Purpose**: Manages AI-powered code modification tasks
- **Key Features**:
  - Auto-workspace setup in `./workspaces/<repo_name>`
  - System prompt injection from `./prompts/`
  - Git repository cloning on first trigger
  - Claude Code SDK integration with MCP servers

#### Workspace Management
- **Location**: `./workspaces/<repo_name>/`
- **Clone Logic**: Extracts repo name from `clone_url`, performs `git clone` if workspace doesn't exist
- **Branch Strategy**: Creates branches named `codex-agent/<short-uuid>` for new tasks

#### System Prompts
- **System Prompt**: `./prompts/system_prompt.md` - Core AI behavior instructions
- **System Info**: `./prompts/system_info.md` - Dynamic system information (OS, date, shell, workspace path)
- **Task Template**: `./prompts/template.md` - Task formatting template

### 3. GitHub App Authentication (`src/codex_agent/utils/`)

#### Settings Management (`settings.py`)
- **Environment Variables**:
  - `GITHUB_APP_SLUG`: App mention slug
  - `GITHUB_APP_WEBHOOK_SECRET`: Webhook signature verification
  - `GITHUB_APP_ID`: GitHub App ID
  - `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`: OAuth credentials
  - `GITHUB_PRIVATE_KEY_PATH`: Path to PEM private key (default: `./configs/app.pem`)

#### JWT Generation (`gen_jwt.py`)
- **Purpose**: Generate GitHub App JWT tokens for API authentication
- **Algorithm**: RS256 with 10-minute expiration
- **Usage**: Required for GitHub API calls and installation token exchange

### 4. Type Definitions (`src/codex_agent/types/`)

#### Webhook Payloads
- **GitHub**: `GithubWebhookPayload` - Complete GitHub webhook event structure
- **Gitea**: `GiteaWebhookPayload` - Gitea webhook event structure
- **Headers**: Webhook header validation models

## Core Workflows

### 1. New Task Flow
1. **Webhook Reception**: FastAPI receives `issue_comment` event
2. **Validation**: Verify webhook headers and parse payload
3. **Mention Check**: Detect `@{app_slug}` in comment body
4. **Workspace Setup**: Clone repository to `./workspaces/<repo_name>`
5. **Branch Creation**: Create new branch `codex-agent/<uuid>`
6. **AI Processing**: Execute Claude Code with system prompts and task
7. **PR Creation**: Commit changes and create pull request

### 2. Continuation Task Flow (Planned)
1. **Context Detection**: Identify existing PR and branch
2. **Branch Checkout**: Switch to existing PR branch
3. **AI Processing**: Continue work on same branch
4. **Update PR**: Push new commits to existing branch

### 3. Generate Commit Message Flow (Planned)
1. **Diff Analysis**: Analyze all changes in PR
2. **Content Generation**: Generate semantic commit message and PR description
3. **PR Update**: Update PR title and description

## Implementation Status

### ✅ Completed Features
- FastAPI webhook endpoints (GitHub/Gitea)
- Webhook payload validation with Pydantic
- Mention detection (`@{app_slug}`)
- Basic workspace management and git cloning
- Claude Code SDK integration framework
- System prompt injection system
- GitHub App JWT generation
- OAuth callback endpoints (demo)

### 🚧 In Progress / Planned
- **Webhook Signature Verification**: GitHub HMAC-SHA256 and Gitea secret validation
- **GitHub API Integration**: PR creation, branch management, commit operations
- **Error Handling**: Robust error recovery and user feedback
- **Branch Management**: Smart branch naming, conflict resolution
- **PR Lifecycle**: Creation, updates, status reporting
- **Multi-model Support**: OpenAI Codex integration alongside Claude Code
- **Audit Logging**: Comprehensive operation logging and security audit trails

## Development Setup

### Prerequisites
- Python 3.10+
- `uv` package manager
- GitHub App configured with appropriate permissions

### Local Development
```bash
# Install dependencies
make uv-install
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your GitHub App credentials

# Run development server
uv run codex_agent
```

### Environment Configuration
Create `.env` file with:
```bash
GITHUB_APP_SLUG=your-app-slug
GITHUB_APP_WEBHOOK_SECRET=your-webhook-secret
GITHUB_APP_ID=your-app-id
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
GITHUB_PRIVATE_KEY_PATH=./configs/app.pem
```

Place your GitHub App private key at `./configs/app.pem`.

## Testing Strategy

### Webhook Testing
- Use tools like ngrok for local webhook testing
- Test with both GitHub and Gitea webhook formats
- Verify mention detection logic

### Integration Testing
- Test full workflow: webhook → AI processing → PR creation
- Verify workspace isolation between different repositories
- Test error scenarios and recovery

## Security Considerations

### Webhook Security
- **Signature Verification**: Validate incoming webhooks with HMAC signatures
- **Event Filtering**: Only process expected event types (`issue_comment`)
- **Input Sanitization**: Validate all user inputs through Pydantic models

### GitHub App Security
- **Minimal Permissions**: Request only necessary GitHub App permissions
- **Private Key Storage**: Secure storage of GitHub App private key
- **Token Rotation**: Use short-lived installation tokens

### Workspace Security
- **Isolation**: Each repository gets isolated workspace
- **Cleanup**: Implement workspace cleanup policies
- **Resource Limits**: Prevent workspace size/time abuse

## API Endpoints

### Core Endpoints
- `GET /`: Health check
- `POST /github/webhook`: GitHub webhook handler
- `POST /gitea/webhook`: Gitea webhook handler

### Demo/Auth Endpoints
- `GET /github/auth`: OAuth callback demonstration
- `GET /github/token/{installation_id}`: Installation token exchange demo

## Contributing Guidelines

### Code Style
- Follow existing code patterns
- Use type hints throughout
- Validate inputs with Pydantic models
- Handle errors gracefully with proper HTTP status codes

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation as needed
4. Ensure all CI checks pass
5. Request review from maintainers

### Testing Requirements
- Unit tests for core logic
- Integration tests for webhook flows
- Mock external dependencies (GitHub API, Claude Code)
- Test error scenarios and edge cases