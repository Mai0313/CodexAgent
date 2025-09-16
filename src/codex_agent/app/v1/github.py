from pathlib import Path

import httpx
from fastapi import Request, APIRouter, HTTPException
from rich.console import Console

from codex_agent.types.github import GithubWebhookPayload
from codex_agent.types.headers import GitHubWebhookHeaders
from codex_agent.utils.gen_jwt import JWTHandler
from codex_agent.utils.settings import Settings

router = APIRouter()

console = Console()
settings = Settings()


@router.post("/webhook")
async def handle_github_webhook(request: Request) -> dict[str, str]:
    GitHubWebhookHeaders(**dict(request.headers))
    body_dict = await request.json()

    payload = GithubWebhookPayload(**body_dict)
    payload.save("./logs/github_payload.json")
    console.print(payload)
    if payload.action != "created" or not payload.comment or not payload.comment.body:
        return {"status": "ignored"}
    if f"@{settings.app_slug}" not in payload.comment.body.lower():
        return {"status": "ignored"}
    if payload.comment and payload.comment.user:
        prompt = Path("./prompts/template.md").read_text()
        prompt = prompt.format(task=payload.comment.body, clone_url=payload.repository.clone_url)
        console.print(prompt)
    return {"status": "received"}


@router.get("/auth")
async def github_auth_callback(code: str, state: str) -> dict[str, str]:
    console.print("✅ OAuth callback received!")
    console.print(f"code={code}, state={state}")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.client_id,
                "client_secret": settings.client_secret,
                "code": code,
                "state": state,
            },
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    token_data = resp.json()
    console.print("🔑 User Access Token:", token_data)
    return {"message": "OAuth callback received", "token": token_data}


@router.get("/token/{installation_id}")
async def get_installation_token(installation_id: int) -> dict[str, str]:
    jwt_token = await JWTHandler.generate_jwt(app_id=settings.app_id, key=settings.private_key)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json",
            },
        )
    if resp.status_code != 201:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    token_data = resp.json()
    console.print("✅ Installation Access Token:", token_data)
    return token_data
