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
    if payload.action is None:
        return {"status": "ignored"}
    if f"@{settings.app_slug}" not in payload.comment.body.lower():
        return {"status": "ignored"}
    if payload.action == "created" and payload.comment and payload.comment.user:
        console.print(payload)
        prompt = Path("./prompts/template.md").read_text()
        prompt = prompt.format(task=payload.comment.body, clone_url=payload.repository.clone_url)
    return {"status": "received"}
