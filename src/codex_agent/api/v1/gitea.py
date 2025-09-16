from pathlib import Path

from fastapi import Request, APIRouter
from rich.console import Console

from codex_agent.types.gitea import GiteaWebhookPayload
from codex_agent.types.headers import GiteaWebhookHeaders
from codex_agent.utils.settings import Settings

router = APIRouter()

console = Console()
settings = Settings()


@router.post("/webhook")
async def handle_gitea_webhook(request: Request) -> dict[str, str]:
    GiteaWebhookHeaders(**dict(request.headers))
    body_dict = await request.json()

    payload = GiteaWebhookPayload(**body_dict)
    payload.save("./logs/gitea_payload.json")
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
