from typing import TYPE_CHECKING
from pathlib import Path
from functools import cached_property

from fastapi import FastAPI, Request
from pydantic import BaseModel, computed_field
from rich.console import Console
from claude_code_sdk import ClaudeCodeOptions, query

from codex_agent.types.gitea import GiteaWebhookPayload
from codex_agent.types.headers import WebhookHeaders

if TYPE_CHECKING:
    from claude_code_sdk.types import McpServerConfig


class ClaudeCodeHandler(BaseModel):
    @computed_field
    @cached_property
    def system_prompt(self) -> str:
        prompt_path = Path("./prompts/default.md")
        return prompt_path.read_text()

    async def run(self, prompt: str) -> None:
        mcp_servers: dict[str, McpServerConfig] = {
            "context7": {
                "type": "http",
                "url": "https://mcp.context7.com/mcp",
                "headers": {"CONTEXT7_API_KEY": "YOUR_API_KEY"},
            }
        }
        options = ClaudeCodeOptions(
            allowed_tools=["*"],
            system_prompt=self.system_prompt,
            mcp_servers=mcp_servers,
            permission_mode="bypassPermissions",
            max_turns=1,
        )

        async for message in query(prompt=prompt, options=options):
            console.print(message)


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
