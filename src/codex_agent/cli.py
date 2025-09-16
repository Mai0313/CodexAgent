from pathlib import Path

from fastapi import FastAPI, Request
from rich.console import Console

from codex_agent.types.gitea import GiteaWebhookPayload
from codex_agent.types.headers import WebhookHeaders

app = FastAPI()
console = Console()


@app.post("/webhook")
async def handle_webhook(request: Request) -> dict[str, str]:
    headers = WebhookHeaders(**dict(request.headers))
    if "Go" not in headers.user_agent:
        return {"status": "ignored"}

    body_dict = await request.json()
    payload = GiteaWebhookPayload(**body_dict)
    # payload.save("./logs/webhook_payload.json")
    if payload.action is None:
        return {"status": "no action"}
    if payload.comment and "@agent" in payload.comment.body:
        prompt = Path("./prompts/template.md").read_text()
        prompt = prompt.replace("<user_id>", payload.comment.user.login)
        prompt = prompt.replace("<task>", payload.comment.body)
        prompt = prompt.replace("<clone_url>", payload.repository.clone_url)
        console.print(prompt)
    return {"status": "received"}
