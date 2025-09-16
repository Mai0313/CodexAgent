from pathlib import Path

from fastapi import FastAPI, Request
from rich.console import Console

from codex_agent.types.gitea import GiteaWebhookPayload
from codex_agent.types.github import GithubWebhookPayload
from codex_agent.utils.verify import Verification
from codex_agent.types.headers import GiteaWebhookHeaders, GitHubWebhookHeaders
from codex_agent.utils.settings import Settings

app = FastAPI()
console = Console()
settings = Settings()


@app.post("/gitea/webhook")
async def handle_gitea_webhook(request: Request) -> dict[str, str]:
    GiteaWebhookHeaders(**dict(request.headers))
    body_dict = await request.json()

    payload = GiteaWebhookPayload(**body_dict)
    # payload.save("./logs/webhook_payload.json")
    if payload.action is None:
        return {"status": "ignored"}
    if f"@{settings.app_slug}" not in payload.comment.body.lower():
        return {"status": "ignored"}
    if payload.comment and payload.comment.user:
        prompt = Path("./prompts/template.md").read_text()
        prompt = prompt.replace("<user_id>", payload.comment.user.login)
        prompt = prompt.replace("<task>", payload.comment.body)
        prompt = prompt.replace("<clone_url>", payload.repository.clone_url)
        console.print(prompt)
    return {"status": "received"}


@app.post("/webhook")
async def handle_github_webhook(request: Request) -> dict[str, str]:
    headers = GitHubWebhookHeaders(**dict(request.headers))
    body_dict = await request.body()

    Verification.verify_github(headers.hub_signature_256, body_dict)

    payload = GithubWebhookPayload(**body_dict)
    # payload.save("./logs/webhook_payload.json")
    if payload.action != "created" or not payload.comment or not payload.comment.body:
        return {"status": "ignored"}
    if f"@{settings.app_slug}" not in payload.comment.body.lower():
        return {"status": "ignored"}
    if payload.comment and payload.comment.user:
        prompt = Path("./prompts/template.md").read_text()
        prompt = prompt.replace("<user_id>", payload.comment.user.login)
        prompt = prompt.replace("<task>", payload.comment.body)
        prompt = prompt.replace("<clone_url>", payload.repository.clone_url)
        console.print(prompt)
    return {"status": "received"}
