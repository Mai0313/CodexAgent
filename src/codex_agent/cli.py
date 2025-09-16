from fastapi import FastAPI, Request
from rich.console import Console

from codex_agent.types.gitea import GiteaWebhookPayload
from codex_agent.types.headers import WebhookHeaders

app = FastAPI()
console = Console()

prompt_template = """
You are an AI coding Assistant, your job is helping {user_id} to finish his job, here is the task:
{task}
Here is the repository URL: {clone_url}
You can use MCP tools to help you complete the task.
"""


@app.post("/webhook")
async def handle_webhook(request: Request) -> dict[str, str]:
    headers = WebhookHeaders(**dict(request.headers))
    if "Go" not in headers.user_agent:
        return {"status": "ignored"}

    body_dict = await request.json()
    payload = GiteaWebhookPayload(**body_dict)
    payload.save("./logs/webhook_payload.json")
    if payload.action is None:
        return {"status": "no action"}
    if payload.comment and "@agent" in payload.comment.body:
        user_id = payload.comment.user.login
        task = payload.comment.body
        clone_url = payload.repository.clone_url
        prompt = prompt_template.format(user_id=user_id, task=task, clone_url=clone_url)
        console.print(prompt)
    return {"status": "received"}
